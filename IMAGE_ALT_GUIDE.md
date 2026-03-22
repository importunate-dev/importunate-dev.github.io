# 이미지 Alt 텍스트 가이드

## 개요
접근성과 SEO를 위해 모든 이미지에 의미 있는 alt 텍스트를 추가해야 합니다.

## 가이드라인

### 1. 의미 있는 이미지
- 이미지가 콘텐츠의 일부인 경우, 이미지의 내용을 설명하는 alt 텍스트를 작성합니다.
- 예: `![데이터베이스 ER 다이어그램](path/to/image.webp)`

### 2. 장식용 이미지
- 단순히 장식 목적의 이미지는 빈 alt를 사용합니다.
- 예: `![](path/to/decoration.webp)` 또는 `alt=""`

### 3. 텍스트가 포함된 이미지
- 이미지에 텍스트가 있는 경우, 그 텍스트를 alt에 포함합니다.
- 예: `![에러 메시지: Connection timeout](path/to/error.webp)`

### 4. 다이어그램/차트
- 다이어그램이나 차트의 경우, 주요 내용을 요약하여 설명합니다.
- 예: `![2024년 월별 방문자 수 추이 그래프](path/to/chart.webp)`

## 마크다운 작성 예시

```markdown
<!-- 좋은 예 -->
![ElastiCache 서버리스 연결 설정 화면](https://cdn.jsdelivr.net/gh/importunate-dev/importunate-dev.github.io/img/log/2025/01/23/1.webp)

<!-- 나쁜 예 -->
![1](https://cdn.jsdelivr.net/gh/importunate-dev/importunate-dev.github.io/img/log/2025/01/23/1.webp)
```

## 자동 처리
- `image-optimization.js` 스크립트가 alt 속성이 없는 이미지에 기본값을 추가합니다.
- 하지만 가능한 한 마크다운 작성 시 명시적으로 alt 텍스트를 작성하는 것을 권장합니다.

## 참고 자료
- [WebAIM: Alternative Text](https://webaim.org/techniques/alttext/)
- [MDN: Images in HTML](https://developer.mozilla.org/en-US/docs/Learn/HTML/Multimedia_and_embedding/Images_in_HTML)
