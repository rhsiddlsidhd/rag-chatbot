from dataclasses import dataclass
import json
import re
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
OUTPUT_DIR = Path(__file__).parent.parent / "output"
BODY_PATH = DATA_DIR / "itf-rules-body.txt"

RULE_RE = re.compile(r"^(\d+)\.\s{2,}([A-Z][A-Z ]+)\s*$")
APPENDIX_RE = re.compile(r"^\s*APPENDIX\s+([IVX]+)\s*$")
WHEELCHAIR_RE = re.compile(r"^\s*RULES OF WHEELCHAIR TENNIS\s*$")
AMENDMENT_RE = re.compile(r"^\s*AMENDMENT TO THE RULES OF TENNIS\s*$")

ROMAN: dict[str, int] = {
    "I": 1, "II": 2, "III": 3, "IV": 4, "V": 5, "VI": 6,
    "VII": 7, "VIII": 8, "IX": 9, "X": 10, "XI": 11, "XII": 12,
}


@dataclass
class Boundary:
    line_idx: int
    chunk_id: str
    title: str
    chunk_type: str
    rule_number: int | None


def detect_boundaries(lines: list[str]) -> list[Boundary]:
    boundaries: list[Boundary] = []
    rules_closed = False  # Wheelchair/Appendix 진입 후 Rule 탐지 중단

    for i, line in enumerate(lines):
        if not rules_closed:
            m = RULE_RE.match(line)
            if m:
                num = int(m.group(1))
                if 1 <= num <= 31:
                    boundaries.append(Boundary(
                        line_idx=i,
                        chunk_id=f"rule_{num:02d}",
                        title=m.group(2).strip(),
                        chunk_type="rule",
                        rule_number=num,
                    ))
                continue

        m = APPENDIX_RE.match(line)
        if m:
            rules_closed = True
            roman = m.group(1)
            boundaries.append(Boundary(
                line_idx=i,
                chunk_id=f"appendix_{roman}",
                title=f"Appendix {roman}",
                chunk_type="appendix",
                rule_number=ROMAN.get(roman),
            ))
            continue

        if WHEELCHAIR_RE.match(line):
            rules_closed = True
            boundaries.append(Boundary(
                line_idx=i,
                chunk_id="wheelchair",
                title="Rules of Wheelchair Tennis",
                chunk_type="wheelchair",
                rule_number=None,
            ))
            continue

        if AMENDMENT_RE.match(line):
            boundaries.append(Boundary(
                line_idx=i,
                chunk_id="amendment",
                title="Amendment to the Rules of Tennis",
                chunk_type="amendment",
                rule_number=None,
            ))

    return boundaries


def build_chunks(lines: list[str], boundaries: list[Boundary]) -> list[dict]:
    chunks: list[dict] = []
    for i, meta in enumerate(boundaries):
        start = meta.line_idx
        end = boundaries[i + 1].line_idx if i + 1 < len(boundaries) else len(lines)
        text = "\n".join(lines[start:end]).strip()
        chunks.append({
            "chunk_id": meta.chunk_id,
            "title": meta.title,
            "type": meta.chunk_type,
            "rule_number": meta.rule_number,
            "text": text,
        })
    return chunks


def main() -> None:
    lines = BODY_PATH.read_text(encoding="utf-8").splitlines()
    boundaries = detect_boundaries(lines)
    chunks = build_chunks(lines, boundaries)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUTPUT_DIR / "chunks.json"
    out_path.write_text(
        json.dumps(chunks, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(f"총 {len(chunks)}개 청크 생성 → {out_path}\n")
    for c in chunks:
        print(f"  [{c['chunk_id']}] {c['title']} ({len(c['text']):,}자)")


if __name__ == "__main__":
    main()
