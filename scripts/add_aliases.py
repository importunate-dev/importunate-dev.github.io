#!/usr/bin/env python3
"""
Jekyll URL aliases를 Hugo 게시글 front matter에 추가하는 스크립트.
Jekyll permalink: /:categories/:title/
Hugo alias: /{category}/{slug}/
"""

import os
import re
import glob

POSTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "content", "posts")

# 파일명에서 slug 추출: 2024-03-18-developer240318.md -> developer240318
FILENAME_RE = re.compile(r"^\d{4}-\d{2}-\d{2}-(.+)\.md$")

# front matter에서 categories 추출
CATEGORY_RE = re.compile(r'^\s*-\s*"?([^"\n]+)"?\s*$')

def extract_slug(filename):
    m = FILENAME_RE.match(filename)
    return m.group(1) if m else None

def add_alias_to_post(filepath):
    filename = os.path.basename(filepath)
    slug = extract_slug(filename)
    if not slug:
        print(f"  SKIP (no slug): {filename}")
        return False

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # front matter 분리
    if not content.startswith("---"):
        print(f"  SKIP (no front matter): {filename}")
        return False

    parts = content.split("---", 2)
    if len(parts) < 3:
        print(f"  SKIP (malformed front matter): {filename}")
        return False

    front_matter = parts[1]
    body = parts[2]

    # 이미 aliases가 있으면 스킵
    if "aliases:" in front_matter:
        print(f"  SKIP (already has aliases): {filename}")
        return False

    # categories 추출
    category = None
    lines = front_matter.split("\n")
    in_categories = False
    for line in lines:
        if line.strip().startswith("categories:"):
            # 인라인 형식: categories: ["study"]
            inline = re.search(r'categories:\s*\[([^\]]+)\]', line)
            if inline:
                vals = inline.group(1).split(",")
                category = vals[0].strip().strip('"').strip("'")
                break
            in_categories = True
            continue
        if in_categories:
            m = CATEGORY_RE.match(line)
            if m:
                category = m.group(1).strip()
                break
            elif line.strip() and not line.startswith(" ") and not line.startswith("\t"):
                break  # categories 섹션 끝

    if not category:
        print(f"  SKIP (no category): {filename}")
        return False

    alias = f"/{category}/{slug}/"

    # front matter 끝(---) 직전에 aliases 삽입
    alias_block = f'aliases:\n  - "{alias}"'

    # front matter 끝에 줄바꿈 확인 후 삽입
    if front_matter.endswith("\n"):
        new_front_matter = front_matter + alias_block + "\n"
    else:
        new_front_matter = front_matter + "\n" + alias_block + "\n"

    new_content = "---" + new_front_matter + "---" + body

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(new_content)

    return True

def main():
    files = sorted(glob.glob(os.path.join(POSTS_DIR, "*.md")))
    print(f"Found {len(files)} posts in {POSTS_DIR}")

    success = 0
    skipped = 0
    for filepath in files:
        if add_alias_to_post(filepath):
            success += 1
        else:
            skipped += 1

    print(f"\nDone: {success} aliases added, {skipped} skipped")

if __name__ == "__main__":
    main()
