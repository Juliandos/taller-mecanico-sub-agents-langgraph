"""Módulo RAG: conecta al pgvector y expone get_retriever()"""

import os
from functools import lru_cache

from langchain_openai import OpenAIEmbeddings
from langchain_postgres import PGVector

DB_URI = os.environ.get("DB_URI", "postgresql://postgres:postgres@localhost:5432/taller_mecanico")
COLLECTION_NAME = "mecanica_docs"


@lru_cache(maxsize=1)
def get_vectorstore() -> PGVector:
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    return PGVector(
        embeddings=embeddings,
        collection_name=COLLECTION_NAME,
        connection=DB_URI,
    )


def get_retriever(k: int = 3):
    return get_vectorstore().as_retriever(search_kwargs={"k": k})