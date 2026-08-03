---
name: publish-blog-post
description: 초안이나 copy 파일을 오늘 날짜의 정식 Hugo 게시글로 발행한다. 이미지 CDN 업로드, Velog 프리뷰 생성, 검토, 빌드, 커밋·푸시를 포함한다. "게시글 작성해줘", "초안 발행해줘", "오늘 게시글로 만들어" 같은 요청에 사용한다.
---

# Codex adapter: publish-blog-post

이 파일은 Codex용 진입점이다. 실제 워크플로의 단일 원본은 다음 파일이다.

`../../../.claude/skills/publish-blog-post/SKILL.md`

이 스킬을 사용하면 작업을 시작하기 전에 위 파일을 처음부터 끝까지 읽고 저장소 지침으로 준수한다. 이미지가 포함되면 `.agents/skills/upload-blog-image/SKILL.md`도 사용한다.

특히 `velog/`는 Git에서 무시되므로 `git status`로 생성 여부를 판단하지 않는다. 최종 응답 전에 예상한 Hugo 게시글, Velog 프리뷰, 이미지 파일을 각각 명시적인 경로로 확인한다.
