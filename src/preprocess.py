from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader

DATA_DIR = Path(__file__).parent.parent / "data"
OUTPUT_DIR = Path(__file__).parent.parent / "output"

PDF_PATH = DATA_DIR / "2026-rules-of-tennis-english.pdf"
OUTPUT_PATH = OUTPUT_DIR / "full_text.txt"


def load_and_merge() -> str:
    loader = PyPDFLoader(str(PDF_PATH))
    pages = loader.load()
    return "\n".join(page.page_content for page in pages)


def main() -> None:
    if not PDF_PATH.exists():
        raise FileNotFoundError(f"PDF를 찾을 수 없습니다: {PDF_PATH}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    full_text = load_and_merge()
    OUTPUT_PATH.write_text(full_text, encoding="utf-8")

    print(f"총 {len(full_text):,}자 추출 완료 → {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
