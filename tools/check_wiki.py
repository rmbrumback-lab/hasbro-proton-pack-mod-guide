"""Check the wiki page and build the verification checklist.

Usage:  python tools/check_wiki.py

Checks (exits non-zero on any failure):
  * every footnote used in the text has a definition, and every definition is used
  * every post footnote [^pN] links to post N of the source thread
  * no Markdown tables (the GBFans wiki editor doesn't support them)
  * every IMG: image exists under docs/, at most 30 images, no third-party images

Also writes build/wiki/page_github.md (images pointing at GitHub, for preview) and
build/wiki/upload_list.txt (the images to upload to the wiki page).

Writes docs/VERIFICATION.md: one checklist section per cited post, listing every
sentence on the page that cites it, so each claim can be checked against the
original post. Existing ticks ([x]) and notes are preserved on regeneration.
"""
from __future__ import annotations

import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGE = ROOT / "docs" / "wiki" / "hasbro-1984-proton-pack.md"
CHECKLIST = ROOT / "docs" / "VERIFICATION.md"
THREAD = "https://forum.gbfans.com/t/hasbro-1984-proton-pack-big-overhaul-and-customisation/219236"
RAW = "https://raw.githubusercontent.com/rmbrumback-lab/hasbro-1984-proton-pack-blueprint/main"

DEF_RE = re.compile(r"^\[\^([\w-]+)\]:\s*(.+)$", re.M)
USE_RE = re.compile(r"\[\^([\w-]+)\](?!:)")


def split_page(text: str) -> tuple[str, str]:
    marker = "\n## References"
    if marker not in text:
        sys.exit("FAIL: page has no '## References' section")
    body, refs = text.split(marker, 1)
    return body, refs


def sentences_citing(body: str) -> dict[str, list[str]]:
    """Map footnote id -> the paragraphs or list items in the body that cite it.

    The whole paragraph or list item is used, because a footnote often supports
    more than the single sentence it follows.
    """
    cites: dict[str, list[str]] = defaultdict(list)
    for line in body.splitlines():
        ids = USE_RE.findall(line)
        if not ids:
            continue
        clean = USE_RE.sub("", line).strip()
        clean = re.sub(r"^(-|\d+\.)\s+", "", clean)
        for fid in dict.fromkeys(ids):
            if clean not in cites[fid]:
                cites[fid].append(clean)
    return cites


def load_ticks() -> dict[str, list[str]]:
    """Preserve per-post status lines from an existing checklist."""
    if not CHECKLIST.exists():
        return {}
    keep: dict[str, list[str]] = {}
    current = None
    for line in CHECKLIST.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^### Post #(\d+)", line)
        if m:
            current = m.group(1)
            keep[current] = []
            continue
        if current and (line.startswith("- [x]") or line.startswith("- Note:")):
            keep[current].append(line)
    return keep


def main() -> int:
    text = PAGE.read_text(encoding="utf-8")
    body, refs = split_page(text)
    errors: list[str] = []

    defs = dict(DEF_RE.findall(refs))
    used = set(USE_RE.findall(body))

    for fid in sorted(used - defs.keys()):
        errors.append(f"footnote [^{fid}] used but not defined")
    for fid in sorted(defs.keys() - used):
        errors.append(f"footnote [^{fid}] defined but never used")

    for fid, ref in defs.items():
        m = re.fullmatch(r"p(\d+)", fid)
        if not m:
            continue
        n = m.group(1)
        if f"{THREAD}/{n})" not in ref:
            errors.append(f"[^{fid}] does not link to post #{n} of the source thread")
        if not re.search(rf"\[post #{n}\]", ref):
            errors.append(f"[^{fid}] link text should read 'post #{n}'")

    for i, line in enumerate(text.splitlines(), 1):
        if re.match(r"^\s*\|.*\|\s*$", line):
            errors.append(f"line {i}: Markdown table (not supported by the wiki editor)")

    # images: IMG:<path under docs/> must exist; wiki allows at most 30 per page
    images = re.findall(r"!\[[^\]]*\]\(IMG:([^)]+)\)", text)
    for rel in images:
        if not (ROOT / "docs" / rel).exists():
            errors.append(f"image IMG:{rel} not found under docs/")
    if len(images) > 30:
        errors.append(f"{len(images)} images; the wiki allows at most 30 per page")
    if re.search(r"!\[[^\]]*\]\((?!IMG:)", text):
        errors.append("image without the IMG: prefix (use our own renderings via IMG:)")

    # preview build: IMG: -> GitHub raw URLs
    build = ROOT / "build" / "wiki"
    build.mkdir(parents=True, exist_ok=True)
    preview = re.sub(r"\]\(IMG:([^)]+)\)", lambda m: f"]({RAW}/docs/{m.group(1)})", text)
    (build / "page_github.md").write_text(preview, encoding="utf-8")
    (build / "upload_list.txt").write_text("\n".join(f"docs/{r}" for r in images) + "\n", encoding="utf-8")

    # build the checklist
    cites = sentences_citing(body)
    ticks = load_ticks()
    posts = sorted((int(f[1:]) for f in used if re.fullmatch(r"p\d+", f)))
    out = [
        "# Verification checklist",
        "",
        "Generated by `tools/check_wiki.py` from the wiki page. Each section lists every",
        "statement on the page that cites one post. Open the post, confirm each statement",
        "matches it (numbers, sizes, part names, who said it), then change the post's",
        "`- [ ] Verified` line to `- [x] Verified` and add a `- Note:` line for anything",
        "corrected. Ticks and notes survive regeneration.",
        "",
        "The first draft was compiled from summaries of the thread, so **every** item",
        "needs checking against the original post before the page is published.",
        "",
        f"Cited posts: {len(posts)}. Verified: "
        f"{sum(1 for p in posts if any(l.startswith('- [x]') for l in ticks.get(str(p), [])))}.",
        "",
    ]
    for p in posts:
        fid = f"p{p}"
        author_date = re.sub(r"\[post #\d+\]\([^)]*\)", f"post #{p}", defs.get(fid, ""))
        out.append(f"### Post #{p}")
        out.append("")
        out.append(f"[{author_date}]({THREAD}/{p})")
        out.append("")
        prior = ticks.get(str(p), [])
        if any(l.startswith("- [x]") for l in prior):
            out.extend(l for l in prior if l.startswith("- [x]"))
        else:
            out.append("- [ ] Verified")
        out.extend(l for l in prior if l.startswith("- Note:"))
        out.append("")
        for s in cites.get(fid, []):
            out.append(f"> {s}")
            out.append(">")
        if out[-1] == ">":
            out.pop()
        out.append("")
    CHECKLIST.write_text("\n".join(out).rstrip() + "\n", encoding="utf-8")

    words = len(re.sub(r"\[\^[\w-]+\]", "", body).split())
    print(f"page: {words} words, {len(used)} footnotes, {len(posts)} posts cited")
    print(f"wrote {CHECKLIST.relative_to(ROOT)}")
    if errors:
        print("\nFAIL:")
        for e in errors:
            print("  -", e)
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
