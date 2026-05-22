# 실행 계획: Jekyll → Hugo 마이그레이션 마무리 & 정리

## 개요
- 작업 목표: Hugo 마이그레이션 이후 남아있던 GitHub 저장소 메타데이터·잔존 브랜치·로컬 작업본·일회성 산출물 정리
- 브랜치: `main`
- 작성일: 2026-05-22
- 디렉토리: `documents/tasks/main/hugo-migration-cleanup/`

## 배경 & 맥락

- **왜 필요한가**: Jekyll → Hugo + PaperMod 마이그레이션은 이미 라이브 사이트에 반영되어 정상 동작 중이지만, GitHub 저장소의 default branch가 여전히 `master`이고, 더 이상 사용하지 않는 `master`/`test` 브랜치 및 로컬 작업본(`../junsoopooh.github.io/`)이 남아 혼란을 야기함. 일회성 마이그레이션 스크립트도 저장소에 잔존
- **현재 상태**: Hugo 사이트 정상 배포(GitHub Pages build_type: workflow), 741개 게시글에 URL aliases 추가 완료, Giscus 댓글 활성화, Decap CMS 제거, blog-images 별도 저장소로 분리 완료. 단, 정리 작업 미완료
- **기대 결과**: 저장소가 Hugo 기반임을 명확히 반영(default branch=main, description 갱신), 불필요한 브랜치/파일/디렉토리 제거

## 마이그레이션 상태 검증 (작업 전)

| 항목 | 상태 | 근거 |
|------|------|------|
| Hugo 사이트 라이브 | ✅ | `/posts/...` 200, sitemap.xml Hugo 형식 |
| 741개 게시글 변환 | ✅ | `content/posts/*.md` 741개 |
| URL aliases | ✅ | 741개 전부 `^aliases:`, Jekyll URL도 200 |
| Giscus 댓글 | ✅ | `layouts/partials/comments.html` 실제 키값 포함, `comments = true` |
| Decap CMS 제거 | ✅ | `static/admin/` 없음 |
| blog-images CDN | ✅ | `cdn.jsdelivr.net/gh/importunate-dev/blog-images/...` 200 |
| GitHub Actions 배포 | ✅ | 최근 빌드 성공 2026-04-16 |
| Google SC 검증 파일 | ✅ | `static/google4cb727437fad26da.html` 배포됨, 200 |
| `junsoopooh/...` 별도 저장소 | N/A | 동일 저장소(id 619531722)의 rename redirect alias |

## 논의 기록

### Q&A

| # | 질문 (사용자) | 답변 (AI) | 결론 |
|---|--------------|-----------|------|
| 1 | `../junsoopooh.github.io`가 안 쓰이는지 확인하고 안 쓰면 삭제 | 별도 GitHub 저장소가 아니라 동일 저장소(id 619531722)에 대한 rename redirect임을 확인. 로컬 디렉토리는 안전하게 삭제 가능 | 로컬 디렉토리 삭제 |
| 2 | 원격 master 브랜치는? | `jekyll-backup`과 동일 커밋(`eedfc6a`)으로 보존되어 있으므로 master는 삭제해도 안전 | 원격 master 삭제 |
| 3 | 원격 test 브랜치는? | Hugo 워크플로우 디버깅용 임시 브랜치. main에 모든 변경 통합 완료 | 원격 test 삭제 |
| 4 | 옛 GitHub 저장소(`junsoopooh/...`)는? | 사용자가 GitHub 계정명을 `junsoopooh` → `importunate-dev`로 rename. `junsoopooh` 사용자는 404, `junsoopooh/junsoopooh.github.io`는 새 저장소로 자동 redirect → 별도 처리 불필요 | 자동 redirect로 보존, 별도 작업 없음 |
| 5 | 마이그레이션 산출물 처리? | `MIGRATION_GUIDE.md`, `scripts/setup-blog-images.sh`, `scripts/add_aliases.py` 모두 일회성 작업 완료. git 히스토리에 남으므로 삭제 가능 | 삭제 |

### 고민 & 의사결정

- **고민**: `../junsoopooh.github.io/` 로컬 디렉토리에 미커밋 `_includes/head.html` google-site-verification 토큰 변경(`A90D11nfnmg1...` → `KlUUFMNGky...`)이 있음. 삭제 시 손실
- **대안 검토**: (1) Hugo 사이트에 새 토큰 메타태그 추가 후 삭제 (2) 그대로 삭제
- **결론**: Hugo 사이트는 이미 `static/google4cb727437fad26da.html` 파일 방식으로 Google Search Console 검증되어 있고 라이브 서빙 200 응답 확인. 옛 미커밋 토큰은 사용자가 새로 시도하다가 미완료한 것으로 추정. 필요시 Search Console에서 재검증 가능하므로 그대로 삭제 결정

- **고민**: 원격 브랜치 삭제 순서
- **대안 검토**: (1) 브랜치 삭제 먼저 → default branch 변경 / (2) default branch 변경 먼저 → 브랜치 삭제
- **결론**: default branch가 `master`인 상태에서는 master 삭제가 거부됨. default를 main으로 변경한 뒤 master/test 삭제하는 순서가 올바름

## 작업 범위

### 변경 파일
- 삭제: `MIGRATION_GUIDE.md`, `scripts/setup-blog-images.sh`, `scripts/add_aliases.py`
- 신규: `documents/tasks/main/hugo-migration-cleanup/{implementation-plan,feature-documentation,release-notes}.md`

### 원격 메타데이터 변경
- default_branch: `master` → `main`
- description: `"Importunate / Jekyll Themes"` → `"Importunate / Hugo + PaperMod 기반 개인 블로그"`
- GitHub Pages source branch: `master` → `main` (build_type은 workflow 그대로)
- 원격 브랜치 삭제: `master`, `test`

### 로컬 외부 변경
- `/Users/junsu/Documents/codespace/project/junsoopooh.github.io/` 디렉토리 삭제

## 단계별 계획

1. **Phase 1 — GitHub 원격 정리** ✅
   - `gh api -X PATCH .../importunate-dev.github.io -f default_branch=main`
   - `gh api -X PATCH .../importunate-dev.github.io -f description=...`
   - `gh api -X PUT .../pages -f 'source[branch]=main' -f 'source[path]=/'`
   - `git push origin --delete master`
   - `git push origin --delete test`

2. **Phase 2 — 로컬 작업본 정리** ✅
   - `rm -rf ../junsoopooh.github.io`

3. **Phase 3 — 일회성 산출물 삭제 & 커밋** ✅
   - `git rm MIGRATION_GUIDE.md scripts/setup-blog-images.sh scripts/add_aliases.py`
   - 커밋 메시지: "Chore: 일회성 마이그레이션 산출물 제거"
   - `git push origin main`

4. **Phase 4 — Plan 모드 산출물 작성** (현재 단계)
   - `documents/tasks/main/hugo-migration-cleanup/implementation-plan.md`
   - `documents/tasks/main/hugo-migration-cleanup/feature-documentation.md`
   - `documents/tasks/main/hugo-migration-cleanup/release-notes.md`
   - 별도 커밋 후 푸시

5. **Phase 5 — 최종 검증**
   - 원격 브랜치 상태
   - default branch
   - description
   - 라이브 사이트 URL 확인
   - GitHub Actions 빌드 상태

## 완료 기준

- [x] GitHub default branch가 `main`
- [x] 원격에 `main`, `jekyll-backup` 2개 브랜치만 존재
- [x] 저장소 description이 Hugo 기반임을 반영
- [x] `../junsoopooh.github.io/` 로컬 디렉토리 삭제됨
- [x] 일회성 마이그레이션 파일 3개 저장소에서 제거 & 커밋 푸시
- [ ] `documents/tasks/main/hugo-migration-cleanup/`에 3개 문서 작성 & 커밋
- [ ] 최종 검증 모두 통과
