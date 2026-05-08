"""
Carga documentos técnicos de docs/mecanica/ en pgvector.
Soporta archivos .pdf y .txt.
Ejecución única (o cuando agregas nuevos documentos):
    uv run python scripts/load_docs.py
"""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_postgres import PGVector
from langchain_core.documents import Document
import pypdf

DB_URI = os.environ.get("DB_URI", "postgresql://postgres:postgres@localhost:5432/taller_mecanico")
DOCS_DIR = Path(__file__).parent.parent / "docs" / "mecanica"
COLLECTION_NAME = "mecanica_docs"


def leer_pdf(archivo: Path) -> str:
    reader = pypdf.PdfReader(str(archivo))
    texto = ""
    for page in reader.pages:
        texto += page.extract_text() or ""
    return texto.strip()


def cargar_documentos() -> list[Document]:
    docs = []

    archivos = [
        f for f in DOCS_DIR.iterdir()
        if f.suffix.lower() in (".pdf", ".txt") and f.name != "README.txt"
    ]

    if not archivos:
        print(f"No se encontraron archivos PDF o TXT en {DOCS_DIR}")
        print("Agrega tus documentos en docs/mecanica/ y vuelve a ejecutar.")
        sys.exit(0)

    for archivo in sorted(archivos):
        try:
            if archivo.suffix.lower() == ".pdf":
                contenido = leer_pdf(archivo)
            else:
                contenido = archivo.read_text(encoding="utf-8")

            if not contenido:
                print(f"  Saltado (vacío): {archivo.name}")
                continue

            doc = Document(
                page_content=contenido,
                metadata={"source": archivo.name, "tema": archivo.stem},
            )
            docs.append(doc)
            print(f"  Cargado: {archivo.name} ({len(contenido):,} chars)")

        except Exception as e:
            print(f"  Error leyendo {archivo.name}: {e}")

    return docs


def main():
    print(f"Conectando a: {DB_URI}")
    print(f"Leyendo documentos de: {DOCS_DIR}\n")

    docs_raw = cargar_documentos()
    print(f"\n{len(docs_raw)} documentos leídos.")

    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
    chunks = splitter.split_documents(docs_raw)
    print(f"Total chunks a indexar: {len(chunks)}")

    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

    print("Indexando en pgvector (esto puede tardar unos segundos)...")
    PGVector.from_documents(
        documents=chunks,
        embedding=embeddings,
        collection_name=COLLECTION_NAME,
        connection=DB_URI,
        pre_delete_collection=True,
    )

    print(f"\n✅ {len(chunks)} chunks cargados en la colección '{COLLECTION_NAME}'")


if __name__ == "__main__":
    main()