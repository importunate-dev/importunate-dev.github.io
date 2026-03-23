# Jekyll → Hugo 마이그레이션 가이드

이 문서는 현재 Jekyll 블로그를 Hugo + PaperMod + GitHub Pages로 전환하는 방법을 설명합니다.

---

## 전제 조건

- Git이 설치되어 있어야 합니다
- GitHub CLI (`gh`) 설치 권장
- Hugo 설치: `brew install hugo` (Mac) 또는 `choco install hugo-extended` (Windows)

---

## Step 1: 이미지 분리 (blog-images 저장소 생성)

### 1-1. GitHub에서 새 저장소 생성

1. https://github.com/new 에서 `blog-images` 이름으로 저장소 생성 (Public)
2. README 없이 빈 저장소로 생성

### 1-2. 이미지 파일 복사 및 Push

```bash
# 현재 블로그 저장소의 img/ 폴더 복사
cp -r img/ ../blog-images/

# blog-images 저장소 초기화
cd ../blog-images
git init
git add .
git commit -m "Initial commit: migrate blog images"
git remote add origin https://github.com/importunate-dev/blog-images.git
git branch -M main
git push -u origin main
```

### 1-3. 확인

이미지가 아래 URL로 접근 가능한지 확인:
```
https://cdn.jsdelivr.net/gh/importunate-dev/blog-images/[파일경로]
```

참고: jsDelivr CDN 캐시가 반영되기까지 수 분 소요될 수 있습니다.

---

## Step 2: Hugo 프로젝트로 저장소 교체

### 2-1. 기존 저장소 백업

```bash
# 기존 Jekyll 저장소를 백업
cd ..
mv importunate-dev.github.io importunate-dev.github.io.bak
```

### 2-2. Hugo 프로젝트를 새 저장소로 설정

```bash
# hugo-migration 폴더를 새 저장소 루트로 사용
cp -r importunate-dev.github.io.bak/hugo-migration importunate-dev.github.io
cd importunate-dev.github.io

# Git 초기화
git init
git branch -M main

# PaperMod 테마를 submodule로 추가
rm -rf themes/PaperMod  # 복사된 폴더 삭제
git submodule add --depth=1 https://github.com/adityatelange/hugo-PaperMod.git themes/PaperMod

# public/ 폴더는 Git에 포함하지 않음
echo "public/" >> .gitignore
echo "resources/" >> .gitignore

# 불필요한 빌드 결과물 삭제
rm -rf public/ resources/

# 커밋
git add .
git commit -m "Migrate from Jekyll to Hugo + PaperMod"
```

### 2-3. GitHub 리모트 설정 및 Push

```bash
git remote add origin https://github.com/importunate-dev/importunate-dev.github.io.git
git push -u origin main --force
```

⚠️ `--force`를 사용하는 이유: 저장소 구조가 완전히 바뀌기 때문입니다.
기존 Jekyll 히스토리가 필요하다면 별도 브랜치(`jekyll-backup`)에 보존하세요.

---

## Step 3: GitHub Pages 설정 변경

### 3-1. GitHub Actions를 통한 배포로 전환

1. GitHub 저장소 → Settings → Pages로 이동
2. **Source**를 `Deploy from a branch`에서 `GitHub Actions`로 변경
3. `.github/workflows/hugo.yml`이 이미 포함되어 있으므로 push 시 자동 빌드/배포됨

### 3-2. 빌드 확인

Push 후 GitHub Actions 탭에서 빌드 상태 확인:
```
https://github.com/importunate-dev/importunate-dev.github.io/actions
```

---

## Step 4: Decap CMS 설정 (선택)

CMS를 사용하려면 GitHub OAuth App 설정이 필요합니다:

1. https://github.com/settings/applications/new 에서 OAuth App 생성
   - Application name: `Blog CMS`
   - Homepage URL: `https://importunate-dev.github.io`
   - Authorization callback URL: `https://importunate-dev.github.io/admin/`
2. `static/admin/config.yml`의 `backend` 섹션에 OAuth 설정 추가

또는 Netlify Identity를 사용할 수도 있습니다 (현재 기본 설정).

---

## Step 5: Google Search Console 재설정

1. Google Search Console에서 사이트맵 재제출: `sitemap.xml`
2. URL이 `/posts/` 접두사가 추가되었으므로, 기존 인덱스와 달라질 수 있음
   - Hugo의 aliases 기능으로 리다이렉트 설정 가능

---

## 로컬 개발

```bash
# 개발 서버 실행
hugo server -D

# 빌드
hugo --gc --minify

# 새 게시글 생성
hugo new content posts/2026-03-22-새글.md
```

---

## 주요 변경 사항

| 항목 | Jekyll (이전) | Hugo (이후) |
|------|:---:|:---:|
| 빌드 시간 | 수 분 | ~4초 |
| 게시글 위치 | `_posts/` (중첩 폴더) | `content/posts/` (플랫) |
| 이미지 위치 | 같은 저장소 `img/` | 별도 저장소 `blog-images` |
| 이미지 URL | 로컬 또는 jsdelivr/main repo | jsdelivr/blog-images |
| 테마 | Hux Blog | PaperMod (다크모드 내장) |
| 빌드/배포 | GitHub Pages 자동 | GitHub Actions → Pages |
| CMS | 없음 | Decap CMS (`/admin`) |
| 검색 | simple-jekyll-search | Fuse.js (PaperMod 내장) |
| 댓글 | Disqus | 미설정 (Giscus 추가 권장) |
| 다크모드 | 없음 | 내장 (auto/light/dark) |

---

## URL 구조 변경 대응

Jekyll의 URL: `/:category/:title/` (예: `/study/developer240318/`)
Hugo의 URL: `/posts/:filename/` (예: `/posts/2024-03-18-developer240318/`)

기존 URL의 SEO를 보존하려면 Hugo의 aliases를 활용할 수 있습니다.
각 게시글의 front matter에 추가:
```yaml
aliases:
  - /study/developer240318/
```

이 작업은 추후 스크립트로 일괄 처리할 수 있습니다.

---

## 디렉토리 구조

```
importunate-dev.github.io/
├── .github/workflows/hugo.yml   # GitHub Actions 빌드
├── archetypes/                   # 게시글 템플릿
├── content/
│   ├── posts/                    # 게시글 741개
│   ├── about/                    # 소개 페이지
│   ├── archives.md               # 아카이브
│   └── search.md                 # 검색
├── static/
│   ├── admin/                    # Decap CMS
│   ├── ads.txt                   # AdSense
│   └── google*.html              # Google 인증
├── themes/PaperMod/              # 테마 (git submodule)
├── hugo.toml                     # Hugo 설정
└── scripts/                      # 유틸리티 스크립트
```
