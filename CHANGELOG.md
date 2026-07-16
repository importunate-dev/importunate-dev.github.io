# CHANGELOG

이 블로그(importunate-dev.github.io)의 변경 이력. [Keep a Changelog](https://keepachangelog.com/ko/1.1.0/) 형식을 참고하며, [유의적 버전(SemVer)](https://semver.org/lang/ko/)을 따른다.

- 사용자에게 보이는 큰 기능/개편 → MINOR (`1.x.0`)
- 버그 수정·작은 개선 → PATCH (`1.0.x`)
- 사이트 구조/URL 체계의 호환성 깨지는 변경 → MAJOR (`x.0.0`)

각 릴리즈는 `content/posts/notice/`에 공지 글로도 안내한다.

## [Unreleased]

## [1.1.0] - 2026-07-16

### Added
- 상단 메뉴에 **공지** 추가(그동안 메뉴로 접근 불가하던 notice 카테고리).
- 카테고리 페이지 **더보기** 버튼: 초기 30개만 표시하고 점진적으로 더 렌더(대량 DOM 초기 부담 감소). 시리즈 필터와 연동.
- `README.md` 추가.
- 누락돼 있던 글 6개에 `description` 보강.

### Changed
- 검색 인덱스(`index.json`) 경량화: 중복·미표시 필드인 `summary`를 인덱스와 `fuseOpts.keys`에서 제거. 전문(`content`) 검색은 유지하면서 크기 5.7MB→3.2MB(약 44%↓), 브라우저 파싱/Fuse 인덱싱 부담 감소.
- **jungle 카테고리(76개)를 log 카테고리의 `jungle` 시리즈로 통합**. 글 URL은 그대로 유지(파일명 기준). 부트캠프 시절 레거시 콘텐츠를 로그 하위에서 시리즈로 열람 가능.
- CI Hugo 버전을 `0.147.1` → `0.162.1`로 정렬(로컬과 일치).
- `hugo.toml`: deprecated `languageCode` → `locale`로 이전(빌드 경고 제거).
- `archetypes/default.md`를 사이트 표준 YAML frontmatter(categories/tags/series/ShowToc)로 정비.

### Notes
- 남은 개선 후보(추후): 원격 이미지 width/height(CLS), thin/중복 description 다듬기, 기본 OG 이미지 에셋 지정. 테마 내부 deprecation 경고 2건은 PaperMod 서브모듈 업데이트 필요.

## [1.0.0] - 2026-07-16
버전 관리 시작 릴리즈. 블로그 사용성 개선 + 콘텐츠 구조 정리.

### Added
- 최근 7일 내 글에 주황색 `N` 뱃지(홈 목록 + 해당 카테고리 메뉴). `recentDays` 파라미터로 기준 조정 가능.
- 카테고리 페이지에 시리즈 필터 버튼 바(클라이언트 사이드 필터).
- 본문 이미지 클릭 시 원본을 새 창에서 크게 보기.
- `[permalinks] posts = "/posts/:contentbasename/"` — 폴더 위치와 무관하게 URL 고정.

### Changed
- 메뉴 순서: `홈 → 소개 → 공부 → 로그 → 프로젝트 → 일상 → 검색 → 아카이브`.
- 목차 링크 hover 커서를 pointer로.
- 게임 개발 글 분류: `study` → `project`.
- `content/posts/`를 `posts/{category}/{series}/` 2단계 구조로 재구성(749개, URL 무변경).

[Unreleased]: https://github.com/importunate-dev/importunate-dev.github.io/compare/v1.1.0...HEAD
[1.1.0]: https://github.com/importunate-dev/importunate-dev.github.io/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/importunate-dev/importunate-dev.github.io/releases/tag/v1.0.0
