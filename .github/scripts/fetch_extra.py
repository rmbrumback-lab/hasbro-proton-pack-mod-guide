"""Download the URLs listed in .github/fetch_extra.txt into sources/extra/ (one per line: url [filename])."""
import hashlib, json, urllib.request
from pathlib import Path
out = Path("sources/extra"); out.mkdir(parents=True, exist_ok=True)
man = []
for line in Path(".github/fetch_extra.txt").read_text().splitlines():
    if not line.strip() or line.startswith("#"):
        continue
    parts = line.split()
    url, name = parts[0], (parts[1] if len(parts) > 1 else parts[0].rsplit("/", 1)[-1].split("?")[0])
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (research fetch)"})
        data = urllib.request.urlopen(req, timeout=120).read()
        (out / name).write_bytes(data)
        man.append({"url": url, "file": name, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()})
        print("ok", len(data), url)
    except Exception as e:
        man.append({"url": url, "error": str(e)}); print("FAIL", url, e)
(out / "manifest.json").write_text(json.dumps(man, indent=1))
