# CHANGELOG

이 블로그(importunate-dev.github.io)의 변경 이력. [Keep a Changelog](https://keepachangelog.com/ko/1.1.0/) 형식을 참고하며, [유의적 버전(SemVer)](https://semver.org/lang/ko/)을 따른다.

- 사용자에게 보이는 큰 기능/개편 → MINOR (`1.x.0`)
- 버그 수정·작은 개선 → PATCH (`1.0.x`)
- 사이트 구조/URL 체계의 호환성 깨지는 변경 → MAJOR (`x.0.0`)

각 릴리즈는 `content/posts/notice/`에 공지 글로도 안내한다.

## [Unreleased]

### Added
- 홈에 대표 프로젝트 카드 3개와 최근 글 섹션 제목·전체 보기 링크 추가.
- 검색에 제목·태그·시리즈 자동완성, 카테고리·시리즈·연도 필터, 결과 설명·메타데이터, 키보드 탐색 추가.
- 1200×630 기본 Open Graph 이미지와 작성자·웹사이트·컬렉션 구조화 데이터 추가.
- 댓글을 화면 근처에서만 불러오는 지연 로딩 추가.
- pull request용 Hugo 빌드와 검색 인덱스·페이지 크기·frontmatter·내부 링크 검증 추가.

### Changed
- 카테고리 목록을 전체 렌더 후 숨김 방식에서 서버 페이지네이션으로 변경하고, 시리즈 필터는 공유 가능한 실제 시리즈 링크로 전환.
- 홈의 중복 CTA와 포트폴리오 메뉴를 제거하고, 소개 페이지에 포트폴리오 요약을 통합. 홈 글 목록에는 `최근 글` 제목과 별도 전체 보기 링크 추가.
- 검색 인덱스를 본문 전문에서 제목·설명·목차·분류 중심으로 변경해 3.38MB에서 약 0.32MB로 축소.
- 태그 허브는 두 편 이상에서 쓰인 태그만 노출하고, 태그 taxonomy 전체를 `noindex` 처리.
- 커스텀 CSS를 페이지별 inline 스타일에서 fingerprint된 공통 stylesheet로 이동.
- Markdown 이미지에 async decoding과 width/height 속성 지원 추가.
- 관련 글에서 과도하게 세분화된 태그의 가중치를 낮추고 카테고리 가중치를 높임.
- PaperMod의 Hugo 0.158 이후 deprecated 언어 속성을 로컬 오버라이드에서 교체.

### Fixed
- 스킴이 빠져 내부 링크로 오인되던 localhost·CodeEat URL 8개 수정.
- 제목이 비어 있던 2024-06-26 주간 로그의 제목 복원.

## [1.2.0] - 2026-07-24

### Added
- **글 하단 시리즈 목차 박스**: 접이식 박스에 시리즈 전체 목록 + 현재 글 하이라이트 + (i/N편) 진행 표시. 20편 초과 대형 시리즈(weekly 315편 등)는 현재 글 ±7편 윈도우만 렌더하고 "전체 보기" 링크로 시리즈 페이지 연결(HTML 크기 폭증 방지).
- **시리즈 범위 이전/다음 편 내비게이션**: 기존 전역 시간순 이전/다음 대신 같은 시리즈 안에서 이동. 시리즈 없는 글은 기존 전역 내비게이션으로 폴백.
- **관련 글 추천**: Hugo 내장 Related Content로 글 하단에 태그·카테고리 기반 관련 글 4개 표시. series 인덱스는 의도적으로 제외해 시리즈 도배 방지(시리즈 탐색은 시리즈 박스가 담당).

### Changed
- 커버 없는 글의 `og:image` 폴백 지정(`params.images`) — 소셜 공유 미리보기 개선. 추후 1200×630 전용 이미지 제작 예정.
- JSON-LD publisher를 Organization → **Person**으로(개인 블로그에 맞게).

### Notes
- 구현은 `post_nav_links.html` 파셜 오버라이드로 처리(테마 single.html 전체 복사 회피 → 서브모듈 업데이트 드리프트 최소화). `ShowPostNavLinks=false`로 끄면 관련 글도 함께 꺼지는 결합이 있음.

## [1.1.1] - 2026-07-17

### Changed
- 최근 글 `N` 뱃지를 길쭉한 알약 → 작은 원형으로.
- 카테고리 페이지 시리즈 필터 버튼에도 최근 글이 있으면 `N` 표시(전체 버튼 포함).
- 공지 글 정렬 고정: 같은 날짜의 v1.0.0·v1.1.0 공지에 명시적 시각을 부여해 최신(v1.1.0)이 위에 오도록.

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

[Unreleased]: https://github.com/importunate-dev/importunate-dev.github.io/compare/v1.2.0...HEAD
[1.2.0]: https://github.com/importunate-dev/importunate-dev.github.io/compare/v1.1.1...v1.2.0
[1.1.1]: https://github.com/importunate-dev/importunate-dev.github.io/compare/v1.1.0...v1.1.1
[1.1.0]: https://github.com/importunate-dev/importunate-dev.github.io/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/importunate-dev/importunate-dev.github.io/releases/tag/v1.0.0
