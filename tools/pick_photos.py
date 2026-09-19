"""Turn the chosen candidates in content/picks.json into square photos for the game.
picks.json: {"apple": {"i": 9, "crop": [0.4, 0, 1, 1]}, ...}
  i    = the number on that word's contact sheet (assets/photo_candidates/<word>.jpg)
  crop = optional box as fractions of the photo [left, top, right, bottom]; the square is taken
         from its centre. Without it, the centre square of the whole photo is used.
  fit  = true to place the whole (cropped) photo on a white square instead of cutting it
Writes assets/photos/<word>.webp and content/photos.json (credits). Re-run after changing picks."""
import io, json, pathlib, re, urllib.request
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent.parent
PICKS = json.loads((ROOT / "content" / "picks.json").read_text(encoding="utf-8"))
CAND = ROOT / "assets" / "photo_candidates"
OUT = ROOT / "assets" / "photos"
OUT.mkdir(parents=True, exist_ok=True)
UA = {"User-Agent": "LittleWriter/1.0 (https://github.com/seun-john/little-writer; children's learning game)"}
SIZE = 360


def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=40) as r:
        return r.read()


def big_url(u):
    if "staticflickr.com" in u:
        return re.sub(r"(_[a-z])?\.jpg$", "_c.jpg", u)
    m = re.match(r"https://upload\.wikimedia\.org/wikipedia/commons/(\w/\w\w)/(.+)$", u)
    if m and not u.lower().endswith((".svg", ".tif", ".tiff")):
        return f"https://upload.wikimedia.org/wikipedia/commons/thumb/{m[1]}/{m[2]}/800px-{m[2]}"
    return u


def credit(r):
    lic = ("CC0" if r["license"] == "cc0" else f"CC {r['license'].upper()} {r.get('license_version') or ''}").strip()
    title = (r.get("title") or "Photo").strip()
    who = r.get("creator") or "unknown photographer"
    return f"“{title}” by {who}, {lic} ({r.get('foreign_landing_url') or r['url']})"


done = {}
for word, pick in PICKS.items():
    cands = json.loads((CAND / f"{word}.json").read_text(encoding="utf-8"))
    r = cands[pick["i"]]
    data = None
    alts = [big_url(r["url"]), r["url"]]
    if "staticflickr.com" in r["url"]:
        alts += [re.sub(r"(_[a-z])?\.jpg$", s, r["url"]) for s in ("_z.jpg", "_n.jpg")]
    m = re.match(r"https://upload\.wikimedia\.org/wikipedia/commons/(\w/\w\w)/(.+)$", r["url"])
    if m:
        alts.append(f"https://upload.wikimedia.org/wikipedia/commons/thumb/{m[1]}/{m[2]}/500px-{m[2]}")
    for u in alts:
        try:
            data = get(u)
            break
        except Exception:
            pass
    if not data:
        print("could not download", word)
        continue
    im = Image.open(io.BytesIO(data)).convert("RGB")
    W, H = im.size
    x0, y0, x1, y1 = pick.get("crop", [0, 0, 1, 1])
    bx0, by0, bx1, by1 = x0 * W, y0 * H, x1 * W, y1 * H
    side = min(bx1 - bx0, by1 - by0)
    cx, cy = (bx0 + bx1) / 2, (by0 + by1) / 2
    if pick.get("fit"):  # whole photo on a white square instead of cropping (for things on white)
        im = im.crop((int(bx0), int(by0), int(bx1), int(by1)))
        side = max(im.size)
        sq = Image.new("RGB", (side, side), "white")
        sq.paste(im, ((side - im.width) // 2, (side - im.height) // 2))
        im = sq
    else:
        im = im.crop((int(cx - side / 2), int(cy - side / 2), int(cx + side / 2), int(cy + side / 2)))
    im = im.resize((SIZE, SIZE), Image.LANCZOS)
    im.save(OUT / f"{word}.webp", "WEBP", quality=78, method=6)
    done[word] = {"credit": credit(r), "license": r["license"], "source": r.get("foreign_landing_url")}
    print("ok", word)

(ROOT / "content" / "photos.json").write_text(json.dumps(done, indent=1, ensure_ascii=False), encoding="utf-8")
print(f"{len(done)}/{len(PICKS)} photos ready")
