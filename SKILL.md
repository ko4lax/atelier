---
name: atelier
description: "Atelier — AI Creative Director. Generates complete brand identity systems from a brief: visual direction, color palette, typography, taglines, brand story, manifesto audio, and a downloadable HTML brand guide. Powered by Kimi K2.5 + p5.js + Minerva TTS. Run locally: `python3 /root/atelier/src/atelier.py \"your brand brief\"`"
triggers:
  - "build a brand identity"
  - "create a brand palette"
  - "generate brand guidelines"
  - "atelier brand"
  - "creative director"
  - "visual identity"
---

# Atelier — AI Creative Director

## What it does

Takes a brand/product brief → generates a complete brand identity system:
- **Visual direction** — p5.js generative art (colors, motion, form)
- **Color palette** — 5-color HSB system with emotional rationale
- **Typography** — heading + body pairing recommendations
- **Taglines** — 5 brand taglines
- **Brand story** — narrative arc and positioning
- **Manifesto** — TTS audio version
- **Social voice** — platform presence and tone
- **Output page** — self-contained HTML brand guide

## Run

```bash
cd /root/atelier

# CLI mode
python3 src/atelier.py --brief "premium coffee brand for remote workers" --user koala

# Web UI mode
python3 src/web.py
# → opens at http://localhost:5000
```

## Architecture

```
atelier/
  src/
    atelier.py       # Main orchestrator
    prompts.py       # Kimi K2.5 prompt templates (analysis + narrative)
    visual.py        # p5.js generative art engine (5 modes: minimal/organic/bold/glitch/ink)
    assemble.py      # HTML brand guide assembly + webroot sync
    memory.py        # Persistent aesthetic preference learning + mood tracking
    web.py           # Flask web UI with feedback loop
  memory/
    {user_id}.json   # Per-user preference weights + session history
  output/
    <session_id>/
      index.html      # Full brand guide (public)
      visual.html     # p5.js canvas
      preview.png     # Screenshot (optional, via Playwright)
      palette.json    # HSB palette data
      analysis.json   # Full analysis
      narrative.json  # Story, taglines, manifesto
      manifesto.mp3   # TTS audio
  webroot/            # Served at atelier.ko4lax.dev/<session_id>/
```

## Key constraints

- **Kimi K2.5** requires `temperature=0.6` + `extra_body={"thinking":{"type":"disabled"}}`
- **p5.js** — `noiseSeed` seeded random, 3 visual modes (minimal/organic/bold)
- **gTTS** — Google TTS, English narration, generates MP3 manifestos
- **Screenshots** — Playwright headless chromium, ignore cert errors flag
- **Output** — auto-synced to `/var/www/atelier/<session_id>/`

## Hackathon context

- Competing: Main Track + Kimi Track
- Deadline: May 3 2026
- Repo: `github.com/Dreamvalian/atelier`
- Live: `atelier.ko4lax.dev`
