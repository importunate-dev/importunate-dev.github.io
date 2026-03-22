# 블로그 개선 계획서

> 작성일: 2026-03-22
> 대상: https://importunate-dev.github.io (Jekyll + GitHub Pages)

---

## 🚨 Phase 1: 긴급 수정 (Sitemap + 치명적 버그)

Google Search Console에서 sitemap.xml을 "가져올 수 없음" 상태인 문제를 해결합니다.

### 1-1. CNAME 파일 수정 (핵심 원인)

**현재 문제:**
- `CNAME` 파일에 원본 테마 제작자의 도메인 `huangxuan.me`가 들어있음
- GitHub Pages는 CNAME 파일을 보고 커스텀 도메인으로 리다이렉트를 시도함
- Google 봇이 `https://importunate-dev.github.io/sitemap.xml`을 요청하면, GitHub Pages가 `huangxuan.me`로 리다이렉트 → 실패
- **이것이 sitemap을 가져올 수 없는 근본 원인일 가능성이 매우 높음**

**해결 방법:**
- 커스텀 도메인을 사용하지 않는다면: `CNAME` 파일 삭제
- 커스텀 도메인을 사용한다면: 본인 소유 도메인으로 내용 변경

**파일:** `CNAME`
```
# 현재 (잘못됨)
huangxuan.me

# 수정 → 파일 자체를 삭제하거나, 본인 도메인으로 변경
```

### 1-2. sitemap.xml 품질 개선

**현재 문제:**
- 총 845개 URL 포함 — 그 중 73개가 페이지네이션 URL (`/page2/` ~ `/page74/`)
- 페이지네이션 URL은 SEO 가치가 낮고, 구글이 "크롤링 예산 낭비"로 판단할 수 있음
- `google4cb727437fad26da.html` (구글 인증 파일)도 sitemap에 포함되어 있음
- 104개 URL에 `<lastmod>` 태그 누락

**해결 방법:**
1. `_config.yml`의 `exclude`에 페이지네이션 관련 파일 제외 설정 추가
2. 또는 커스텀 `sitemap.xml`을 직접 작성하여 jekyll-sitemap 플러그인 출력을 오버라이드
3. `google4cb727437fad26da.html`을 exclude에 추가

**수정 예시 (`_config.yml`):**
```yaml
defaults:
  - scope:
      path: "google4cb727437fad26da.html"
    values:
      sitemap: false
```

### 1-3. robots.txt 확인

**현재 상태:** 올바르게 설정되어 있음 — 수정 불필요
```
User-agent: *
Allow: /
Sitemap: https://importunate-dev.github.io/sitemap.xml
```

---

## 🔧 Phase 2: SEO 강화

### 2-1. Twitter Card 메타 태그 추가

**현재 문제:** Open Graph 태그는 있지만 Twitter Card 태그가 없음
**영향:** Twitter/X에서 블로그 링크 공유 시 미리보기가 제대로 표시되지 않음

**수정 파일:** `_includes/head.html`
```html
<!-- Twitter Card -->
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{{ page.title }}">
<meta name="twitter:description" content="{{ page.excerpt | strip_html | truncate: 200 }}">
<meta name="twitter:image" content="{{ page.header-img | default: site.sidebar-avatar }}">
```

### 2-2. 포스트별 OG 이미지 개선

**현재 문제:** 모든 포스트의 `og:image`가 사이드바 아바타(프로필 사진)로 설정됨
**영향:** SNS 공유 시 모든 글의 썸네일이 동일하여 클릭률 저하

**해결 방법:**
- `og:image`를 포스트의 `header-img`로 우선 사용하도록 변경
- front matter에 `og-image` 필드를 추가하여 포스트별 커스텀 이미지 지원

### 2-3. SEO Title 개선

**현재 문제:** `SEOTitle`이 "Importunate"로만 설정 — 검색 결과에서 블로그 내용을 유추하기 어려움
**해결:** `SEOTitle`을 "Importunate | 백엔드 개발 블로그" 같은 형태로 변경

### 2-4. meta description 동적 개선

**현재 상태:** `site.description` 하나로 모든 페이지에 동일한 description 사용
**해결:** 포스트에서는 `post.excerpt` 또는 `post.subtitle`을 우선 사용하도록 변경 (이미 OG에는 적용되어 있지만, `<meta name="description">`에도 적용 필요)

---

## ⚡ Phase 3: 성능 최적화

### 3-1. jQuery 중복 로딩 제거

**현재 문제:** jQuery가 `head.html`과 `footer.html`에서 **2번** 로딩됨
- head.html: `<script src="jquery.min.js"></script>` (렌더 블로킹)
- footer.html: `<script defer src="jquery.min.js"></script>`

**해결:** head.html에서의 jQuery 로딩을 제거하고, footer.html의 defer 로딩만 유지
- 단, 인라인 스크립트에서 jQuery를 사용하는 부분이 있는지 확인 필요

### 3-2. CDN 리소스 프리커넥트 추가

**현재 문제:** Google Fonts에만 `preconnect` 적용됨

**추가할 것 (`head.html`):**
```html
<link rel="dns-prefetch" href="https://cdnjs.cloudflare.com">
<link rel="dns-prefetch" href="https://cdn.jsdelivr.net">
<link rel="preconnect" href="https://cdn.jsdelivr.net" crossorigin>
```

### 3-3. 불필요한 페이지네이션 제거

**현재 문제:** `_config.yml`에 `paginate: 10`으로 설정되어 있지만, `index.html`에서 자체 JS 페이지네이션(5개씩)을 사용하고 있음

**영향:**
- Jekyll이 74개의 페이지네이션 HTML 파일을 생성 (`/page2/` ~ `/page74/`)
- 이 파일들은 실제로 사용되지 않지만 sitemap에 포함됨
- 빌드 시간 증가 + sitemap 오염

**해결:** `_config.yml`에서 `paginate` 설정을 제거하거나, JS 페이지네이션 대신 Jekyll 페이지네이션을 사용하도록 통일

---

## 🎨 Phase 4: UX/접근성 개선

### 4-1. Skip-to-Content 링크 추가

**현재 문제:** 키보드 사용자를 위한 "본문으로 건너뛰기" 링크가 없음

**수정 파일:** `_layouts/default.html`
```html
<body>
  <a href="#main-content" class="skip-link">본문으로 건너뛰기</a>
  ...
```

### 4-2. ARIA 레이블 보강

**현재 문제:** 네비게이션, 검색 등에 ARIA 레이블이 거의 없음

**주요 수정 대상:**
- `<nav>` 에 `aria-label="메인 네비게이션"` 추가
- 검색 입력에 `aria-label="블로그 검색"` 추가
- 페이지네이션 버튼에 `aria-label` 추가

### 4-3. 다크 모드 (선택사항)

**현재 문제:** 다크 모드 미지원
**영향:** 야간 사용자 경험 저하, 최신 트렌드 미반영

**구현 방법:**
- CSS 변수 기반 테마 시스템 도입
- `prefers-color-scheme` 미디어 쿼리 활용
- 토글 버튼 + localStorage로 사용자 선호도 저장

---

## 🔒 Phase 5: 보안 및 기타

### 5-1. 외부 스크립트 SRI(Subresource Integrity) 추가

**현재 문제:** CDN에서 불러오는 jQuery, Bootstrap 등에 integrity 속성 없음
**영향:** CDN이 해킹당할 경우 악성 코드가 주입될 수 있음

```html
<!-- 예시 -->
<script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.x/jquery.min.js"
        integrity="sha384-..."
        crossorigin="anonymous"></script>
```

### 5-2. Disqus → Giscus 마이그레이션 고려

**이유:**
- Disqus는 무거움 (수십 개의 외부 요청 발생)
- 광고 삽입됨 (무료 플랜)
- Giscus는 GitHub Discussions 기반으로 개발 블로그에 적합
- 가볍고 광고 없음

### 5-3. Service Worker 호스트네임 정리

**현재 문제:** `sw.js`의 `HOSTNAME_WHITELIST`에 원본 테마 제작자의 도메인이 포함됨
```js
// 현재
["self.location.hostname", "huangxuan.me", "yanshuo.io", ...]

// 수정 → 불필요한 도메인 제거
["self.location.hostname", "cdnjs.cloudflare.com", "cdn.jsdelivr.net"]
```

---

## 📋 실행 우선순위 로드맵

| 순서 | 작업 | 긴급도 | 난이도 | 예상 시간 |
|------|------|--------|--------|-----------|
| **1** | CNAME 파일 삭제/수정 | 🔴 긴급 | 쉬움 | 1분 |
| **2** | sitemap에서 페이지네이션 URL 제외 | 🔴 긴급 | 보통 | 30분 |
| **3** | Google Search Console에서 sitemap 재제출 | 🔴 긴급 | 쉬움 | 5분 |
| **4** | jQuery 중복 로딩 제거 | 🟡 중요 | 보통 | 15분 |
| **5** | Twitter Card 메타 태그 추가 | 🟡 중요 | 쉬움 | 10분 |
| **6** | meta description 동적 적용 | 🟡 중요 | 쉬움 | 10분 |
| **7** | SEOTitle 개선 | 🟡 중요 | 쉬움 | 1분 |
| **8** | CDN preconnect 추가 | 🟢 보통 | 쉬움 | 5분 |
| **9** | Skip-to-content + ARIA | 🟢 보통 | 보통 | 20분 |
| **10** | SW 호스트네임 정리 | 🟢 보통 | 쉬움 | 5분 |
| **11** | SRI 해시 추가 | 🟢 보통 | 보통 | 20분 |
| **12** | Giscus 마이그레이션 | 🔵 장기 | 어려움 | 1~2시간 |
| **13** | 다크 모드 | 🔵 장기 | 어려움 | 3~5시간 |

---

## 핵심 요약

sitemap을 구글이 가져올 수 없는 **근본 원인은 `CNAME` 파일**입니다. 이 파일에 원본 테마 제작자의 도메인(`huangxuan.me`)이 들어있어서 GitHub Pages가 잘못된 도메인으로 리다이렉트를 시도합니다. 이 파일을 삭제하면 sitemap 문제가 즉시 해결될 가능성이 높습니다.

그 외에 sitemap 품질 개선(불필요한 페이지네이션 URL 74개 제거), jQuery 이중 로딩 수정, Twitter Card 추가 등을 순차적으로 진행하면 블로그의 SEO와 성능이 크게 향상됩니다.
