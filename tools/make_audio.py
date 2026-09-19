"""Generate every spoken line in the game with a free Microsoft neural voice (edge-tts)
into assets/audio/<key>.mp3, plus phrases.json (key -> text). Existing clips are kept,
so edit a line's text and delete its mp3 to re-record just that one."""
import asyncio, json, pathlib
import edge_tts

ROOT = pathlib.Path(__file__).resolve().parent.parent
C = json.loads((ROOT / "content" / "content.json").read_text(encoding="utf-8"))
OUT = ROOT / "assets" / "audio"
OUT.mkdir(parents=True, exist_ok=True)

P = {}
for l, d in C["letters"].items():
    U = l.upper()
    P[f"wr_{l}"] = f"Let's write the letter {U}!"
    P[f"q_{l}"] = f"{U} is for... what?"
    P[f"find_{l}"] = f"Find the letter {U}!"
    P[f"that_{l}"] = f"That is the letter {U}."
    P[f"snd_{l}"] = f"{U} says... {d['sound']}."
    for i, w in enumerate(d["words"]):
        word = w[0].replace("-", " ") if w[0] != "yo-yo" else "yo-yo"
        P[f"is_{l}_{i}"] = f"{word.capitalize()} ends with {U}." if len(w) > 2 else f"{U} is for {word}."
for k, word in enumerate(C["numbers"], 1):
    P[f"n_{k}"] = f"{word.capitalize()}."
    P[f"wrn_{k}"] = f"Let's write number {word}!"
    P[f"findn_{k}"] = f"Find the number {word}!"
    P[f"thatn_{k}"] = f"That is {word}."
P.update({
    "ln_stand": "Let's draw a stroke!", "ln_sleep": "Let's draw a dash!",
    "ln_slant": "Let's draw a slanted stroke!", "ln_curve": "Let's draw a curve!",
    "ln_circle": "Let's draw a circle!", "ln_cross": "Let's draw a cross!",
    "b_stand": "Stroke.", "b_sleep": "Dash.", "b_slant": "Slanted stroke.",
    "b_curve": "Curve.", "b_circle": "Circle.", "b_hook": "Hook.", "b_hump": "Hump.", "b_dot": "Dot.",
    "then": "then,",
    "tip_top": "Top to bottom.", "tip_left": "Left to right.", "tip_slide": "Slide down.",
    "tip_round": "Start at the top, and go round.", "tip_eight": "Curve, curve, and back up.",
    "watch": "Watch me!", "turn_first": "Your turn! Start at the green dot.", "turn": "Your turn!",
    "green": "Start at the green dot!", "tapdot": "Tap the dot!", "erase": "All clean! Let's try again.",
    "count_tap": "How many? Tap each one to count!", "which": "Which number is it?",
    "tryagain": "Try again!", "count_them": "Let's count them!",
    "star": "You got a star!", "sticker": "Wow! A new sticker!",
    "p1": "Well done!", "p2": "Super!", "p3": "You did it!", "p4": "Great writing!",
    "p5": "Hurray!", "p6": "Wonderful!", "p7": "Good job!", "p8": "Great counting!", "p9": "Great job!",
    "again": "Let's practise again!", "offtrack": "Oops! Stay on the line.",
    "add_intro": "Let's add!", "sub_intro": "Let's take away!",
    "plus": "plus", "take": "take away", "equals": "makes",
    "altogether": "How many altogether?", "left": "How many are left?",
    "fly": "Bye bye!", "pick": "Pick a game!",
})


async def one(key, text, sem):
    dest = OUT / f"{key}.mp3"
    if dest.exists():
        return
    async with sem:
        for attempt in range(3):
            try:
                await edge_tts.Communicate(text, C["voice"], rate=C["rate"], pitch="+4Hz").save(str(dest))
                return
            except Exception as e:  # network hiccup: retry
                if attempt == 2:
                    print("FAILED", key, e)
                await asyncio.sleep(2)


async def main():
    sem = asyncio.Semaphore(6)
    await asyncio.gather(*(one(k, t, sem) for k, t in P.items()))
    (OUT.parent / "phrases.json").write_text(json.dumps(P, indent=1), encoding="utf-8")
    have = sum(1 for k in P if (OUT / f"{k}.mp3").exists())
    print(f"{have}/{len(P)} clips ready")

asyncio.run(main())
