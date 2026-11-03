"""Search the GBFans forum (Discourse API) and save every matching topic's posts.

Reads queries from .github/forum_queries.txt (one per line). Saves
sources/search/results.json and sources/search/t<id>.json (all posts, raw).
"""
import json, time, urllib.parse, urllib.request
from pathlib import Path
B = "https://forum.gbfans.com"
UA = {"User-Agent": "Mozilla/5.0 (research fetch; rmbrumback-lab)", "Accept": "application/json"}
out = Path("sources/search"); out.mkdir(parents=True, exist_ok=True)
def get(url):
    req = urllib.request.Request(url, headers=UA)
    return json.loads(urllib.request.urlopen(req, timeout=60).read())
results, topics = {}, {}
for q in Path(".github/forum_queries.txt").read_text().splitlines():
    q = q.strip()
    if not q or q.startswith("#"):
        continue
    for page in (1, 2, 3):
        try:
            d = get(f"{B}/search.json?q={urllib.parse.quote(q)}&page={page}")
        except Exception as e:
            print("FAIL", q, e); break
        posts = d.get("posts", [])
        for t in d.get("topics", []):
            topics[t["id"]] = t.get("title")
        results.setdefault(q, []).extend({"topic_id": p["topic_id"], "post_number": p["post_number"], "blurb": p.get("blurb")} for p in posts)
        print(q, page, len(posts))
        if len(posts) < 50:
            break
        time.sleep(1)
    time.sleep(1)
(out / "results.json").write_text(json.dumps({"results": results, "topics": topics}, indent=1))
ids = sorted({r["topic_id"] for v in results.values() for r in v})
print(len(ids), "topics")
for tid in ids:
    try:
        d = get(f"{B}/t/{tid}.json?print=true")
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
    time.sleep(0.7)
