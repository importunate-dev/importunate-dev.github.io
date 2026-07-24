# 기능 문서: 시리즈 내비게이션 + 관련 글 추천 (v1.2.0)

## 개요
포스트 상세 페이지 하단(태그 아래, 공유 버튼 위)에 세 가지 요소를 추가했다.
1. **시리즈 목차 박스** — 접이식 `<details>`, 현재 글 하이라이트, (i/N편) 진행 표시
2. **시리즈 범위 이전/다음 편** — 같은 series 내 날짜 오름차순 기준
3. **관련 글 추천** — Hugo 내장 Related Content, 태그·카테고리 기반 4개

## 구현 구조

```
layouts/partials/post_nav_links.html   ← PaperMod 파셜 오버라이드 (오케스트레이터)
├── layouts/partials/series_box.html   ← 시리즈 목차 박스
├── (inline) 시리즈 범위 .paginav      ← PaperMod 기존 카드 스타일 재사용
├── (inline) 전역 시간순 .paginav      ← 시리즈 없는 글 폴백 (테마 원본 복사)
└── layouts/partials/related_posts.html ← 관련 글
```

- **single.html 전체를 복사하지 않고** `post_nav_links.html` 파셜만 오버라이드 — 테마 서브모듈 업데이트 시 diff 확인 범위 최소화.
- 렌더 조건: `ShowPostNavLinks=true`(hugo.toml 전역) + 페이지가 mainSections 소속. **끄면 관련 글도 같이 꺼지는 결합** 있음(파셜 주석에 기록).

## 동작 상세

### 시리즈 박스 (`series_box.html`)
- 정렬: `$term.Pages.ByDate` 오름차순 → 가장 오래된 글이 1편. 같은 날짜는 Hugo tie-break(weight→date→linkTitle→filePath)로 결정적. 순서 교정 필요 시 frontmatter `weight` 사용.
- **윈도우 처리**: 시리즈가 20편 초과면 현재 글 ±7편(15편)만 렌더 + 위/아래 "전체 N편 보기" 링크(시리즈 term 페이지 `/series/{name}/`). `<ol start>`로 실제 편 번호 유지. weekly(315편) 페이지의 HTML 폭증 방지 목적.
- 현재 글: 링크 없는 `<li class="current" aria-current="page">`.
- 기본 접힘 — summary에 시리즈명(term 페이지 링크)과 진행 위치가 노출됨.
- CSS 클래스 `series-window-more`는 기존 카테고리 페이지 "더보기" 버튼(`.series-more`)과의 충돌을 피하려고 별도 명명.

### 시리즈 이전/다음
- `cur-1`(과거) = « 이전 편, `cur+1`(미래) = 다음 편 ». PaperMod 원본 라벨 의미와 일관.
- 시리즈 없는 글(notice 6개) 또는 1편짜리 시리즈: 테마 원본과 동일한 전역 시간순 내비로 폴백.

### 관련 글 (`related_posts.html` + hugo.toml `[related]`)
- 인덱스: tags(100) / categories(40) / date(10), threshold 30, includeNewer.
- **series 인덱스 의도적 제외** — weekly끼리 추천 도배 방지. 시리즈 탐색은 시리즈 박스가 담당.
- `site.RegularPages.Related . | first 4`, 자기 자신 자동 제외. 제목+날짜+첫 태그 카드.

### SEO 부수 변경 (hugo.toml)
- `params.images = ["apple-touch-icon.png"]` — 커버 없는 글 og:image 폴백. **추후 1200×630 전용 이미지로 교체 권장.**
- `params.schema.publisherType = "person"` — JSON-LD publisher를 Person으로.

## 스타일
- `layouts/partials/extend_head.html` 인라인 `<style>`에 `.series-box`, `.related-posts` 추가.
- PaperMod CSS 변수(--entry/--border/--primary/--secondary/--radius)만 사용 → 다크모드 자동 대응. 강조색 #ff7a18(기존 관례).

## 성능
- 빌드: 4.0s → 4.7s (+0.7s). partialCached 미사용 — 윈도우 도입으로 페이지당 렌더 ≤21항목이라 캐시 이득 없음.

## 검증 결과 (2026-07-24)
| 케이스 | 결과 |
|---|---|
| weekly 1편 | (1/315편), ol start=1, 다음 편만, 아래 더보기만 ✅ |
| weekly 150편 | (150/315편), ol start=143, 이전/다음 둘 다, 위아래 더보기 ✅ |
| weekly 315편 | (315/315편), ol start=301, 이전 편만 ✅ |
| cs_alone(13편) | 전체 목록, 더보기 없음 ✅ |
| 시리즈 없는 notice | series-box 없음, 전역 paginav 폴백 ✅ |
| 관련 글 | weekly 글에 비-weekly 4개 추천 (도배 없음) ✅ |
| og:image / publisher | 폴백 이미지·Person 출력 확인 ✅ |
