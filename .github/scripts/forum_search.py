"""Search the GBFans forum (Discourse API) and save every matching topic's posts.

Reads queries from .github/forum_queries.txt (one per line). Saves
sources/search/results.json and sources/search/t<id>.json (all posts, raw).
"""
import json, time, urllib.error, urllib.parse, urllib.request
from pathlib import Path
B = "https://forum.gbfans.com"
UA = {"User-Agent": "Mozilla/5.0 (research fetch; rmbrumback-lab)", "Accept": "application/json"}
out = Path("sources/search"); out.mkdir(parents=True, exist_ok=True)
def get(url, tries=5):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers=UA)
            return json.loads(urllib.request.urlopen(req, timeout=60).read())
        except urllib.error.HTTPError as e:
            if e.code == 429 and i < tries - 1:
                wait = int(e.headers.get("Retry-After", "20") or 20)
                print("429, waiting", wait); time.sleep(min(wait, 90) + 2); continue
            raise
results, topics = {}, {}
for q in Path(".github/forum_queries.txt").read_text().splitlines():
    q = q.strip()
    if not q or q.startswith("#"):
        continue
    for page in (1, 2, 3):
        try:
            d = get(f"{B}/search.json?q={urllib.parse.quote(q)}&page={page}")
        except Exception as e:
            print("FAIL", q, e); time.sleep(30); break
        posts = d.get("posts", [])
        for t in d.get("topics", []):
            topics[t["id"]] = t.get("title")
        results.setdefault(q, []).extend({"topic_id": p["topic_id"], "post_number": p["post_number"], "blurb": p.get("blurb")} for p in posts)
        print(q, page, len(posts))
        if len(posts) < 50:
            break
        time.sleep(6)
    time.sleep(6)
(out / "results.json").write_text(json.dumps({"results": results, "topics": topics}, indent=1))
import os
extra = [int(x) for x in Path(".github/forum_topics.txt").read_text().split()] if Path(".github/forum_topics.txt").exists() and not os.environ.get("NO_EXTRA") else []
kw = ("haslab", "hasbro", "spengler", "1984 pack", "plasma")
if os.environ.get("ALL_RESULTS"):
    # every topic with a matching post, ranked by number of hits, capped
    from collections import Counter
    hits = Counter(r["topic_id"] for v in results.values() for r in v)
    found = [t for t, _ in hits.most_common(int(os.environ.get("MAX_TOPICS", "80")))]
else:
    found = [r["topic_id"] for v in results.values() for r in v
             if any(k in (topics.get(r["topic_id"]) or "").lower() for k in kw)]
ids = sorted(set(extra) | set(found))
print(len(ids), "topics")
errs = []
for tid in ids:
    try:
        d = get(f"{B}/t/{tid}.json")
        posts = d["post_stream"]["posts"]
        stream = d["post_stream"].get("stream", [])
        have = {p["id"] for p in posts}
        miss = [i for i in stream if i not in have]
        for k in range(0, len(miss), 20):
            qs = "&".join(f"post_ids[]={i}" for i in miss[k:k + 20])
            posts += get(f"{B}/t/{tid}/posts.json?{qs}")["post_stream"]["posts"]
            time.sleep(0.5)
        slim = {"id": tid, "title": d.get("title"), "posts": [{"n": p["post_number"], "user": p["username"], "created": p["created_at"], "cooked": p["cooked"]} for p in sorted(posts, key=lambda p: p["post_number"])]}
        (out / f"t{tid}.json").write_text(json.dumps(slim))
        print("topic", tid, len(posts))
    except Exception as e:
        print("FAIL topic", tid, e)
        errs.append({"topic": tid, "error": repr(e), "body": getattr(e, "read", lambda: b"")()[:300].decode("utf-8", "replace")})
    time.sleep(3)
(out / "errors.json").write_text(json.dumps(errs, indent=1))
