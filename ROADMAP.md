# Atelier — Roadmap

**Last updated:** April 18, 2026

---

## Status Summary

| Phase | Status | Notes |
|-------|--------|-------|
| Phase 1: Foundation | ✅ Complete | Kimi pipeline, p5.js engine, 3 visual modes |
| Phase 2: Core Features | ✅ Complete | Memory, narrative, TTS |
| Phase 3: Output & Polish | ✅ Complete | HTML brand guide, assembly, webroot sync |
| Phase 3.5: Bug Fixes | ✅ Complete | 15 bugs fixed, code review passed |
| Phase 3.6: Feature Push | ✅ Complete | Web UI, feedback loop, glitch+ink modes, mood tracking |
| Phase 4: Demo & Submission | 🔴 Not started | Deadline: May 3, 2026 (15 days) |

---

## Phase 4: Demo & Submission (Now → May 3)

### Week 1 (Apr 18-25): Demo Prep
- [ ] Write 2-minute demo script (see timing below)
- [ ] Pick 3 showcase briefs that produce distinct visual modes
- [ ] Pre-run demo sessions to have polished output ready
- [ ] Set up screen recording (terminal + browser side by side)
- [ ] Record dry run, review pacing

### Week 2 (Apr 26-May 3): Submission
- [ ] Record final demo video (clean terminal, no debug output)
- [ ] Write project description (what it does, why it matters)
- [ ] Post tweet with video, tag @NousResearch
- [ ] Drop tweet link in Discord #creative-hackathon-submissions
- [ ] Verify Kimi Track eligibility (video shows Kimi model)

### Demo Script (2 min)
| Time | Action | Shows |
|------|--------|-------|
| 0:00-0:20 | Type brief in terminal, run command | User input, CLI |
| 0:20-0:50 | Show terminal output: Kimi analysis, visual gen | Pipeline running, Kimi model |
| 0:50-1:20 | Open output page: canvas, palette, narrative, TTS | Full brand guide |
| 1:20-1:50 | Run second brief, show memory influencing output | Persistent memory |
| 1:50-2:00 | Close-up on Kimi model reference in terminal | Kimi Track proof |

---

## Post-Hackathon: What's Next

### P1: Architecture Improvements
- [ ] Extract `colors.py` — single source for palette math (eliminates visual.py/assemble.py duplication)
- [ ] Replace HTML f-string with Jinja2 templates (maintainability)
- [ ] Add unit tests for color math, memory ops, JSON parsing
- [ ] Structured logging (replace print statements)

### P2: Feature Expansion
- [x] **Web UI** — Flask frontend with brief form, results, feedback
- [x] **Feedback loop** — wired `update_preferences()` into rating UI (love/like/meh/dislike)
- [x] **Non-generic visual modes** — glitch (digital distortion), ink (watercolor diffusion)
- [x] **Mood tracking** — warm/cool/neutral tracked from palette in memory
- [ ] **Export formats** — PDF brand guide, Figma tokens, CSS variables
- [ ] **Prompt versioning** — track prompt schema changes so old memory stays compatible

### P3: Memory Intelligence
- [ ] Rolling window for session history (not just pruning at 50)
- [ ] Cross-user preference clusters ("users who liked X also liked Y")
- [ ] Seasonal/temporal awareness (trends shift over time)
- [ ] Track `mood` (warm/cool/neutral) from palette — currently ignored

### P4: Production Hardening
- [ ] Rate limiting + retry with backoff for Kimi API
- [ ] Async pipeline (Kimi calls + visual gen in parallel)
- [ ] Bundle p5.js locally (remove CDN dependency for offline use)
- [ ] Configurable output path (not hardcoded `/var/www/atelier/`)
- [ ] Docker container for one-command deployment

### P5: Monetization Angles
- [ ] **SaaS tier** — hosted version at atelier.ko4lax.dev with user accounts
- [ ] **API access** — developers integrate Atelier into their workflows
- [ ] **Template marketplace** — community visual modes
- [ ] **Agency tool** — white-label for design agencies doing brand exploration

---

## Technical Debt (from Code Review)

| Item | Severity | Status |
|------|----------|--------|
| XSS in HTML output | HIGH | ✅ Fixed (html.escape) |
| Path traversal in memory | MEDIUM | ✅ Fixed (sanitize user_id) |
| API crash on network error | MEDIUM | ✅ Fixed (try/except) |
| Memory unbounded growth | MEDIUM | ✅ Fixed (prune at 50) |
| Duplicate color logic | LOW | ⏳ Post-hackathon (extract colors.py) |
| HTML f-string (500+ lines) | LOW | ⏳ Post-hackathon (Jinja2) |
| Dead `update_preferences()` | LOW | ⏳ Post-hackathon (wire to UI) |
| No tests | LOW | ⏳ Post-hackathon (add test suite) |
| Hardcoded /var/www path | LOW | ⏳ Post-hackathon (config) |
| Memory convergence calcified | LOW | ✅ Fixed (EMA alpha=0.3) |

---

## Key Metrics

- **Codebase:** 6 Python files, ~1,300 LOC
- **Visual modes:** 5 (minimal, organic, bold, glitch, ink)
- **Sessions generated:** 12
- **Bugs fixed:** 15 (across 2 fix rounds)
- **Features shipped:** Web UI, feedback loop, mood tracking, 2 new visual modes
- **Cost per generation:** ~$0.01-0.05
- **Deadline:** May 3, 2026
- **Prize pool:** $10k + $3.5k (Main) / $3.5k + $1k (Kimi)
