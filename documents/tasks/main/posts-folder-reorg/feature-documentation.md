# 기능 문서 — posts 폴더 카테고리+시리즈 2단계 재구성

## 무엇이 바뀌었나
- `content/posts/`의 749개 글을 평면 구조에서 `content/posts/{category}/{series}/` 2단계 구조로 재배치.
  - 시리즈 있는 743개 → `posts/{category}/{series}/`
  - 시리즈 없는 6개(notice) → `posts/notice/` 직속
- `hugo.toml`에 `[permalinks] posts = "/posts/:contentbasename/"` 추가.

## 동작 원리 (URL 유지)
- Hugo 기본 permalink는 파일 위치를 URL에 반영하므로, 폴더를 옮기면 URL이 바뀐다.
- `:contentbasename` 토큰은 **파일명(확장자 제외)만** 사용 → 하위 폴더 깊이와 무관하게 URL이 `/posts/{파일명}/`로 고정된다.
- 재구성 전 URL과 완전히 동일(파일명을 그대로 유지했기 때문). 748개 글의 `aliases`(구 Jekyll URL 호환)도 그대로 유효.

## 검증 결과
- 빌드 에러 0.
- 재구성 전/후 전체 페이지 URL 목록 diff: **사라진 URL 0, 추가된 URL 0** (총 4526페이지 동일, 글 749개 동일).
- 카테고리/시리즈/아카이브/홈/RSS 페이지 정상.
- git: 749개 파일 모두 rename(R)으로 추적 → 이력 보존.

## 앞으로 새 글 추가하는 법
1. 글의 카테고리와 시리즈를 정한다.
2. `content/posts/{category}/{series}/YYYY-MM-DD-slug.md` 위치에 파일 생성.
   - notice처럼 시리즈가 없으면 `content/posts/{category}/` 직속에 둔다.
3. 파일명(basename)이 곧 URL이 되므로, 파일명은 유일하게 유지한다.
4. frontmatter의 `categories`/`series`는 폴더와 별개로 그대로 작성(사이트 분류·필터는 frontmatter 기준).
