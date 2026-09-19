"""Download Microsoft Fluent 3D emoji (MIT licence) named in content.json and save
them as small WebP files in assets/pics/. Existing files are skipped."""
import io, json, pathlib, urllib.parse, urllib.request
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent.parent
C = json.loads((ROOT / "content" / "content.json").read_text(encoding="utf-8"))
OUT = ROOT / "assets" / "pics"
OUT.mkdir(parents=True, exist_ok=True)
RAW = "https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/"
API = "https://api.github.com/repos/microsoft/fluentui-emoji/contents/assets/"


def key(name):
    return name.lower().replace(" ", "_")


def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "little-writer"}), timeout=30) as r:
        return r.read()


def fetch(name):
    q = urllib.parse.quote(name)
    s = key(name)
    for path in (f"{q}/3D/{s}_3d.png", f"{q}/Default/3D/{s}_3d_default.png"):
        try:
            return get(RAW + path)
        except Exception:
            pass
    # fall back to asking GitHub for the real file name
    for sub in ("3D", "Default/3D"):
        try:
            files = json.loads(get(API + q + "/" + sub))
            png = [f for f in files if f["name"].endswith(".png")]
            if png:
                return get(png[0]["download_url"])
        except Exception:
            pass
    return None


names = set(C["countThings"] + C["stickers"] + C["buddies"] + C["extraPics"])
for l in C["letters"].values():
    names.update(w[1] for w in l["words"])

missing = []
for name in sorted(names):
    dest = OUT / (key(name) + ".webp")
    if dest.exists():
        continue
    data = fetch(name)
    if not data:
        missing.append(name)
        continue
    img = Image.open(io.BytesIO(data)).convert("RGBA")
    img.thumbnail((160, 160), Image.LANCZOS)
    img.save(dest, "WEBP", quality=82, method=6)
    print("ok", name)

print(f"{len(names) - len(missing)} pictures ready, missing: {missing}")
