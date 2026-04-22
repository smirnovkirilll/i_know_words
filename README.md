[![CI](https://github.com/smirnovkirilll/i_know_words/actions/workflows/python-publish.yml/badge.svg)](https://github.com/smirnovkirilll/i_know_words/actions/workflows/python-publish.yml)
[![PyPI version](https://img.shields.io/pypi/v/i_know_words.svg)](https://pypi.org/project/i_know_words/)
[![License](https://img.shields.io/github/license/smirnovkirilll/i_know_words)](./LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/smirnovkirilll/i_know_words?style=social)](https://github.com/smirnovkirilll/i_know_words/stargazers)


> [!CAUTION]
> AI-created/vibe coded
>
> AI-model: ChatGPT 5.2
>
> AI-participation degree: 80%


# I Know Words


## What is this?

**I Know Words** is a lightweight macOS menubar application for ambient vocabulary exposure.

It sits quietly in your system tray and surfaces words from your own dictionaries at a steady pace — no sessions, no pressure, no gamification.
Where traditional tools demand attention, I Know Words works in the background.
Just enough to feel productive without actually trying too hard.

---

## How It Compares

| Tool             | UX Model           | Friction   | Customization        | Passive Mode | Notes                            |
| ---------------- | ------------------ | ---------- | -------------------- | ------------ | -------------------------------- |
| **I Know Words** | Menubar, always-on | ⭐ Very low | ⭐ High (YAML + JSON) | ✅ Yes        | Background exposure, no sessions |
| WordBar          | Menubar            | Low        | Low                  | ✅ Yes        | Minimal, less configurable       |
| Vocable          | Full app           | Medium     | Medium               | ❌ No         | Session-based learning           |
| Anki             | Full app (SRS)     | High       | High                 | ❌ No         | Powerful but requires discipline |
| Memrise          | App/Web            | Medium     | Low                  | ❌ No         | Gamified, content-driven         |

---

## Key Differences

### vs Anki / Vocable

* No sessions
* No “review queue”
* No cognitive overhead

👉 You don’t *study* words — you just keep seeing them.

---

### vs WordBar

* Configurable menu structure
* Multiple dictionaries
* Frequency-based word selection

👉 More control, same simplicity.

---

### vs Memrise

* No gamification
* No streaks
* No dopamine loops

👉 Just words. Quietly appearing.

---

## Philosophy

* No popups
* No notifications
* No streaks
* No guilt

Just words. Appearing. Like you planned it.

---

## Why?

Because opening Anki is a commitment.

This is not.

---

## When to Use It

* While working
* While coding
* While pretending to be productive

---

## What It’s Not

* Not a full learning system
* Not a replacement for Anki
* Not trying to make you fluent overnight

---

## Features

* 🧠 Random word rotation with frequency-based weighting (common words appear more often)
* ⏱ Configurable update interval
* 🌍 Multiple dictionaries with instant switching
* 📌 Menubar-first UX (no windows, no distractions)
* 🔗 Clickable links (Wiktionary, Google Translate, etc.)
* 📋 One-click copy for any field
* 🕘 History of recently shown words
* 🎛 Configurable menu structure via YAML

---

## How it works

* Words are loaded from JSON dictionaries
* Selection is weighted using logarithmic ranking (if available)
* The UI is rendered dynamically from config
* The app lives entirely in your system tray

---

## Installation

```bash
pip install -r requirements.txt
```

Run:

```bash
python3 app.py
```

---

## Configuration

All behavior is controlled via `config.yaml`.

Example:

```yaml
interval: 10

dictionaries:
  TR → EN: dictionaries/tr_en.json
  EN → TR: dictionaries/en_tr.json

default: TR → EN

display:
  tr_en:
    show_translation_in_bar: false
    ranking:
      enabled: true
      key: rank
    menu_items:
      word: english
      translation: turkish
      wiktionary: wiktionary
      gtranslate: "google translate"
      rank: rank
```

---

## Dictionary Format

Each dictionary is a JSON array of objects:

```json
[
  {
    "english": "ephemeral",
    "turkish": "geçici",
    "rank": 1234,
    "wiktionary": "https://...",
    "google translate": "https://..."
  }
]
```

* Keys are flexible — just reference them in config
* URL values become clickable links in the menu

---

## Disclaimer

This app will not make you fluent.

But it will make you *feel* like you're doing something about it — which is arguably more important.

---

## Known Issues

* dictionaries are not ready yet
* no hotkeys implemented
* no timer-reset on `Next`-button use
