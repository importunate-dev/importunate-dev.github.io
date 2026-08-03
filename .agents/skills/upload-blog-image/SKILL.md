---
name: upload-blog-image
description: 블로그용 이미지를 별도 blog-images 저장소로 옮기고 커밋·푸시한 뒤 jsDelivr CDN URL을 본문에 적용한다. "이미지 올려줘", "이미지를 블로그에 넣어줘", "CDN 경로 줘" 같은 요청에 사용한다.
---

# Codex adapter: upload-blog-image

이 파일은 Codex용 진입점이다. 실제 워크플로의 단일 원본은 다음 파일이다.

`../../../.claude/skills/upload-blog-image/SKILL.md`

이 스킬을 사용하면 작업을 시작하기 전에 위 파일을 처음부터 끝까지 읽고 저장소 지침으로 준수한다.

이미지는 블로그 본문 저장소의 `static/`에 추가하지 않는다. `/Users/junsu/Documents/codespace/project/blog-images`에 저장하고 해당 저장소에서 별도로 커밋·푸시한 뒤 jsDelivr URL을 사용한다.
