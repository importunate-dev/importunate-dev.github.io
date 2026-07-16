# 실행 계획 — posts 폴더 카테고리+시리즈 2단계 재구성

## 개요
- **작업 목표**: 평면(flat)으로 쌓인 749개 글을 `content/posts/{category}/{series}/` 2단계 폴더 구조로 재배치하여 글 관리·추가를 쉽게 한다. **단, 기존 URL·색인·aliases는 100% 그대로 유지한다.**
- **브랜치**: `main`
- **작성일**: 2026-07-16
- **디렉토리**: `documents/tasks/main/posts-folder-reorg/`

## 배경 & 맥락
- **왜 필요한가**: 현재 `content/posts/`에 749개 `.md` 파일이 전부 평면으로 쌓여 있어, 새 글을 추가하거나 특정 글을 찾을 때 불편하다. 폴더를 카테고리/시리즈로 나누면 파일 탐색·추가가 쉬워진다.
- **현재 상태**:
  - `content/posts/YYYY-MM-DD-slug.md` 형식의 파일 749개가 한 폴더에 평면 배치.
  - 글 URL = `/posts/{파일명전체}/` (예: `/posts/2026-07-16-game_maker/`). Hugo 기본 permalink가 파일 basename을 그대로 사용.
  - **748개 글이 `aliases`로 구 Jekyll URL 호환** 중 → URL 변경 시 색인/링크 붕괴 위험.
- **기대 결과**: 폴더는 2단계로 정리되지만, 방문자·검색엔진이 보는 URL은 재구성 전과 완전히 동일.

## 논의 기록

### Q&A
| # | 질문 (사용자) | 답변/결정 | 결론 |
|---|--------------|-----------|------|
| 1 | posts 폴더를 카테고리·시리즈로 분리하는 것 어때? | URL이 바뀌면 SEO/색인 위험. `[permalinks]`로 URL 고정 가능한지 PoC로 검증 | 안전하게 가능함이 검증됨 |
| 2 | 재구성 깊이는? | **카테고리 + 시리즈 2단계** 선택 | `posts/{category}/{series}/` |
| 3 | 진행 방식은? | **계획서 먼저 작성** 후 확인 | 본 문서 작성 |

### 고민 & 의사결정
- **고민 1 — URL 유지 방법**
  - 대안 A: 폴더만 옮기고 방치 → 기본 동작상 URL이 `/posts/{category}/{series}/{slug}/`로 바뀜. **748개 글 색인·aliases·외부 링크 붕괴. 기각.**
  - 대안 B: `[permalinks] posts = "/posts/:contentbasename/"` 추가 → 폴더 깊이와 무관하게 파일 basename으로 URL 고정.
  - **결론**: 대안 B. `:contentbasename` 토큰은 파일명(확장자 제외)만 사용하므로 하위 폴더 위치가 URL에 영향을 주지 않는다. 현재 flat 구조의 URL과도 완전히 동일(무변경).
  - **검증(PoC 완료)**:
    1. 1단계 이동(`posts/study/…`) → URL `/posts/2026-07-15-developer/` 유지 확인.
    2. 2단계 이동(`posts/study/developer/…`) → 동일하게 URL 유지 + 카테고리/시리즈 목록 정상 노출 확인.
    3. 두 PoC 모두 `git mv`로 이동 후 원복, 저장소 잔여 변경 0 확인.

- **고민 2 — 2단계 구조의 엣지 케이스**
  - 시리즈 개수 분포 조사 결과: **743개 = 시리즈 정확히 1개, 6개 = 시리즈 0개(전부 `notice`), 시리즈 2개 이상 = 0개.**
  - **결론**: 매핑이 100% 결정적. 시리즈 있는 743개는 `posts/{category}/{series}/`, 시리즈 없는 notice 6개는 `posts/notice/`(시리즈 폴더 없이) 직접 배치.
  - 시리즈명 위험문자(공백/슬래시 등) 검사 → **없음**. 폴더명으로 시리즈명 원문 그대로 사용 안전(대소문자 `MySQL`/`RestfulAPI`/`Godot` 포함, git·macOS·Linux 처리 문제 없음).

## 작업 범위

### 최종 폴더 구조 (카테고리/시리즈 → 글 수)
```
content/posts/
├── jungle/
│   ├── essay/    (7)
│   ├── log/      (68)
│   └── remind/   (1)
├── life/
│   ├── book/     (22)
│   ├── essay/    (2)
│   └── hiking/   (4)
├── log/
│   ├── diary/    (1)
│   ├── interview/(2)
│   └── weekly/   (315)
├── notice/       (6)   ← 시리즈 없음, 카테고리 폴더 직속
├── project/
│   ├── Godot/    (1)
│   ├── codeeat/  (1)
│   ├── nestjs/   (25)
│   └── portfolio/(1)
└── study/
    ├── MySQL/          (48)
    ├── RestfulAPI/     (11)
    ├── algorithm/      (140)
    ├── cleancode/      (47)
    ├── coding_interview/(12)
    ├── cs_alone/       (13)
    ├── csapp/          (6)
    ├── developer/      (7)
    └── network/        (9)
```

### 변경 파일
- `hugo.toml`: `[permalinks] posts = "/posts/:contentbasename/"` 추가 (URL 고정).
- `content/posts/**`: 749개 파일 `git mv`로 하위 폴더 이동 (frontmatter 내용 변경 없음).
- (검토) `archetypes/`: 새 글 작성 편의를 위한 안내는 별도 후속 작업으로 분리 가능.

## 단계별 계획
1. **permalinks 설정 추가**: `hugo.toml`에 `[permalinks] posts = "/posts/:contentbasename/"` 삽입.
2. **이동 스크립트 실행**: 각 글의 frontmatter에서 category(1개)·series(0~1개)를 읽어 대상 경로 결정 후 `git mv`.
   - 시리즈 있음 → `content/posts/{category}/{series}/{원본파일명}`
   - 시리즈 없음(notice) → `content/posts/{category}/{원본파일명}`
3. **빌드 검증**:
   - `hugo --gc --minify` 에러 0.
   - 재구성 전 URL 목록과 재구성 후 URL 목록을 diff → **차이 0**(핵심 회귀 검증).
   - 카테고리/시리즈 목록 페이지, 아카이브, 홈, RSS 정상.
4. **커밋**: 사용자 확인 후 `git mv` 이동을 한 커밋으로.

## 완료 기준
- [ ] `hugo.toml`에 permalinks 설정 추가됨
- [ ] 749개 파일이 계획된 2단계 구조로 이동됨 (git 이력 보존)
- [ ] `hugo --gc --minify` 빌드 에러 0
- [ ] **재구성 전/후 전체 글 URL 목록 diff = 0** (URL 무변경 보증)
- [ ] 카테고리·시리즈·아카이브·홈·RSS 페이지 정상 렌더
- [ ] 새 글 추가 시 해당 `{category}/{series}/` 폴더에 넣으면 되는 워크플로 확인

## 리스크 & 대응
- **URL 회귀**: 3단계에서 전/후 URL 목록 diff로 자동 검증. 차이 발견 시 롤백.
- **대량 git mv 노이즈**: 순수 이동이라 `git mv`로 rename 추적됨. 내용 변경 없음.
- **CI Hugo 버전(0.147.1)과 `:contentbasename` 토큰 호환성**: `:contentbasename`은 Hugo 0.92+ 지원 → 0.147.1 문제 없음. (배포 워크플로에서 재확인)
