"""Download reference material for measurement into sources/ (run by GitHub Actions).

Fetches:
  * the GBFans overhaul thread as JSON (verbatim post text) and every photo in it
  * Hasbro Pulse product images for the 1984 pack, at full resolution
  * the HasLab Spengler's Proton Pack manual (shared tooling)
Writes sources/manifest.json listing every file with its URL, size and sha256.
"""
import hashlib
import json
import re
import sys
import time
import urllib.request
from pathlib import Path

OUT = Path("sources")
UA = {"User-Agent": "Mozilla/5.0 (research fetch; rmbrumback-lab/hasbro-1984-proton-pack-blueprint)"}
manifest = []


def get(url, timeout=60):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read(), r.headers.get("Content-Type", "")


def save(url, path, note=""):
    path = OUT / path
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        data, ctype = get(url)
    except Exception as e:  # keep going; record the failure
        manifest.append({"url": url, "file": None, "error": str(e), "note": note})
        print("FAIL", url, e)
        return None
    path.write_bytes(data)
    manifest.append({"url": url, "file": str(path), "bytes": len(data), "type": ctype,
                     "sha256": hashlib.sha256(data).hexdigest(), "note": note})
    print("ok  ", len(data), url)
    time.sleep(0.4)
    return data


# 1. Thread JSON (Discourse print view returns all posts)
TID = 219236
data = save(f"https://forum.gbfans.com/t/{TID}.json?print=true", "forum/thread_219236.json", "thread JSON")
posts = []
if data:
    j = json.loads(data)
    posts = j.get("post_stream", {}).get("posts", [])
    stream = j.get("post_stream", {}).get("stream", [])
    have = {p["id"] for p in posts}
    missing = [i for i in stream if i not in have]
    for k in range(0, len(missing), 20):
        chunk = missing[k:k + 20]
        q = "&".join(f"post_ids[]={i}" for i in chunk)
        d = save(f"https://forum.gbfans.com/t/{TID}/posts.json?{q}", f"forum/posts_extra_{k}.json", "extra posts")
        if d:
            posts += json.loads(d).get("post_stream", {}).get("posts", [])
    posts.sort(key=lambda p: p["post_number"])
    (OUT / "forum" / "posts.json").write_text(json.dumps(
        [{"n": p["post_number"], "user": p["username"], "created": p["created_at"], "cooked": p["cooked"]}
         for p in posts], indent=1), encoding="utf-8")

# 2. Every original photo in the thread
seen = set()
for p in posts:
    for url in re.findall(r'https://discdn\.gbfans\.com/original/[^"\s)]+\.(?:jpe?g|png|webp)', p["cooked"]):
        if url in seen:
            continue
        seen.add(url)
        save(url, f"forum/photos/p{p['post_number']:03d}_{url.rsplit('/', 1)[-1]}", f"post {p['post_number']}")

# 3. Hasbro Pulse product images, 1984 pack
for i in range(1, 13):
    save(f"https://cdn.media.amplience.net/i/hasbropulse/G19145L00_{i}.png", f"hasbro/G19145L00_{i}.png",
         "Hasbro Pulse product image, 1984 pack")

# 4. HasLab manual (shared tooling)
save("https://instructions.hasbro.com/api/download/F5226_en-us_ghostbusters-plasma-series-spengler-s-proton-pack-"
     "collectible-has-lab-project-1-1-scale-movie-replica.pdf", "hasbro/F5226_manual.pdf", "HasLab manual")

(OUT / "manifest.json").write_text(json.dumps(manifest, indent=1), encoding="utf-8")
ok = sum(1 for m in manifest if m.get("file"))
print(f"{ok}/{len(manifest)} files fetched")
sys.exit(0 if ok else 1)
