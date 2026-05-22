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
