# Atelier — Build Checklist

## Project: AI Creative Director Agent
**Hackathon:** Hermes Agent Creative Hackathon (Creative Edition)
**Deadline:** May 3, 2026
**Tracks:** Main Track + Kimi Track (dual eligibility)

---

## Phase 1: Foundation (Day 1-3) ✅

### Environment Setup
- [x] Get Kimi API key (platform.moonshot.ai or OpenRouter) — Koala provided
- [x] Install Node.js (`apt install nodejs npm`) — not needed (pure Python + p5.js CDN)
- [x] Create `~/atelier/` project directory — done
- [x] Set up Python venv with dependencies (openai, jinja2) — done
- [x] Test Kimi API connection with simple prompt — verified ✅

### Kimi Analysis Pipeline
- [x] Design brand analysis prompt template (brief → structured JSON)
- [x] Build `prompts.py` — all prompt templates in one file
- [x] Build `atelier.py` — main orchestrator skeleton
- [x] Test: input brief → get back personality, palette, direction JSON — verified (3 sessions)
- [x] Handle edge cases: URL input, image input, short vague briefs — URL/images tested

### p5.js Visual Engine
- [x] Design 3 visual modes based on brand personality:
  - [x] Minimal mode (geometric, negative space, slow motion) ✅
  - [x] Organic mode (flow fields, noise curves, breathing) ✅
  - [x] Bold mode (particles, high contrast, explosive) ✅
- [x] Build `generate_visual.py` — takes analysis JSON → outputs HTML file
- [x] Parameterize: colors from palette, complexity from personality, motion from energy
- [x] Test: each mode generates valid HTML that opens in browser — all 3 modes verified
- [x] PNG export via headless capture or saveCanvas — Playwright screenshot verified ✅

---

## Phase 2: Core Features (Day 4-8) ✅

### Memory System
- [x] Design `memory/{user_id}.json` schema — done
- [x] Build `memory.py`:
  - [x] `load_memory(user_id)` — read existing preferences ✅
  - [x] `save_session(user_id, session_data)` — record generation + feedback ✅
  - [x] `get_preferences(user_id)` — extract weighted aesthetic fingerprint ✅
  - [x] `update_preferences(user_id, feedback)` — adjust weights from explicit feedback ✅
- [x] Integrate memory into analysis prompt (Kimi sees past preferences) ✅
- [x] Test: run 3 sessions, verify preferences shift based on feedback — verified (6 sessions, weights updating) ✅

### Narrative Generation
- [x] Design narrative prompt (brand voice, taglines, emotional rationale) ✅
- [x] Generate 3 tagline variations per session ✅
- [x] Generate brand story paragraph ✅
- [x] Generate "why" rationale for each visual choice ✅
- [x] Generate brand voice sample (social media copy) ✅

### TTS Integration
- [x] Build TTS call for brand manifesto narration — gTTS ✅
- [x] Save as MP3 in output directory ✅
- [x] Embed audio player in output page — Phase 3 output.html

---

## Phase 3: Output & Polish (Day 9-12) ✅

### Output Page
- [x] Design `assemble.py` layout:
  - [x] Hero section — p5.js canvas (interactive iframe)
  - [x] Color palette section — swatch cards with hex values
  - [x] Typography section — font pairing display
  - [x] Brand voice section — taglines + copy samples
  - [x] Rationale section — "why these choices"
  - [x] Audio section — TTS player
  - [x] Download section — PNG, palette JSON, analysis JSON, narrative JSON
  - [x] Dark theme, premium feel, responsive
  - [x] Assemble all components into single HTML file per session ✅

### End-to-End Integration
- [x] Wire all layers together in `atelier.py`:
  - [x] Input → Analysis → Memory lookup → Visual gen → Narrative → TTS → Output page
  - [x] Add CLI interface: `python3 src/atelier.py --brief "minimal tech startup" --user koala`
  - [x] Error handling for API failures, missing keys, empty inputs
  - [x] Progress logging for demo visibility
- [x] Auto-sync to `/var/www/atelier/<session_id>/`

### Hermes Skill Registration
- [x] Write `SKILL.md` for Atelier as a Hermes skill ✅
- [x] Test: "Hey Hermes, create a brand identity for my coffee shop" → triggers Atelier
- [ ] Hermes gateway integration test (pending Koala test)

---

## Phase 4: Demo & Submission (Day 13-15)

### Video Demo
- [ ] Script the 2-minute demo:
  - [ ] 0:00-0:20 — Show input: type a brief
  - [ ] 0:20-0:50 — Show pipeline running: Kimi analysis, p5.js generation
  - [ ] 0:50-1:20 — Show output: interactive page, visuals, narrative
  - [ ] 1:20-1:50 — Show memory: second session shows learned preferences
  - [ ] 1:50-2:00 — Show Kimi model usage (for Kimi Track eligibility)
- [ ] Record demo (screen capture + terminal)
- [ ] Edit for pacing — no dead air, snappy cuts

### Writeup & Submission
- [ ] Write brief project description (what it does, why it matters)
- [ ] Record video demo
- [ ] Tweet with video tagging @NousResearch
- [ ] Drop tweet link in Nous Discord #creative-hackathon-submissions channel
- [ ] Verify Kimi Track eligibility (video shows Kimi model usage)

---

## Dependencies (Blockers)

| Item | Status | Owner |
|------|--------|-------|
| Kimi API key | 🟢 SET (`MOONSHOT_API_KEY` in `~/.hermes/configs/.env`) | — |
| Node.js installed | 🔴 NOT INSTALLED | Onyx (not needed — pure Python + p5.js CDN) |
| ffmpeg | 🟢 INSTALLED | — |
| Python 3 | 🟢 INSTALLED | — |
| p5.js skill | 🟢 AVAILABLE | — |
| TTS capability | 🟢 AVAILABLE (gTTS) | — |

---

## Notes

- Kimi K2.5 pricing: ~$0.60/M input, $3.00/M output (direct) or $0.45/$2.20 (OpenRouter)
- Estimated cost per generation: $0.01-0.05
- p5.js output is single self-contained HTML — no server needed for viewing
- Memory system is file-based JSON — no database needed
- Total estimated build time: 12-13 active days, 2 days buffer
