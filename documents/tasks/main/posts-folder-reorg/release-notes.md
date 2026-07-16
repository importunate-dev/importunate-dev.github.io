# 릴리즈 노트 — v1.0.0 (2026-07-16)

블로그 사용성 개선 + 콘텐츠 구조 정리 릴리즈. 이번 릴리즈부터 `CHANGELOG.md`로 버전을 관리한다.

## ✨ 사용자에게 보이는 변경 (UI/UX)
- **최근 글 N 뱃지**: 최근 7일 내 올라온 글 제목 옆에 주황색 `N` 표시(홈·목록).
- **메뉴 N 뱃지**: 최근 글이 있는 카테고리 메뉴 옆에 작은 `N` 표시.
- **시리즈 필터**: 카테고리 페이지(공부/로그/프로젝트/일상)에서 시리즈별로 글을 필터링하는 버튼 바 추가.
- **이미지 크게 보기**: 본문 이미지를 클릭하면 원본을 새 창에서 크게 볼 수 있음.
- **목차 커서 개선**: 목차 링크에 hover 시 손가락(pointer) 커서.
- **메뉴 순서 변경**: `홈 → 소개 → 공부 → 로그 → …`.

## 🗂 콘텐츠/구조 변경
- **게임 개발 글 분류 정정**: `study` → `project`.
- **posts 폴더 2단계 재구성**: 749개 글을 `posts/{category}/{series}/`로 재배치. `[permalinks]`로 **URL 100% 유지**(색인·외부 링크 영향 없음).

## 🔧 내부
- `hugo.toml`: `recentDays = 7` 파라미터, `[permalinks] posts = "/posts/:contentbasename/"` 추가.
- 오버라이드: `layouts/_default/list.html`, `layouts/partials/header.html`, `layouts/_default/_markup/render-image.html`, `layouts/partials/extend_head.html`, `layouts/partials/extend_footer.html`.

## ✅ 검증
- 빌드 에러 0.
- 재구성 전/후 URL diff = 0 (사라진 URL 0, 추가 URL 0).
- 749개 파일 git rename 추적(이력 보존).

## 📌 후속 후보 (개선 조사 결과, 별도 진행)
- 검색 인덱스 `index.json` 5.7MB 경량화(High)
- CI Hugo 버전(0.147.1) ↔ 로컬(0.162.1) 정렬(Med)
- 카테고리 페이지 대량 DOM(log 318/study 293) 부분 렌더(Med)
- 원격 이미지 width/height로 CLS 개선(Med)
- thin/중복 meta description 개선(Med), `jungle`(76)·`notice` 메뉴 노출 결정(Med)
- 글 Article 구조화 데이터/기본 OG 이미지(SEO)
