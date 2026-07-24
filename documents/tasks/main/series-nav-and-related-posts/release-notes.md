# 릴리즈 노트: v1.2.0 (2026-07-24)

## 요약
글 간 연결 강화 릴리즈. 시리즈 목차 박스, 시리즈 범위 이전/다음 편, 관련 글 추천을 포스트 하단에 추가하고 og:image 폴백·JSON-LD publisher를 정비했다.

## 변경 파일
| 파일 | 변경 |
|---|---|
| `layouts/partials/post_nav_links.html` | 신규 — 테마 파셜 오버라이드(시리즈 박스+시리즈 내비+관련 글 조립, 전역 내비 폴백) |
| `layouts/partials/series_box.html` | 신규 — 접이식 시리즈 목차(20편 초과 시 ±7편 윈도우) |
| `layouts/partials/related_posts.html` | 신규 — Related Content 4개 카드 |
| `hugo.toml` | `[related]` 블록(tags 100/categories 40/date 10, series 제외), `params.images` og:image 폴백, `params.schema.publisherType = "person"` |
| `layouts/partials/extend_head.html` | `.series-box`, `.related-posts` CSS 추가(다크모드 대응) |
| `CHANGELOG.md` | v1.2.0 항목 |
| `content/posts/notice/2026-07-24-notice-v1-2.md` | 공지 글 |

## 사용자 영향
- 시리즈 글에서 순서대로 읽기·전체 목차 파악 가능. 내부 링크 증가로 SEO(크롤링 경로)·체류시간 개선 기대.
- 커버 없는 글도 소셜 공유 시 미리보기 이미지 표시.

## 남은 후속 과제
- 1200×630 전용 기본 OG 이미지 제작 후 `params.images` 교체 (현재 apple-touch-icon 180px 임시 사용).
- 시리즈 term 페이지(`/series/{name}/`)는 기본 렌더 — 필요 시 커스텀 여지.

## 롤백
파셜 3개 삭제 + hugo.toml 3개 블록 제거 + extend_head.html CSS 블록 제거로 완전 원복 가능 (콘텐츠 무변경).
