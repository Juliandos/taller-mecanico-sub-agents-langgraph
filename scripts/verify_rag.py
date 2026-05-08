"""
Verifica que los documentos están indexados en pgvector.
    uv run python scripts/verify_rag.py
"""

import os
from dotenv import load_dotenv
load_dotenv()

from langchain_openai import OpenAIEmbeddings
from langchain_postgres import PGVector

DB_URI = os.environ.get("DB_URI", "postgresql://postgres:postgres@localhost:5432/taller_mecanico")
COLLECTION_NAME = "mecanica_docs"

QUERIES_TEST = [
    "motor vibra al frenar",
    "cambio de aceite",
    "ruido en la suspensión",
]


def main():
    print(f"Conectando a: {DB_URI}\n")

    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    vectorstore = PGVector(
        embeddings=embeddings,
        collection_name=COLLECTION_NAME,
        connection=DB_URI,
    )

    for query in QUERIES_TEST:
        print(f"{'='*60}")
        print(f"QUERY: '{query}'")
        print(f"{'='*60}")

        docs = vectorstore.similarity_search(query, k=2)

        if not docs:
            print("  ⚠️  Sin resultados — la colección puede estar vacía.\n")
            continue

        for i, doc in enumerate(docs, 1):
            fuente = doc.metadata.get("source", "desconocido")
            preview = doc.page_content[:200].replace("\n", " ")
            print(f"  [{i}] Fuente: {fuente}")
            print(f"      Preview: {preview}...")
            print()

    print("✅ Verificación completa.")


if __name__ == "__main__":
    main()