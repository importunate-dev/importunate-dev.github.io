# Repository Instructions

## Global Behavior

- Respond primarily in Korean unless the user asks for another language.
- Keep responses concise, direct, and implementation-focused.

## Plan-Mode Documentation Rule

When the workflow explicitly enters a planning phase for repository work, persist planning artifacts under:

`documents/tasks/{current-branch}/{topic}/`

Use these filenames when applicable:

- `implementation-plan.md`
- `feature-documentation.md`
- `release-notes.md`
- `api-changes.md` for API changes only

Do not leave the plan only in chat. Include user questions, key tradeoffs, and final decisions. Use the current Git branch name as directory segments as-is.

## Alpha-Claude Skill Restriction

When this repository is under `/Users/junsu/Documents/codespace/project/`, do not invoke, read, or use skills from `/Users/junsu/workspace/claude/Alpha-Claude/skills/` (including all `sk-*` skills). Use native Codex capabilities or repository-local/non-Alpha-Claude skills instead.

## Repository-Local Workflow Rules

- `.claude/skills/` contains the canonical workflow documentation shared with Claude Code.
- Codex adapters live under `.agents/skills/`. When an adapter applies, read its referenced canonical `.claude` skill completely before taking action and follow it as repository instructions.
- Do not edit the Codex adapter and canonical workflow independently. Update the canonical `.claude` skill first; adapters should continue pointing to it.

## Blog Publishing — Mandatory

For requests such as “게시글 작성해줘”, “초안 발행해줘”, “오늘 게시글로 만들어”, or equivalent publishing requests:

1. Use the repository-local `publish-blog-post` skill.
2. Read the same series' immediately previous Hugo post and Velog preview before editing.
3. Treat the following as one publishing bundle:
   - `content/posts/.../YYYY-MM-DD-slug.md`
   - `velog/YYYY-MM-DD-slug-preview.md`
   - images in `/Users/junsu/Documents/codespace/project/blog-images/...` when applicable
4. `velog/` is ignored by Git. Never use `git status`, `git diff`, or a successful Hugo build as evidence that the preview exists. Verify the expected preview path explicitly.
5. Images must not be added under this repository's `static/` directory. Follow the `upload-blog-image` workflow and use jsDelivr CDN URLs.
6. Before reporting completion, verify every required artifact explicitly. For a post with images, confirm:
   - Hugo post exists with correct front matter and date.
   - Velog preview exists, links to the final post URL, and contains one representative image.
   - Image files exist in `blog-images` and the Hugo/Velog Markdown references the intended CDN URLs.
   - Hugo production build succeeds.
7. The Velog preview is a local publishing artifact and remains excluded from the blog repository commit unless the repository policy changes.
