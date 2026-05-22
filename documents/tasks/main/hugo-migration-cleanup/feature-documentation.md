# 기능 문서: Hugo + PaperMod 블로그 (마이그레이션 후 최종 상태)

> 본 문서는 Jekyll → Hugo 마이그레이션 완료 + 정리 작업 이후의 블로그 최종 구조와 운영 가이드를 기술한다.

## 사이트 개요

- URL: https://importunate-dev.github.io
- 정적 사이트 생성기: Hugo (extended) v0.147.1
- 테마: [PaperMod](https://github.com/adityatelange/hugo-PaperMod) (git submodule)
- 호스팅: GitHub Pages (GitHub Actions workflow 배포)
- 게시글 수: 741개 (이전 Jekyll에서 완전 이관)

## 디렉토리 구조

```
importunate-dev.github.io/
├── .github/workflows/hugo.yml       # GitHub Actions 빌드/배포
├── archetypes/default.md            # 신규 게시글 템플릿
├── content/
│   ├── posts/                       # 게시글 741개 (플랫 구조)
│   ├── about/index.md               # 소개
│   ├── archives.md                  # 아카이브
│   └── search.md                    # 검색 페이지
├── layouts/partials/comments.html   # Giscus 댓글
├── static/
│   ├── ads.txt                      # AdSense
│   └── google4cb727437fad26da.html  # Google Search Console 검증
├── themes/PaperMod/                 # 테마 (submodule)
├── hugo.toml                        # Hugo 설정
└── documents/tasks/                 # 작업 문서
```

## 핵심 기능

### 1. URL aliases (Jekyll URL 호환)

- Jekyll URL 패턴: `/:categories/:title/` (예: `/study/developer240318/`)
- Hugo URL 패턴: `/posts/:filename/` (예: `/posts/2024-03-18-developer240318/`)
- 모든 게시글 front matter에 `aliases:` 추가하여 Jekyll URL로도 접근 시 자동 리다이렉트

예시 (`content/posts/2024-03-18-developer240318.md`):
```yaml
---
title: "..."
categories: ["study"]
aliases:
  - "/study/developer240318/"
---
```

### 2. Giscus 댓글 시스템

- 위치: `layouts/partials/comments.html`
- GitHub Discussions 기반, 다크모드 자동 대응
- 활성화 조건: `hugo.toml`의 `[params].comments = true`
- 설정:
  - repo: `importunate-dev/importunate-dev.github.io`
  - category: `Announcements`
  - mapping: `pathname`
  - theme: `preferred_color_scheme`
  - lang: `ko`

### 3. 이미지 CDN (blog-images 별도 저장소)

- 별도 저장소: https://github.com/importunate-dev/blog-images
- CDN URL: `https://cdn.jsdelivr.net/gh/importunate-dev/blog-images/[경로]`
- 사용 예: 게시글 내 `![img](https://cdn.jsdelivr.net/gh/importunate-dev/blog-images/developer/240318/240318_1.webp)`
- 장점: 메인 저장소 사이즈 경량화, jsDelivr CDN을 통한 글로벌 캐시

### 4. 다크모드

- PaperMod 내장 기능
- 기본값: `defaultTheme = "auto"` (시스템 설정 자동 감지)
- 토글 가능 (`disableThemeToggle = false`)

### 5. 검색

- PaperMod 내장 Fuse.js 기반 클라이언트 검색
- `content/search.md`로 활성화

### 6. SEO / 분석

- Google Search Console: `static/google4cb727437fad26da.html` 파일 검증
- 사이트맵: Hugo 자동 생성 `sitemap.xml`
- robots.txt: `enableRobotsTXT = true` (Hugo 자동)
- Google Analytics: GTM 스크립트 (gtag.js, ID `G-QZMSC32TSX`)

## 빌드 & 배포

### 자동 배포 (GitHub Actions)

`main` 브랜치에 push 시 `.github/workflows/hugo.yml`이 트리거:
1. Hugo extended v0.147.1 설치
2. submodule(`themes/PaperMod`) 포함 체크아웃
3. `hugo --gc --minify --baseURL ...` 빌드
4. GitHub Pages artifact 업로드 & 배포

### 로컬 개발

```bash
# 개발 서버
hugo server -D

# 빌드
hugo --gc --minify

# 새 게시글
hugo new content posts/YYYY-MM-DD-제목.md
```

## 브랜치 전략

- `main`: 현재 운영 브랜치 (default). Push 시 자동 빌드/배포
- `jekyll-backup`: Jekyll 시절 백업 (마지막 커밋 `eedfc6a`, 보존만 함)

## 마이그레이션 시 제거된 항목

- Jekyll 의존성 (Gemfile, _config.yml, _posts/, _layouts/, _includes/ 등)
- Decap CMS (`static/admin/`)
- Disqus 댓글
- simple-jekyll-search
- Hux Blog 테마

## 유지보수 가이드

### 게시글 작성

`content/posts/YYYY-MM-DD-slug.md` 형식으로 생성. front matter는 `archetypes/default.md` 참고.

### 이미지 추가

1. `../blog-images/` 저장소에 파일 추가
2. `git add . && git commit && git push`
3. 본문에서 `https://cdn.jsdelivr.net/gh/importunate-dev/blog-images/[경로]` 참조
4. jsDelivr 캐시 반영까지 수 분 소요

### 테마 업데이트

```bash
cd themes/PaperMod
git pull origin master
cd ../..
git add themes/PaperMod
git commit -m "Update PaperMod theme"
```

### Hugo 버전 업데이트

`.github/workflows/hugo.yml`의 `HUGO_VERSION` 환경변수 수정.

## 참고 외부 리소스

- Hugo 공식: https://gohugo.io/
- PaperMod 문서: https://github.com/adityatelange/hugo-PaperMod/wiki
- Giscus 설정: https://giscus.app
- jsDelivr 캐시: https://www.jsdelivr.com/documentation
