import json
from pathlib import Path

from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings

load_dotenv()

CHUNKS_PATH = Path(__file__).parent.parent / "output" / "chunks.json"
FAISS_DIR = Path(__file__).parent.parent / "output" / "faiss"


def load_chunks() -> list[dict]:
    if not CHUNKS_PATH.exists():
        raise FileNotFoundError(f"청크 파일을 찾을 수 없습니다: {CHUNKS_PATH}")
    return json.loads(CHUNKS_PATH.read_text(encoding="utf-8"))


def to_documents(chunks: list[dict]) -> list[Document]:
    docs: list[Document] = []
    for chunk in chunks:
        metadata: dict[str, str | int] = {
            "chunk_id": chunk["chunk_id"],
            "title": chunk["title"],
            "type": chunk["type"],
        }
        if chunk["rule_number"] is not None:
            metadata["rule_number"] = chunk["rule_number"]

        docs.append(Document(page_content=chunk["text"], metadata=metadata))
    return docs


def main() -> None:
    chunks = load_chunks()
    documents = to_documents(chunks)

    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

    vectorstore = FAISS.from_documents(documents, embeddings)

    FAISS_DIR.mkdir(parents=True, exist_ok=True)
    vectorstore.save_local(str(FAISS_DIR))

    print(f"총 {len(documents)}개 청크 임베딩 완료 → {FAISS_DIR}")


if __name__ == "__main__":
    main()
