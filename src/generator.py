from dataclasses import dataclass

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from retriever import retrieve, RetrievedChunk

load_dotenv()

SYSTEM_PROMPT = """You are an expert on the ITF Rules of Tennis.
Answer the user's question using only the provided context.
If the answer is not in the context, say you don't know.
Be concise and precise."""


@dataclass
class GenerationResult:
    query: str
    answer: str
    sources: list[RetrievedChunk]


def build_context(chunks: list[RetrievedChunk]) -> str:
    return "\n\n---\n\n".join(
        f"[{c.title}]\n{c.text}" for c in chunks
    )


def generate(query: str, k: int = 5) -> GenerationResult:
    chunks = retrieve(query, k=k)
    context = build_context(chunks)

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=f"Context:\n{context}\n\nQuestion: {query}"),
    ]

    response = llm.invoke(messages)
    return GenerationResult(
        query=query,
        answer=str(response.content),
        sources=chunks,
    )


def main() -> None:
    query = "How many points are needed to win a game?"
    print(f"Q: {query}\n")

    result = generate(query)
    print(f"A: {result.answer}\n")

    print("Sources:")
    for chunk in result.sources:
        print(f"  - {chunk.title} ({chunk.chunk_id})")


if __name__ == "__main__":
    main()
