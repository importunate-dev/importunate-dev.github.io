# 블로그 종합 개선: 시리즈 내비게이션 + 관련 글 + SEO 보완

## Context
- 옵시디언 그래프 뷰 논의에서 글 간 내부 링크 부족을 인지 → 시리즈 내 이전/다음 글 + 시리즈 목차 기능 요청, 겸사겸사 블로그·Hugo 종합 개선.
- 웹 조사 결과: PaperMod의 `ShowPostNavLinks`는 전역 시간순이라 시리즈 맥락이 없고, 시리즈 목차·관련 글 기능은 테마에 없음 → 커스텀 파셜로 구현. 관련 글은 Hugo 내장 Related Content 사용.
- 기대 결과: 시리즈 회유(내부 링크·SEO·체류시간) 개선, 소셜 공유 미리보기 개선.

## 사용자와의 논의 기록 (구현 시 implementation-plan.md에 포함)
| # | 질문 | 결론 |
|---|------|------|
| 1 | 시리즈 내비 UI 방식 | **박스형 시리즈 목차** (접이식 + 현재 글 하이라이트 + 이전/다음 버튼) |
| 2 | 개선 범위 | 관련 글 추천 ✅ / PaperMod 편의 기능 ✅ / SEO·메타 ✅ / 댓글 ❌(giscus 이미 존재 확인) |

주요 설계 결정(고민→결론):
- **single.html 전체 오버라이드 vs 파셜 오버라이드** → `post_nav_links.html` 파셜만 오버라이드. 삽입 지점(태그 아래, share 위)이 정확히 이 파셜 위치이고, single.html(자주 변경되는 80줄) 복사 대비 테마 업데이트 드리프트가 최소. 트레이드오프: ShowPostNavLinks=false 시 관련 글도 꺼짐 — 현재 true 고정이라 무해, 파셜 주석으로 기록.
- **대형 시리즈(weekly 315편) HTML 폭증** → 20편 초과 시 현재 글 ±7편(15편) 윈도우 + 앞/뒤 "N편 더 보기"(시리즈 term 페이지 링크). `<ol start>`로 실제 편 번호 유지.
- **정렬** → `$term.Pages.ByDate` 오름차순(오래된 글=1편). Hugo tie-break가 결정적이라 같은 날짜 글도 순서 안정. 예외는 frontmatter `weight`로 교정 가능(escape hatch).
- **Related 인덱스에서 series 의도적 제외** → weekly끼리 추천 도배 방지. 시리즈 탐색은 시리즈 박스가 담당, Related는 "시리즈 밖 관련 글" 역할로 차별화 (tags 100 / categories 40 / date 10, threshold 30).
- **partialCached 미사용** → 윈도우 도입으로 페이지당 렌더 ≤21항목, 총 ~1.5만 li로 미미. 현재 글 하이라이트 때문에 캐시 불가한 구조라 복잡도 대비 이득 없음. `$cur` 인덱스 탐색은 1회만 수행해 dict로 파셜에 전달.

## 점검 결과 조치 불필요 항목 (보고용)
- PaperMod 편의 플래그(ShowReadingTime/ShareButtons/BreadCrumbs/CodeCopyButtons/RssButton 등) 대부분 이미 켜짐. ShowWordCount는 한국어 부정확으로 생략.
- 모든 포스트에 description 존재(누락 0). PaperMod가 BlogPosting + BreadcrumbList JSON-LD 이미 출력. sitemap/robots 존재.

## 변경 파일

### 1. `layouts/partials/post_nav_links.html` (신규 — 테마 파셜 오버라이드, 오케스트레이터)
- 시리즈 있는 글: `series_box.html` 파셜 + 시리즈 범위 이전/다음(`.paginav` 클래스 재사용 — 기존 카드 스타일 그대로).
- 시리즈 없는 글(6개): 테마 원본(`themes/PaperMod/layouts/partials/post_nav_links.html`)의 전역 시간순 nav 코드 폴백.
- 마지막에 `related_posts.html` 호출. `in $mainPages $page` 가드로 about 등 비포스트 페이지 제외.
- 방향 라벨: asc 리스트에서 `cur-1`(과거)=« 이전 편, `cur+1`=다음 편 » (PaperMod 원본 의미와 일관).

### 2. `layouts/partials/series_box.html` (신규)
```
<details class="series-box">
  <summary>📚 <a href="{term.Permalink}">{시리즈명}</a> 시리즈 <span>(i/N편)</span></summary>
  [start>0이면] <div class="series-more">↑ 앞의 N편 — 전체 보기</div>
  <ol start="{start+1}"> …현재 글은 <li class="current" aria-current="page"><span>제목</span></li>, 나머지는 링크… </ol>
  [남으면] <div class="series-more">↓ 뒤의 N편 — 전체 보기</div>
</details>
```
- 기본 접힘(summary에 시리즈명+진행 위치가 이미 노출). limit=20, window=±7, 경계 클램프.

### 3. `layouts/partials/related_posts.html` (신규)
- `site.RegularPages.Related . | first 4` — 제목 + 날짜 + 첫 태그를 카드 리스트로. 자기 자신 자동 제외.

### 4. `hugo.toml`
- `[related]` 블록 추가: includeNewer=true, toLower=true, threshold=30, indices = tags(100)/categories(40)/date(10). series 제외 주석 명시.
- SEO 보완: `[params.schema] publisherType = "person"` (개인 블로그인데 기본값 Organization), `[params] images = ["apple-touch-icon.png"]` — 커버 없는 글의 og:image 폴백(임시, 추후 1200×630 전용 이미지 제작 권장으로 릴리즈 노트에 기록).

### 5. `layouts/partials/extend_head.html`
- 기존 `<style>` 블록 끝에 `.series-box`, `.series-more`, `.related-posts` CSS 추가. PaperMod CSS 변수(--entry/--border/--primary/--secondary/--radius)만 사용해 다크모드 자동 대응, 강조색 #ff7a18 기존 관례 유지.

### 6. 문서 (전역 Plan 규칙)
- `documents/tasks/main/series-nav-and-related-posts/`에 implementation-plan.md(이 계획 + 논의 기록) 저장 후 구현 시작.
- 구현 완료 후 feature-documentation.md, release-notes.md 작성. CHANGELOG + notice 공지 관례(v1.2.0)에 따라 버전 릴리즈.

## 구현 순서
1. documents/tasks 문서 생성 → 2. hugo.toml → 3. related_posts.html → 4. series_box.html → 5. post_nav_links.html → 6. CSS → 7. 검증 → 8. 문서·CHANGELOG·notice 마무리

## 검증
- `hugo --gc --minify` 빌드 성공 + 빌드 시간 변경 전후 비교 (수 초 이내 증가 허용).
- `hugo server`로 확인:
  - weekly 중간 글(앞뒤 더보기 둘 다), weekly 1편(앞 더보기 없음), weekly 최신 편(뒤 더보기 없음) — `<ol start>` 번호와 (i/N편) 일치
  - 20편 이하 시리즈(예: cs_alone 13편): 전체 목록, 더보기 없음
  - 시리즈 없는 글: 전역 nav 폴백 정상
  - 관련 글이 weekly로 도배되지 않는지, 다크/라이트 모드 스타일
- `public/posts/{weekly글}/index.html` 크기 스팟체크 (윈도우 효과).
- 커밋·푸시는 사용자 확인 후.
