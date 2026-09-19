"""Search Openverse for openly licensed photos (CC0 / CC BY / CC BY-SA) of each word in
content.json and save small numbered previews as contact sheets, so a person can pick the
clearest photo for a small child. Results go to assets/photo_candidates/ (not published).
Usage: python tools/find_photos.py [word ...]   (no words = every word not yet searched)"""
import concurrent.futures as cf, io, json, pathlib, re, sys, time, urllib.parse, urllib.request
from PIL import Image, ImageDraw

ROOT = pathlib.Path(__file__).resolve().parent.parent
C = json.loads((ROOT / "content" / "content.json").read_text(encoding="utf-8"))
OUT = ROOT / "assets" / "photo_candidates"
OUT.mkdir(parents=True, exist_ok=True)
UA = {"User-Agent": "LittleWriter/1.0 (https://github.com/seun-john/little-writer; children's learning game)"}
N = 10


def get(url, timeout=30):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout) as r:
        return r.read()


def small_url(u):
    """Ask the photo host for a small copy where it offers one."""
    if "staticflickr.com" in u:
        return re.sub(r"(_[a-z])?\.jpg$", "_n.jpg", u)
    m = re.match(r"https://upload\.wikimedia\.org/wikipedia/commons/(\w/\w\w)/(.+)$", u)
    if m and not u.lower().endswith((".svg", ".tif", ".tiff")):
        return f"https://upload.wikimedia.org/wikipedia/commons/thumb/{m[1]}/{m[2]}/330px-{m[2]}"
    return u


def search(q):
    qs = urllib.parse.urlencode({"q": q, "license": "cc0,by,by-sa", "page_size": N, "mature": "false",
                                 "excluded_source": "", "aspect_ratio": "", "extension": "jpg,png"})
    return json.loads(get("https://api.openverse.org/v1/images/?" + qs))["results"]


def thumb(r):
    for u in (small_url(r["url"]), r["url"]):
        try:
            im = Image.open(io.BytesIO(get(u))).convert("RGB")
            im.thumbnail((220, 220))
            return im
        except Exception:
            pass
    return None


words = [(l, w) for l, d in C["letters"].items() for w in d["words"]]
only = set(sys.argv[1:])
for l, w in words:
    meta = OUT / f"{w['w']}.json"
    if (only and w["w"] not in only) or (not only and meta.exists()):
        continue
    try:
        res = search(w["q"])
    except Exception as e:
        print("search failed", w["w"], e)
        time.sleep(5)
        continue
    with cf.ThreadPoolExecutor(8) as ex:
        thumbs = list(ex.map(thumb, res))
    keep = [(r, t) for r, t in zip(res, thumbs) if t]
    meta.write_text(json.dumps([{k: r.get(k) for k in ("id", "title", "creator", "creator_url", "license",
                     "license_version", "license_url", "foreign_landing_url", "url", "attribution", "width", "height")}
                     for r, _ in keep], indent=1), encoding="utf-8")
    sheet = Image.new("RGB", (5 * 224, 2 * 250), "white")
    d = ImageDraw.Draw(sheet)
    for i, (_, t) in enumerate(keep):
        x, y = (i % 5) * 224, (i // 5) * 250
        sheet.paste(t, (x + 2 + (220 - t.width) // 2, y + 28 + (220 - t.height) // 2))
        d.rectangle([x + 2, y + 2, x + 40, y + 26], fill="black")
        d.text((x + 8, y + 6), str(i), fill="white", font_size=20)
    d.text((5 * 224 - 300, 2 * 250 - 24), f"{l}: {w['w']}  ({w['q']})", fill="red", font_size=18)
    sheet.save(OUT / f"{w['w']}.jpg", quality=80)
    print(f"{w['w']}: {len(keep)} candidates")
    time.sleep(3.2)  # stay inside Openverse's 20 searches a minute
