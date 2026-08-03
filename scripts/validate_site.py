#!/usr/bin/env python3
"""Validate the generated Hugo site without third-party dependencies."""

from __future__ import annotations

import argparse
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import struct
from urllib.parse import unquote, urlparse


SITE_HOST = "importunate-dev.github.io"
MAX_SEARCH_INDEX_BYTES = 2_000_000
MAX_CATEGORY_PAGE_BYTES = 200_000
ALLOWED_CATEGORIES = {"log", "study", "project", "life", "notice"}


class AssetParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.references: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if tag == "a" and values.get("href"):
            self.references.append(values["href"] or "")
        elif tag in {"img", "script"} and values.get("src"):
            self.references.append(values["src"] or "")
        elif tag == "link" and values.get("href"):
            self.references.append(values["href"] or "")


def local_target(public: Path, current: Path, reference: str) -> Path | None:
    parsed = urlparse(reference)
    if parsed.scheme in {"mailto", "tel", "javascript", "data"}:
        return None
    if parsed.scheme in {"http", "https"} and parsed.netloc != SITE_HOST:
        return None

    raw_path = unquote(parsed.path)
    if not raw_path:
        return current
    if raw_path.startswith("/"):
        target = public / raw_path.lstrip("/")
    else:
        target = current.parent / raw_path

    if raw_path.endswith("/"):
        return target / "index.html"
    if target.suffix:
        return target
    if target.is_dir():
        return target / "index.html"
    return target


def png_dimensions(path: Path) -> tuple[int, int]:
    with path.open("rb") as image:
        signature = image.read(24)
    if signature[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(f"{path} is not a PNG")
    return struct.unpack(">II", signature[16:24])


def parse_frontmatter(path: Path) -> dict[str, object]:
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    try:
        end = lines.index("---", 1)
    except ValueError:
        return {}

    values: dict[str, object] = {}
    active_list: str | None = None
    for line in lines[1:end]:
        if re.match(r"^[A-Za-z][A-Za-z0-9_]*:", line):
            key, raw = line.split(":", 1)
            raw = raw.strip().strip('"\'')
            values[key] = raw if raw else []
            active_list = key if not raw else None
        elif active_list and re.match(r"^\s+-\s+", line):
            item = re.sub(r"^\s+-\s+", "", line).split("#", 1)[0].strip().strip('"\'')
            assert isinstance(values[active_list], list)
            values[active_list].append(item)
    return values


def validate_content(repo: Path) -> list[str]:
    errors: list[str] = []
    posts = repo / "content" / "posts"
    for path in posts.rglob("*.md"):
        values = parse_frontmatter(path)
        relative = path.relative_to(repo)
        for key in ("title", "date", "description", "categories", "tags"):
            if not values.get(key):
                errors.append(f"{relative}: missing or empty {key}")
        date = values.get("date")
        if isinstance(date, str) and not re.fullmatch(r"\d{4}-\d{2}-\d{2}(?:T\d{2}:\d{2}:\d{2}[+-]\d{2}:\d{2})?", date):
            errors.append(f"{relative}: date must use YYYY-MM-DD or ISO 8601")
        categories = values.get("categories", [])
        if isinstance(categories, list):
            invalid = set(categories) - ALLOWED_CATEGORIES
            if invalid:
                errors.append(f"{relative}: invalid categories {sorted(invalid)}")
        if len(errors) >= 20:
            break
    return errors


def validate(public: Path, repo: Path) -> list[str]:
    errors: list[str] = validate_content(repo)
    index_path = public / "index.json"
    if not index_path.exists():
        errors.append("missing search index: index.json")
    else:
        if index_path.stat().st_size > MAX_SEARCH_INDEX_BYTES:
            errors.append(
                f"search index is {index_path.stat().st_size:,} bytes "
                f"(budget {MAX_SEARCH_INDEX_BYTES:,})"
            )
        try:
            records = json.loads(index_path.read_text(encoding="utf-8"))
            required = {"title", "description", "permalink", "date", "categories", "tags", "series"}
            for number, record in enumerate(records, 1):
                missing = required - record.keys()
                if missing:
                    errors.append(f"search record {number} is missing: {', '.join(sorted(missing))}")
                    break
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            errors.append(f"invalid search index: {exc}")

    for category in ("log", "study"):
        page = public / "categories" / category / "index.html"
        if page.exists() and page.stat().st_size > MAX_CATEGORY_PAGE_BYTES:
            errors.append(
                f"category {category} is {page.stat().st_size:,} bytes "
                f"(budget {MAX_CATEGORY_PAGE_BYTES:,})"
            )

    home = public / "index.html"
    if home.exists():
        html = home.read_text(encoding="utf-8")
        if "대표 프로젝트" not in html or "최근 글" not in html:
            errors.append("home page is missing featured or recent section headings")
        if "포트폴리오 보기" in html or "소개 보기" in html:
            errors.append("home page still contains redundant intro action buttons")
        if "og-default.png" not in html:
            errors.append("home page does not use og-default.png")
        if ".post-new{" in html:
            errors.append("custom CSS is still duplicated inline")

    og_image = public / "og-default.png"
    if not og_image.exists():
        errors.append("missing og-default.png")
    else:
        try:
            if png_dimensions(og_image) != (1200, 630):
                errors.append(f"og-default.png must be 1200x630, got {png_dimensions(og_image)}")
        except ValueError as exc:
            errors.append(str(exc))

    tag_root = public / "tags" / "index.html"
    if tag_root.exists() and not re.search(r'<meta name=robots content="?noindex', tag_root.read_text(encoding="utf-8")):
        errors.append("tag index is not marked noindex")
    tag_term = next(
        (path for path in (public / "tags").glob("*/index.html") if path.parent.name != "page"),
        None,
    )
    if tag_term and not re.search(r'<meta name=robots content="?noindex', tag_term.read_text(encoding="utf-8")):
        errors.append(f"tag term is not marked noindex: {tag_term.parent.name}")

    sitemap = public / "sitemap.xml"
    if sitemap.exists() and re.search(r"<loc>[^<]*/tags/", sitemap.read_text(encoding="utf-8")):
        errors.append("tag pages leaked into sitemap.xml")

    broken: list[str] = []
    for html_path in public.rglob("*.html"):
        parser = AssetParser()
        try:
            parser.feed(html_path.read_text(encoding="utf-8"))
        except UnicodeDecodeError:
            errors.append(f"invalid UTF-8 HTML: {html_path.relative_to(public)}")
            continue
        for reference in parser.references:
            target = local_target(public, html_path, reference)
            if target is not None and not target.exists():
                broken.append(
                    f"{html_path.relative_to(public)} -> {reference}"
                )
                if len(broken) >= 20:
                    break
        if len(broken) >= 20:
            break
    if broken:
        errors.append("broken local references (first 20):\n  " + "\n  ".join(broken))

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--public", type=Path, default=Path("public"))
    parser.add_argument("--repo", type=Path, default=Path("."))
    args = parser.parse_args()
    errors = validate(args.public.resolve(), args.repo.resolve())
    if errors:
        print("Site validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Site validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
