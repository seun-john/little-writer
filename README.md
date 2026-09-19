# Little Writer

A talking handwriting game for nursery children, built for phones.

**Play:** https://seun-john.github.io/little-writer/ (on a phone, add it to the home screen to use it as an app; it keeps working offline).

- Trace pre-writing strokes (stroke, dash, slanted stroke, curve, circle), numbers 1–10 and letters a–z in ball-and-stick style, in worksheet rows that go from a full guide, to dots, to writing alone
- Count, add and take away with pictures
- "a is for apple" picture matching, balloon popping, and a sticker book

## Building

```
python tools/fetch_pics.py   # cartoon pictures listed in content/content.json
python tools/find_photos.py  # photo candidates to choose from (contact sheets)
python tools/pick_photos.py  # chosen photos in content/picks.json -> assets/photos
python tools/make_audio.py   # voice lines
python build.py              # writes the app to docs/
```

Words, pictures and letter sounds live in `content/content.json`; the game itself is in `parts/`.

## Credits

- Photos: openly licensed (CC0, CC BY, CC BY-SA) photos found through [Openverse](https://openverse.org); each photographer is credited in `content/photos.json` and in the app under Grown-ups → Photo credits
- Cartoon pictures and icons: [Microsoft Fluent Emoji](https://github.com/microsoft/fluentui-emoji) (MIT licence)
- Voice: Microsoft neural voice en-NG-Ezinne, generated with [edge-tts](https://github.com/rany2/edge-tts)
- Font: [Andika](https://fonts.google.com/specimen/Andika) by SIL (Open Font License)
