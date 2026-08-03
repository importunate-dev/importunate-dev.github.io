# importunate-dev.github.io

샐러드랩 백엔드 개발자 **배준수**의 기술 블로그. Hugo + [PaperMod](https://github.com/adityatelange/hugo-PaperMod) 기반 정적 사이트이며 GitHub Pages로 배포된다.

- 🔗 사이트: https://importunate-dev.github.io/
- 📝 변경 이력: [CHANGELOG.md](./CHANGELOG.md)

## 로컬 실행

```bash
git clone --recurse-submodules <repo>   # 테마가 서브모듈이라 recursive 필요
hugo server -D                           # 로컬 미리보기 (드래프트 포함)
hugo --gc --minify                       # 프로덕션 빌드 → ./public
```

Hugo **extended** 필요. CI/로컬 모두 `0.162.1` 기준.

## 콘텐츠 구조

```
content/posts/{category}/{series}/YYYY-MM-DD-slug.md
```

- **category**: `log` · `study` · `project` · `life` · `notice`
- **series**: 카테고리 내 시리즈 (없으면 category 폴더 직속)
- 폴더 위치와 무관하게 URL은 `/posts/{파일명}/`로 고정된다 (`[permalinks]` 설정). 파일명(basename)만 유지하면 폴더를 옮겨도 URL이 바뀌지 않는다.
- 새 글은 `hugo new posts/{category}/{series}/YYYY-MM-DD-slug.md` 또는 기존 글 복사로 작성. frontmatter 형식은 [archetypes/default.md](./archetypes/default.md) 참고.

### 태그 작성 원칙

- 태그는 다른 글과 연결할 수 있는 재사용 가능한 주제만 3~5개 사용한다.
- 알고리즘 문제 번호, 날짜, 글 제목의 일부처럼 한 번만 쓰이는 값은 태그로 만들지 않는다.
- 표기가 갈리는 동의어는 기존 태그를 우선한다. 예: `환경 변수`와 `환경변수`를 함께 만들지 않는다.
- 세부 연재 구분은 `series`, 큰 주제 구분은 `categories`를 사용한다.

## 이미지

이미지는 별도 저장소 [`importunate-dev/blog-images`](https://github.com/importunate-dev/blog-images)에 두고 jsdelivr CDN URL로 참조한다.

```
https://cdn.jsdelivr.net/gh/importunate-dev/blog-images/{카테고리}/{파일명}
```

여러 이미지를 사용하는 새 글은 게시글 단위로 디렉터리를 분리한다.

```
{카테고리}/{시리즈}/{YYYY-MM-DD}/{의미-있는-파일명}.{확장자}
```

예: `project/godot/2026-08-02/stock-price.gif`. 시리즈 전체에서 `1.gif`, `2.gif`처럼 전역 순번을 이어 붙이지 않는다.

레이아웃 이동을 줄이기 위해 새 이미지에는 원본의 `width`와 `height`를 함께 기록한다. Markdown 이미지에는 Goldmark 속성을 사용할 수 있다.

```markdown
![주문 처리 흐름](https://cdn.jsdelivr.net/gh/importunate-dev/blog-images/project/example.png){width=1200 height=675}
```

본문용 이미지는 가능하면 WebP 또는 AVIF를 함께 생성하고, 움직임이 필요할 때만 GIF를 사용한다. HTML `<img>`를 직접 쓰면 공통 lazy loading 렌더 훅을 우회하므로 Markdown 이미지 문법을 우선한다.

## 배포

`main` 브랜치 push 시 `.github/workflows/hugo.yml`가 자동 빌드·배포한다.

## 버전 관리

릴리즈마다 [CHANGELOG.md](./CHANGELOG.md)를 갱신하고 `content/posts/notice/`에 공지 글을 추가한다. SemVer를 따른다.
