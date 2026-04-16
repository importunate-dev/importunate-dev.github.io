# 실행 계획: Jekyll → Hugo 마이그레이션 완료

## 개요
- 작업 목표: Jekyll 블로그를 Hugo + PaperMod으로 완전히 전환하고 배포
- 브랜치: `main`
- 작성일: 2026-04-16
- 디렉토리: `documents/tasks/main/hugo-migration-complete/`

## 배경 & 맥락
- **왜 필요한가**: Hugo 마이그레이션이 ~95% 완료되어 있으나 실제 배포 전환이 안 됨. 현재 `master` 브랜치의 Jekyll이 배포 중
- **현재 상태**: 741개 게시글 변환 완료, PaperMod 테마 설정 완료, GitHub Actions 워크플로우 작성 완료
- **기대 결과**: Hugo 사이트가 https://importunate-dev.github.io 에서 정상 동작, 기존 URL 리다이렉트, Giscus 댓글 활성화

## 논의 기록

### Q&A

| # | 질문 (사용자) | 답변 (AI) | 결론 |
|---|--------------|-----------|------|
| 1 | URL aliases 설정할까? | SEO 보존을 위해 권장 | aliases 설정 (사용자 선택) |
| 2 | 댓글 시스템은? | Giscus 권장 (무료, 다크모드, GitHub 기반) | Giscus로 전환 (사용자 선택) |
| 3 | Decap CMS 설정할까? | OAuth App 필요 | 필요 없음 (사용자 선택) → 삭제 |

### 고민 & 의사결정

- **고민**: aliases를 YAML 라이브러리로 파싱 vs 문자열 기반 삽입
- **대안 검토**: YAML 라이브러리는 포맷을 재정렬할 수 있음 / 문자열 삽입은 기존 형식 보존
- **결론**: 문자열 기반 삽입으로 기존 front matter 포맷 보존

- **고민**: 배포 전환 순서 (먼저 전환 vs 먼저 push)
- **대안 검토**: 먼저 전환하면 빌드 실패 위험 / 먼저 push 후 빌드 성공 확인 후 전환이 안전
- **결론**: 모든 변경 push → Actions 빌드 성공 확인 → Pages 설정 전환

## 작업 범위

### 변경 파일
- `content/posts/*.md` (741개) - aliases 추가
- `hugo.toml` - comments = true 추가
- `layouts/partials/comments.html` - 신규 생성 (Giscus)
- `static/admin/` - 삭제 (Decap CMS 제거)

## 단계별 계획

### Phase 1: URL Aliases 추가 (741개 게시글)

Jekyll URL 패턴: `/:categories/:title/`
- 예: `2024-03-18-developer240318.md` + `categories: ["study"]` → `/study/developer240318/`

**스크립트 로직**:
1. `content/posts/*.md` 순회
2. 파일명에서 slug 추출: `YYYY-MM-DD-{slug}.md` → `{slug}`
3. front matter에서 첫 번째 category 추출
4. `aliases: ["/{category}/{slug}/"]`를 front matter 닫는 `---` 직전에 삽입
5. 이미 aliases가 있으면 스킵

**엣지 케이스**: categories 없는 포스트 → 로그 남기고 스킵

### Phase 2: Giscus 댓글 설정

**사전 조건 (사용자 수동 작업 필요)**:
1. GitHub repo Settings → Discussions 활성화
2. Discussion 카테고리 "Comments" 생성 (Announcements 타입)
3. https://github.com/apps/giscus 설치 → 레포 접근 허용
4. https://giscus.app 에서 repo-id, category-id 확인

**구현**:
1. `layouts/partials/comments.html` 생성 (Giscus 스크립트)
2. `hugo.toml`의 `[params]`에 `comments = true` 추가

### Phase 3: Decap CMS 제거

- `static/admin/config.yml` 삭제
- `static/admin/index.html` 삭제
- `static/admin/` 디렉토리 삭제

### Phase 4: 배포 전환

1. 모든 변경사항 커밋 & push to `main`
2. GitHub Actions에서 Hugo 빌드 성공 확인
3. GitHub repo Settings → Pages → Source를 "GitHub Actions"로 변경
4. 라이브 사이트 검증

### Phase 5: 배포 후 작업 (수동)

1. Google Search Console에서 sitemap.xml 재제출
2. Google Analytics 실시간 리포트로 추적 확인
3. (선택) `main`을 기본 브랜치로 설정

## 롤백 계획
Hugo 사이트에 문제 발생 시 → Pages 설정을 "Deploy from branch: master"로 되돌리면 즉시 Jekyll 복원

## 완료 기준
- [ ] 741개 게시글에 aliases 추가됨
- [ ] 기존 Jekyll URL로 접속 시 리다이렉트 동작
- [ ] Giscus 댓글이 게시글에 표시됨
- [ ] Decap CMS 파일 제거됨
- [ ] GitHub Actions 빌드 성공
- [ ] https://importunate-dev.github.io 에서 Hugo 사이트 정상 동작
- [ ] ads.txt, sitemap.xml, robots.txt 정상 접근 가능
