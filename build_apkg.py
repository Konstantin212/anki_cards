#!/usr/bin/env python3
"""Build the Anki .apkg from words.json.

Data source: words.json (list of entries). Each entry:
  {
    "word":        headword shown on the front (bare noun / verb infinitive).
                   Separable verbs mark the split with "*": "auf*stehen".
    "full":        "der Übersetzer, -" for nouns; "" for verbs,
    "translation": Ukrainian translation,
    "forms":       "Perfekt: ... · Präteritum: ..." for verbs; "" otherwise,
    "examples":    [[German sentence, Ukrainian translation], ...]  (0-2 items)
  }

Fixed model/deck IDs + guid derived from the CLEANED word (no "*") => re-importing
updates existing notes instead of duplicating, and adding a "*" marker later still
matches the same note.
"""
import os
from pathlib import Path

import genanki

from word_utils import clean_word, load_collection

HERE = os.path.dirname(os.path.abspath(__file__))

MODEL_ID = 1980290111
DECK_ID = 1980290222
DECK_NAME = "Deutsch_Begegnungen_A2_B1"

FIELDS = ["Word", "Full", "Translation", "Forms",
          "ExampleDE1", "ExampleUA1", "ExampleDE2", "ExampleUA2",
          "WordClean"]  # WordClean = Word without "*", used for TTS

TTS_VOICE = "com.google.android.tts-de-DE-language"  # explicit AnkiDroid/Google voice

FRONT = """
<div class="word">{{Word}}</div>
{{tts de_DE voices=%(v)s:WordClean}}
""".strip() % {"v": TTS_VOICE}

BACK = """
<div class="word">{{Word}}</div>
<hr id="answer">
{{#Full}}<div class="full">{{Full}}</div>{{/Full}}
<div class="translation">{{Translation}}</div>
{{#Forms}}<div class="forms">{{Forms}}</div>{{/Forms}}
{{#ExampleDE1}}<div class="example"><div class="de">{{ExampleDE1}}</div><div class="ua">{{ExampleUA1}}</div></div>{{/ExampleDE1}}
{{#ExampleDE2}}<div class="example"><div class="de">{{ExampleDE2}}</div><div class="ua">{{ExampleUA2}}</div></div>{{/ExampleDE2}}
{{tts de_DE voices=%(v)s:ExampleDE1}}
""".strip() % {"v": TTS_VOICE}

CSS = """
.card {
  font-family: -apple-system, "Segoe UI", Roboto, Arial, sans-serif;
  font-size: 20px;
  text-align: center;
  color: #1a202c;
  background: #ffffff;
}
.nightMode .card, .card.nightMode { color: #e8eaed; background: #202124; }
.word { font-size: 30px; font-weight: 600; margin: 10px 0; }
.full { font-size: 22px; font-weight: 600; color: #2b6cb0; margin-top: 10px; }
.nightMode .full { color: #7fb0e8; }
.translation { font-size: 24px; margin: 8px 0 4px; }
.forms { font-size: 15px; color: #718096; margin: 6px 0 4px; }
.nightMode .forms { color: #9aa0a6; }
.example { margin: 16px auto 0; max-width: 92%; }
.example .de { font-size: 19px; }
.example .ua { font-size: 16px; font-style: italic; color: #718096; margin-top: 2px; }
.nightMode .example .ua { color: #9aa0a6; }
hr#answer { margin: 16px 0; border: none; border-top: 1px solid #cbd5e0; }
.nightMode hr#answer { border-top: 1px solid #3c4043; }
"""

model = genanki.Model(
    MODEL_ID,
    "Deutsch Wort",
    fields=[{"name": f} for f in FIELDS],
    templates=[{"name": "Karte", "qfmt": FRONT, "afmt": BACK}],
    css=CSS,
)


def entry_to_fields(e):
    ex = e.get("examples", [])
    de1, ua1 = (ex[0] if len(ex) > 0 else ("", ""))
    de2, ua2 = (ex[1] if len(ex) > 1 else ("", ""))
    return [e["word"], e.get("full", ""), e["translation"], e.get("forms", ""),
            de1, ua1, de2, ua2, clean_word(e["word"])]


def main():
    data = load_collection(Path(HERE) / "words.json")

    deck = genanki.Deck(DECK_ID, DECK_NAME)
    for e in data:
        deck.add_note(genanki.Note(
            model=model,
            fields=entry_to_fields(e),
            guid=genanki.guid_for(clean_word(e["word"])),  # stable => updates, no dupes
        ))

    out = os.path.join(HERE, "Deutsch_Begegnungen_A2_B1.apkg")
    genanki.Package(deck).write_to_file(out)
    print(f"Wrote {out} ({len(data)} notes)")


if __name__ == "__main__":
    main()
