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

## 이미지

이미지는 별도 저장소 [`importunate-dev/blog-images`](https://github.com/importunate-dev/blog-images)에 두고 jsdelivr CDN URL로 참조한다.

```
https://cdn.jsdelivr.net/gh/importunate-dev/blog-images/{카테고리}/{파일명}
```

## 배포

`main` 브랜치 push 시 `.github/workflows/hugo.yml`가 자동 빌드·배포한다.

## 버전 관리

릴리즈마다 [CHANGELOG.md](./CHANGELOG.md)를 갱신하고 `content/posts/notice/`에 공지 글을 추가한다. SemVer를 따른다.
