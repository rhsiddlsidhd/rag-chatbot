# Build Log

## 2026-05-22 — 벡터 스토어 선택

> 초기 계획: ChromaDB + langchain-chroma 조합으로 임베딩 벡터 저장

! ChromaDB 1.5.9 실행 시 segfault 발생
  - Python 3.14 환경에서 `uv run src/embedder.py` 실행 → segfault (exit 139)
  - Python 3.12로 다운그레이드 후 재시도 → 동일하게 segfault
  - 원인 분석: chromadb 1.x가 내부적으로 Rust 바인딩(`chromadb.api.rust.RustBindingsAPI`)을 사용하며, 해당 바인딩이 현재 Windows 환경에서 불안정
  - 레거시 Python 구현체(`chromadb.api.segment.SegmentAPI`) 강제 시도 → `hnswlib` 모듈 없음으로 실패
  - PowerShell에서도 동일하게 exit code 5 (Windows ACCESS_VIOLATION = segfault) 확인

> ChromaDB 포기, FAISS로 교체 결정
  - `faiss-cpu`는 Windows 공식 wheel을 제공하고 Python 3.14에서 안정적으로 동작
  - `langchain-community`에 FAISS 통합이 이미 포함되어 있어 추가 의존성 최소화
  - 45개 청크 규모에서 ChromaDB와 기능 차이 없음

* ChromaDB 버전별 구현 차이
  - 0.x: 순수 Python 기반 (`hnswlib` 사용)
  - 1.x: Rust 바인딩으로 전환 (`chromadb.api.rust.RustBindingsAPI`)
  - Rust 바인딩은 성능 향상이 목적이나 플랫폼 호환성 문제가 발생할 수 있음

* Windows에서 segfault 해석
  - Linux: exit code 139 (SIGSEGV)
  - Windows: exit code 5 (0xC0000005, STATUS_ACCESS_VIOLATION)
  - 동일한 메모리 접근 위반이지만 OS마다 표현 방식이 다름

* 벡터 스토어 선택 기준
  - 플랫폼 호환성, 의존성 복잡도, 프로젝트 규모를 함께 고려해야 함
  - 소규모 RAG 프로젝트에서는 FAISS가 ChromaDB보다 설치 및 실행이 단순함

## 2026-05-22 — 청킹 전략 변경

> 초기 목표: 페이지 단위 split + overlap 청킹 구현 (sliding window 학습)

! PDF 전처리 단계에서 막힘
  - PDF마다 구조가 달라 일관된 파싱 불가
  - 스캔본 PDF는 OCR 처리 필요 — 텍스트 추출 자체가 부정확
  - 파싱 후 불필요한 내용(페이지 번호, 헤더, 푸터 등) 제거 로직을 일반화하기 어려움
  - 전처리 문제를 해결하지 못한 채 청킹 단계로 진입 불가

> 우회 전략으로 전환
  - 구조가 깨끗한 단일 PDF(테니스 규정집) 선택
  - 전체 텍스트 추출 후 itf-rules-body.txt 로 수동 슬라이싱
  - Rule 번호 경계를 기준으로 의미 단위 청킹 (overlap 없음)

* RAG에서 전처리가 청킹보다 먼저 풀려야 하는 문제임을 직접 체감
  - 대부분의 RAG 튜토리얼은 깨끗한 데이터를 전제로 청킹을 설명함
  - 실제 PDF는 구조, 품질, 포맷이 제각각이라 전처리 자체가 독립적인 난제
  - overlap 청킹 원리는 구현했으나, 적용 전제(깨끗한 텍스트)를 만드는 것이 더 어려웠음

