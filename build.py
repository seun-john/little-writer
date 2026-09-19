"""Build the game: joins parts/*.html into index.html and bundles the pictures and
voice clips into content.js and voice.js (so the game is just 3 files).
Run tools/fetch_pics.py and tools/make_audio.py first when words change."""
import base64, json, pathlib

ROOT = pathlib.Path(__file__).resolve().parent
parts = sorted((ROOT / "parts").glob("*.html"))
(ROOT / "index.html").write_text("".join(p.read_text(encoding="utf-8") for p in parts), encoding="utf-8")

content = json.loads((ROOT / "content" / "content.json").read_text(encoding="utf-8"))
phrases = json.loads((ROOT / "assets" / "phrases.json").read_text(encoding="utf-8"))
pics = {p.stem: "data:image/webp;base64," + base64.b64encode(p.read_bytes()).decode()
        for p in sorted((ROOT / "assets" / "pics").glob("*.webp"))}
(ROOT / "content.js").write_text(
    "window.CONTENT=" + json.dumps(content, separators=(",", ":")) + ";\n"
    "window.PHRASES=" + json.dumps(phrases, separators=(",", ":")) + ";\n"
    "window.PICS=" + json.dumps(pics, separators=(",", ":")) + ";\n", encoding="utf-8")

clips = {k: "data:audio/mpeg;base64," + base64.b64encode((ROOT / "assets" / "audio" / f"{k}.mp3").read_bytes()).decode()
         for k in phrases if (ROOT / "assets" / "audio" / f"{k}.mp3").exists()}
(ROOT / "voice.js").write_text("window.CLIPS=" + json.dumps(clips, separators=(",", ":")) + ";\n", encoding="utf-8")

# the installable app: everything in docs/ (served by GitHub Pages)
import hashlib, shutil
site = ROOT / "docs"
site.mkdir(exist_ok=True)
for f in ("index.html", "content.js", "voice.js"):
    shutil.copy(ROOT / f, site / f)
for f in (ROOT / "app").iterdir():
    if f.name != "sw.js":
        shutil.copy(f, site / f.name)
version = hashlib.sha1(b"".join((site / f).read_bytes() for f in ("index.html", "content.js", "voice.js"))).hexdigest()[:10]
(site / "sw.js").write_text((ROOT / "app" / "sw.js").read_text(encoding="utf-8").replace("__VERSION__", "lw-" + version), encoding="utf-8")
(site / ".nojekyll").write_text("")

for f in ("index.html", "content.js", "voice.js"):
    print(f"{f}: {(ROOT / f).stat().st_size / 1e6:.2f} MB")
print(f"{len(pics)} pictures, {len(clips)}/{len(phrases)} voice clips")
