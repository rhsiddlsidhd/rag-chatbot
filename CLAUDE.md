# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this
repository.

## Git Strategy

브랜치 흐름: `feat/*` → `dev` → `main`

- 하나의 브랜치에 두 개 이상의 작업을 섞지 않는다
- `feat/*` 브랜치를 `main`에 직접 병합하지 않는다
- `feat/*` 브랜치를 `dev` 검증 없이 `main`으로 올리지 않는다
- `dev`에서 검증이 완료되지 않은 상태로 `main`에 병합하지 않는다
- 충돌 해결을 `main`에서 하지 않는다 — 반드시 `feat/*` → `dev` 단계에서 해결한다
- 로컬에서 `dev`에 병합이 완료된 `feat/*` 브랜치를 남기지 않는다
