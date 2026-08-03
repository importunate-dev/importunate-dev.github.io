# 블로그 탐색·성능·SEO 개선 기능 문서

## 홈

- 소개 영역의 중복 CTA를 제거하고 `대표 프로젝트 → 최근 글` 순서로 탐색한다.
- `content/portfolio/*/index.md` 중 `featured: true`인 문서를 `featuredOrder` 순서로 최대 3개 노출한다.
- 최근 글 제목 옆의 `전체 보기`는 아카이브로 연결한다.
- 별도 포트폴리오 메뉴는 제거하고 소개 페이지에 프로젝트 요약을 통합한다. 기존 `/portfolio/`는 소개 페이지로 이동한다.

## 카테고리와 시리즈

- 카테고리 목록은 Hugo의 전통적인 서버 페이지네이션을 사용한다.
- 상단 시리즈 칩은 JavaScript 필터가 아니라 `/series/{term}/` 링크다.
- 필터 상태가 URL로 표현되므로 링크 공유, 뒤로 가기, JavaScript 비활성 환경을 지원한다.

## 검색

- 인덱스 필드: title, description, headings, permalink, date, year, categories, tags, series.
- 본문 전문은 초기 인덱스에서 제외한다.
- 카테고리, 시리즈, 연도 필터를 검색어와 함께 사용할 수 있다.
- 제목·태그·시리즈에서 최대 8개의 자동완성 후보를 제공한다.
- 결과는 최대 50개를 표시하고 실제 전체 결과 수를 알린다.
- 검색 결과 링크는 위·아래 방향키로 이동할 수 있다.

## 태그

- 태그 허브에는 두 편 이상에서 사용된 태그만 표시한다.
- 태그 루트와 개별 term은 `robotsNoIndex` cascade를 통해 검색엔진 색인에서 제외한다.
- 기존 게시글의 태그 값은 콘텐츠 의미 보존을 위해 일괄 삭제하지 않았다.
- 신규 글은 재사용 가능한 태그 3~5개를 권장한다.

## 공유와 구조화 데이터

- 기본 공유 이미지는 `static/og-default.png`이며 1200×630 PNG다.
- 홈페이지는 WebSite와 Person을 각각 선언한다.
- 게시글은 BlogPosting, 일반 단일 페이지는 WebPage, 목록은 CollectionPage로 선언한다.
- 작성자 이름은 사이트명 대신 `배준수`로 고정한다.

## 이미지와 댓글

- Markdown 이미지에는 `loading=lazy`, `decoding=async`가 적용된다.
- Goldmark 속성 문법으로 width, height, srcset, sizes를 전달할 수 있다.
- Giscus는 사용자가 댓글 영역에 접근하거나 버튼을 누를 때만 로드한다.

## 자동 검증

`python3 scripts/validate_site.py --public public`은 다음을 확인한다.

- 게시글 필수 frontmatter와 카테고리 값
- 검색 인덱스 스키마와 2MB 크기 예산
- 주요 카테고리 첫 페이지 200KB 크기 예산
- 홈 포트폴리오 링크와 기본 OG 이미지
- OG 이미지의 1200×630 크기
- 태그 noindex와 sitemap 제외
- 생성된 HTML의 내부 링크와 로컬 자산 존재 여부

PR에서는 Hugo 프로덕션 빌드 후 이 검증을 실행하며, Pages 업로드와 배포는 수행하지 않는다.
