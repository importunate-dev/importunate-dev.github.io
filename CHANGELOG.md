# CHANGELOG

이 블로그(importunate-dev.github.io)의 변경 이력. [Keep a Changelog](https://keepachangelog.com/ko/1.1.0/) 형식을 참고하며, [유의적 버전(SemVer)](https://semver.org/lang/ko/)을 따른다.

- 사용자에게 보이는 큰 기능/개편 → MINOR (`1.x.0`)
- 버그 수정·작은 개선 → PATCH (`1.0.x`)
- 사이트 구조/URL 체계의 호환성 깨지는 변경 → MAJOR (`x.0.0`)

각 릴리즈는 `content/posts/notice/`에 공지 글로도 안내한다.

## [Unreleased]

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

[Unreleased]: https://github.com/importunate-dev/importunate-dev.github.io/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/importunate-dev/importunate-dev.github.io/releases/tag/v1.0.0
