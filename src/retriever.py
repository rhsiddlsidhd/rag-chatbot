from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings

load_dotenv()

FAISS_DIR = Path(__file__).parent.parent / "output" / "faiss"
DEFAULT_K = 5


@dataclass
class RetrievedChunk:
    chunk_id: str
    title: str
    chunk_type: str
    text: str
    score: float


def load_vectorstore() -> FAISS:
    if not FAISS_DIR.exists():
        raise FileNotFoundError(
            f"FAISS 인덱스를 찾을 수 없습니다: {FAISS_DIR}\n"
            "먼저 embedder.py를 실행하세요."
        )
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    return FAISS.load_local(
        str(FAISS_DIR),
        embeddings,
        allow_dangerous_deserialization=True,
    )


def retrieve(query: str, k: int = DEFAULT_K) -> list[RetrievedChunk]:
    vectorstore = load_vectorstore()
    results = vectorstore.similarity_search_with_score(query, k=k)
    return [
        RetrievedChunk(
            chunk_id=doc.metadata["chunk_id"],
            title=doc.metadata["title"],
            chunk_type=doc.metadata["type"],
            text=doc.page_content,
            score=float(score),
        )
        for doc, score in results
    ]


def main() -> None:
    query = "How many points are needed to win a game?"
    print(f"Query: {query}\n")

    chunks = retrieve(query)
    for i, chunk in enumerate(chunks, 1):
        print(f"[{i}] {chunk.title} ({chunk.chunk_id}) — score: {chunk.score:.4f}")
        print(f"    {chunk.text[:120].strip()}...")
        print()


if __name__ == "__main__":
    main()
