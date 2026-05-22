# 릴리즈 노트: Hugo 마이그레이션 마무리 & 정리

**작업일**: 2026-05-22
**브랜치**: `main`
**관련 커밋**: `6fc8d8a Chore: 일회성 마이그레이션 산출물 제거`

## 요약

Jekyll → Hugo + PaperMod 마이그레이션의 잔존 정리 작업을 완료. 라이브 사이트는 이미 Hugo로 동작 중이었고, 본 작업은 GitHub 저장소 메타데이터·잔존 브랜치·로컬 작업본·일회성 산출물의 정리에 한정됨.

## 변경 사항

### GitHub 저장소 메타데이터

| 항목 | 이전 | 이후 |
|------|------|------|
| Default branch | `master` | `main` |
| Description | `Importunate / Jekyll Themes` | `Importunate / Hugo + PaperMod 기반 개인 블로그` |
| Pages source branch | `master` (workflow build) | `main` (workflow build) |

### 원격 브랜치 정리

- 삭제: `master` (Jekyll 시절. 동일 커밋이 `jekyll-backup`에 보존됨)
- 삭제: `test` (Hugo 워크플로우 디버깅용. main에 통합 완료)
- 유지: `main` (현재 운영), `jekyll-backup` (백업 보존)

### 저장소 파일 변경

삭제된 파일:
- `MIGRATION_GUIDE.md` (Jekyll → Hugo 가이드, 완료)
- `scripts/setup-blog-images.sh` (blog-images 저장소 초기화 스크립트, 완료)
- `scripts/add_aliases.py` (741개 게시글 aliases 추가 스크립트, 완료)

### 로컬 환경 정리

- 삭제: `/Users/junsu/Documents/codespace/project/junsoopooh.github.io/`
  - GitHub 계정명 rename(`junsoopooh` → `importunate-dev`) 이전의 working copy
  - 새 저장소의 `jekyll-backup` 브랜치(`eedfc6a`)에 동일 커밋이 보존되어 있어 안전하게 삭제

## 영향

### 사용자에게 보이는 변경

- 없음. 라이브 사이트 동작은 변함 없음.

### 개발자에게 보이는 변경

- `git clone` 시 기본 체크아웃 브랜치가 `master`에서 `main`으로 변경
- GitHub 저장소 페이지의 설명 문구 갱신
- 일회성 마이그레이션 도구 파일이 저장소에서 제거됨 (필요 시 git 히스토리에서 조회 가능, 커밋 `1f7f36b` 이전 시점)

## 검증 결과

- [x] `gh repo view importunate-dev/importunate-dev.github.io --json defaultBranchRef` → `{"name":"main"}`
- [x] `git ls-remote --heads origin` → `main`, `jekyll-backup` 2개
- [x] Description 갱신됨
- [x] `https://importunate-dev.github.io/` 200, Hugo 사이트 정상
- [x] `https://importunate-dev.github.io/study/developer240318/` 200 (aliases 동작 — Jekyll URL 호환)
- [x] `https://importunate-dev.github.io/google4cb727437fad26da.html` 200 (SC 검증 유지)
- [x] 최근 GitHub Actions 빌드 성공

## 롤백 절차 (참고용)

문제 발생 시:

1. **default branch 되돌리기**:
   ```bash
   gh api -X PATCH repos/importunate-dev/importunate-dev.github.io -f default_branch=master
   ```
   단, master 브랜치를 이미 원격에서 삭제했으므로 먼저 jekyll-backup에서 master 복원 필요:
   ```bash
   git push origin jekyll-backup:master
   ```

2. **Pages를 Jekyll로 임시 복귀**: Settings → Pages → Source를 `Deploy from a branch: jekyll-backup`으로 변경. workflow 기반 Hugo 배포가 중단되고 jekyll-backup 브랜치의 Jekyll 사이트가 빌드됨

## 후속 권장 작업 (수동, 선택)

- Google Search Console에서 sitemap.xml 재제출 (URL 변경 인지 가속)
- Google Analytics 실시간 리포트에서 트래픽 패턴 모니터링
- `archetypes/default.md`를 새 게시글 작성 워크플로우에 맞게 보강
