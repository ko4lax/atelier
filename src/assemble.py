"""
Assembly module — combines all session data into a single polished HTML page.
"""

import json
import os


def hex_from_palette(palette_json):
    """Convert palette JSON (HSB raw) to hex colors.
    
    Offsets MUST match visual.py generate_palette_colors() so the
    brand guide swatches match the p5.js canvas colors exactly.
    """
    p = palette_json if isinstance(palette_json, dict) else json.loads(palette_json)
    h_main = p.get("primary_hue", 210)
    h_sec = p.get("secondary_hue", (h_main + 30) % 360)
    h_acc = p.get("accent_hue", (h_main + 180) % 360)
    sat = p.get("saturation", 50)
    bri = p.get("brightness", 80)
    import colorsys
    def hsb(h, s, v):
        r, g, b = colorsys.hsv_to_rgb(h/360, s/100, v/100)
        return f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"
    # Offsets match visual.py generate_palette_colors() exactly
    bg_sat = max(10, sat - 40)
    bg_bri = max(8, bri - 70)
    muted_sat = max(5, sat - 30)
    muted_bri = max(30, bri - 30)
    return {
        "bg": hsb(h_main, bg_sat, bg_bri),
        "primary": hsb(h_main, sat, bri),
        "secondary": hsb(h_sec, max(20, sat - 15), bri),
        "accent": hsb(h_acc, min(100, sat + 20), bri),
        "text": hsb(h_main, 15, 95),
        "muted": hsb(h_main, muted_sat, muted_bri),
    }


def generate_session_page(session_dir, session_id):
    """Build a full interactive HTML page for this session."""
    base = session_dir

    # Load data
    with open(os.path.join(base, "analysis.json")) as f:
        analysis = json.load(f)
    with open(os.path.join(base, "narrative.json")) as f:
        narrative = json.load(f)
    with open(os.path.join(base, "palette.json")) as f:
        palette = json.load(f)

    colors = hex_from_palette(palette)
    personality = analysis.get("brand_personality", "creative")
    tags = analysis.get("keywords", [])[:5]
    color_meaning = narrative.get("color_meaning", {})

    manifesto_exists = os.path.exists(os.path.join(base, "manifesto.mp3"))
    visual_exists = os.path.exists(os.path.join(base, "visual.html"))
    preview_exists = os.path.exists(os.path.join(base, "preview.png"))

    tags_html = "".join(f'<span class="tag">#{t}</span>' for t in tags)

    audio_html = ""
    if manifesto_exists:
        audio_html = f'''
        <section class="audio-section">
          <h2>Brand Manifesto</h2>
          <p class="manifesto-text">"{narrative.get("manifesto", "")}"</p>
          <audio controls>
            <source src="manifesto.mp3" type="audio/mpeg">
            Your browser does not support audio.
          </audio>
        </section>'''

    rationale = narrative.get("visual_rationale", "")
    brand_story = narrative.get("brand_story", "")
    taglines = narrative.get("taglines", [])
    social = narrative.get("social_voice", {})
    color_meaning_str = narrative.get("color_meaning", {})

    palette_html = ""
    for name, hex_val in colors.items():
        palette_html += f'''
        <div class="swatch-card">
          <div class="swatch" style="background:{hex_val}"></div>
          <span class="swatch-name">{name}</span>
          <code class="swatch-hex">{hex_val}</code>
        </div>'''

    taglines_html = ""
    for i, tag in enumerate(taglines, 1):
        taglines_html += f'<div class="tagline"><span class="tagline-num">0{i}</span>{tag}</div>'

    color_meaning_html = ""
    if color_meaning_str:
        for name, meaning in color_meaning_str.items():
            hex_val = colors.get(name, "#888")
            color_meaning_html += f'''
            <div class="meaning-card">
              <div class="meaning-dot" style="background:{hex_val}"></div>
              <div>
                <strong>{name.capitalize()}</strong>
                <p>{meaning}</p>
              </div>
            </div>'''

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{analysis.get("brand_personality", "Creative").capitalize()} Brand Identity — Atelier</title>
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=Playfair+Display:ital,wght@0,400;0,700;1,400&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
  :root {{
    --bg: {colors["bg"]};
    --primary: {colors["primary"]};
    --secondary: {colors["secondary"]};
    --accent: {colors["accent"]};
    --text: {colors["text"]};
    --muted: {colors["muted"]};
    --surface: rgba(255,255,255,0.03);
    --border: rgba(255,255,255,0.07);
  }}
  html {{ scroll-behavior: smooth; }}
  body {{
    font-family: 'Space Grotesk', sans-serif;
    background: var(--bg);
    color: var(--text);
    line-height: 1.6;
  }}
  ::selection {{ background: var(--accent); color: var(--bg); }}

  /* Nav */
  nav {{
    position: fixed; top: 0; left: 0; right: 0;
    display: flex; justify-content: space-between; align-items: center;
    padding: 1rem 2rem;
    background: rgba(10,10,15,0.85);
    backdrop-filter: blur(12px);
    border-bottom: 1px solid var(--border);
    z-index: 100;
  }}
  .nav-logo {{
    font-family: 'Playfair Display', serif;
    font-size: 1.2rem; font-weight: 700;
    color: var(--text);
    text-decoration: none;
  }}
  .nav-badge {{
    font-size: 0.7rem; font-family: 'JetBrains Mono', monospace;
    background: var(--accent);
    color: var(--bg);
    padding: 0.2rem 0.6rem;
    border-radius: 100px;
    letter-spacing: 0.05em;
  }}

  /* Hero */
  .hero {{
    min-height: 100vh;
    display: grid;
    grid-template-columns: 1fr 1fr;
    align-items: center;
    padding: 0 4rem;
    padding-top: 5rem;
  }}
  @media (max-width: 768px) {{
    .hero {{ grid-template-columns: 1fr; padding: 6rem 1.5rem 2rem; text-align: center; }}
  }}
  .hero-left {{
    animation: fadeUp 0.8s ease forwards;
    opacity: 0;
  }}
  @keyframes fadeUp {{
    from {{ opacity: 0; transform: translateY(24px); }}
    to {{ opacity: 1; transform: translateY(0); }}
  }}
  .hero-personality {{
    font-size: 0.75rem; font-family: 'JetBrains Mono', monospace;
    color: var(--accent);
    letter-spacing: 0.15em;
    text-transform: uppercase;
    margin-bottom: 1rem;
  }}
  .hero-tags {{ margin: 1.5rem 0; display: flex; flex-wrap: wrap; gap: 0.5rem; }}
  .tag {{
    font-size: 0.7rem; font-family: 'JetBrains Mono', monospace;
    background: var(--surface);
    border: 1px solid var(--border);
    padding: 0.3rem 0.7rem;
    border-radius: 100px;
    color: var(--muted);
  }}
  .hero-title {{
    font-family: 'Playfair Display', serif;
    font-size: clamp(2.5rem, 5vw, 4rem);
    font-weight: 700;
    line-height: 1.1;
    margin-bottom: 1.5rem;
    background: linear-gradient(135deg, var(--text) 60%, var(--muted));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }}
  .hero-story {{
    font-size: 1.05rem;
    color: var(--muted);
    max-width: 500px;
    line-height: 1.7;
    margin-bottom: 2rem;
  }}
  .hero-canvas {{
    display: flex;
    justify-content: center;
    align-items: center;
    animation: fadeUp 0.8s 0.2s ease forwards;
    opacity: 0;
  }}
  .hero-canvas iframe {{
    width: 100%; max-width: 540px; aspect-ratio: 16/10;
    border: none; border-radius: 12px;
    box-shadow: 0 32px 80px rgba(0,0,0,0.5);
  }}

  /* Sections */
  section {{ padding: 6rem 4rem; border-top: 1px solid var(--border); }}
  @media (max-width: 768px) {{ section {{ padding: 4rem 1.5rem; }} }}
  .section-label {{
    font-size: 0.7rem; font-family: 'JetBrains Mono', monospace;
    color: var(--accent); letter-spacing: 0.15em;
    text-transform: uppercase; margin-bottom: 0.75rem;
  }}
  .section-title {{
    font-family: 'Playfair Display', serif;
    font-size: clamp(1.8rem, 3vw, 2.5rem);
    font-weight: 700; margin-bottom: 2rem;
  }}

  /* Palette */
  .palette-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
    gap: 1rem;
  }}
  .swatch-card {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 10px;
    overflow: hidden;
    transition: transform 0.2s, border-color 0.2s;
  }}
  .swatch-card:hover {{ transform: translateY(-3px); border-color: var(--accent); }}
  .swatch {{ height: 80px; width: 100%; }}
  .swatch-name {{
    display: block; padding: 0.5rem 0.75rem 0.25rem;
    font-size: 0.75rem; font-weight: 600;
    color: var(--text); text-transform: capitalize;
  }}
  .swatch-hex {{
    display: block; padding: 0 0.75rem 0.75rem;
    font-size: 0.65rem; font-family: 'JetBrains Mono', monospace;
    color: var(--muted);
  }}

  /* Taglines */
  .taglines {{
    display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 1.5rem;
  }}
  .tagline {{
    font-family: 'Playfair Display', serif;
    font-size: clamp(1.1rem, 2vw, 1.5rem);
    font-weight: 400; font-style: italic;
    color: var(--text);
    padding: 1.5rem;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 10px;
    display: flex; align-items: baseline; gap: 1rem;
    transition: border-color 0.2s;
  }}
  .tagline:hover {{ border-color: var(--accent); }}
  .tagline-num {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem; color: var(--accent);
    font-style: normal; flex-shrink: 0;
  }}

  /* Brand Story */
  .story-grid {{
    display: grid; grid-template-columns: 1fr 1fr; gap: 3rem;
  }}
  @media (max-width: 768px) {{ .story-grid {{ grid-template-columns: 1fr; }} }}
  .story-text {{
    font-size: 1.1rem; line-height: 1.8;
    color: var(--muted);
  }}
  .rationale-text {{
    font-size: 1rem; line-height: 1.8;
    color: var(--muted);
    border-left: 2px solid var(--accent);
    padding-left: 1.5rem;
  }}

  /* Color Meaning */
  .meaning-grid {{
    display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 1.5rem;
  }}
  .meaning-card {{
    display: flex; gap: 1rem; align-items: flex-start;
    background: var(--surface); border: 1px solid var(--border);
    border-radius: 10px; padding: 1.25rem;
  }}
  .meaning-dot {{
    width: 12px; height: 12px; border-radius: 50%;
    flex-shrink: 0; margin-top: 0.35rem;
  }}
  .meaning-card strong {{
    font-size: 0.85rem; color: var(--text);
    text-transform: capitalize; display: block; margin-bottom: 0.35rem;
  }}
  .meaning-card p {{ font-size: 0.85rem; color: var(--muted); line-height: 1.5; }}

  /* Social Voice */
  .social-card {{
    background: var(--surface); border: 1px solid var(--border);
    border-radius: 12px; padding: 2rem;
    max-width: 600px;
  }}
  .social-tone {{
    font-size: 0.8rem; font-family: 'JetBrains Mono', monospace;
    color: var(--accent); margin-bottom: 1rem;
  }}
  .social-example {{
    font-size: 1.2rem; line-height: 1.6;
    color: var(--text); font-style: italic;
    quotes: "\\201C" "\\201D";
  }}
  .social-example::before {{ content: open-quote; color: var(--accent); }}
  .social-example::after {{ content: close-quote; color: var(--accent); }}

  /* Audio */
  .audio-section {{ max-width: 700px; }}
  .manifesto-text {{
    font-family: 'Playfair Display', serif;
    font-size: clamp(1.1rem, 2vw, 1.4rem);
    font-style: italic; line-height: 1.7;
    color: var(--muted); margin: 1.5rem 0;
  }}
  audio {{
    width: 100%; height: 40px;
    border-radius: 100px; outline: none;
    accent-color: var(--accent);
  }}

  /* Audience & Direction */
  .meta-grid {{
    display: grid; grid-template-columns: 1fr 1fr; gap: 2rem;
  }}
  @media (max-width: 768px) {{ .meta-grid {{ grid-template-columns: 1fr; }} }}
  .meta-card {{
    background: var(--surface); border: 1px solid var(--border);
    border-radius: 10px; padding: 1.5rem;
  }}
  .meta-label {{
    font-size: 0.7rem; font-family: 'JetBrains Mono', monospace;
    color: var(--accent); letter-spacing: 0.1em;
    text-transform: uppercase; margin-bottom: 0.5rem;
  }}
  .meta-value {{
    font-size: 0.95rem; color: var(--muted); line-height: 1.5;
  }}

  /* Download */
  .download-section {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 2rem;
    display: flex;
    flex-wrap: wrap;
    gap: 1rem;
    align-items: center;
  }}
  .download-btn {{
    display: inline-flex; align-items: center; gap: 0.5rem;
    padding: 0.6rem 1.2rem;
    background: var(--primary);
    color: var(--bg);
    text-decoration: none;
    border-radius: 8px;
    font-size: 0.85rem; font-weight: 600;
    transition: opacity 0.2s, transform 0.2s;
  }}
  .download-btn:hover {{ opacity: 0.85; transform: translateY(-1px); }}

  /* Footer */
  footer {{
    text-align: center; padding: 3rem;
    border-top: 1px solid var(--border);
    font-size: 0.8rem; color: #555;
  }}
  footer a {{ color: var(--accent); text-decoration: none; }}
</style>
</head>
<body>

<nav>
  <a href="/" class="nav-logo">Atelier</a>
  <span class="nav-badge">AI Creative Director</span>
</nav>

<!-- HERO -->
<div class="hero">
  <div class="hero-left">
    <div class="hero-personality">{personality.upper()}</div>
    <h1 class="hero-title">{analysis.get("visual_direction", "").split(",")[0] or "Creative Identity"}</h1>
    <div class="hero-tags">{tags_html}</div>
    <p class="hero-story">{brand_story}</p>
  </div>
  <div class="hero-canvas">
    {'<iframe src="visual.html" title="Brand Visual"></iframe>' if visual_exists else '<div style="width:100%;max-width:540px;aspect-ratio:16/10;background:var(--surface);border-radius:12px;display:flex;align-items:center;justify-content:center;color:var(--muted);font-size:0.85rem;">Visual generation</div>'}
  </div>
</div>

<!-- PALETTE -->
<section>
  <div class="section-label">Color System</div>
  <h2 class="section-title">Brand Palette</h2>
  <div class="palette-grid">{palette_html}</div>
</section>

<!-- TAGLINES -->
<section>
  <div class="section-label">Brand Voice</div>
  <h2 class="section-title">Taglines</h2>
  <div class="taglines">{taglines_html}</div>
</section>

<!-- STORY & RATIONALE -->
<section>
  <div class="section-label">Narrative</div>
  <h2 class="section-title">Brand Story</h2>
  <div class="story-grid">
    <div>
      <p class="story-text">{brand_story}</p>
    </div>
    <div>
      <p class="rationale-text">{rationale}</p>
    </div>
  </div>
</section>

<!-- COLOR MEANING -->
<section>
  <div class="section-label">Emotional Logic</div>
  <h2 class="section-title">Why These Colors</h2>
  <div class="meaning-grid">{color_meaning_html}</div>
</section>

<!-- SOCIAL VOICE -->
<section>
  <div class="section-label">Tone & Voice</div>
  <h2 class="section-title">Social Media Presence</h2>
  <div class="social-card">
    <div class="social-tone">TONE: {social.get("tone", "Distinctive")}</div>
    <blockquote class="social-example">{social.get("example_post", "")}</blockquote>
  </div>
</section>

<!-- AUDIO -->
{audio_html}

<!-- META -->
<section>
  <div class="section-label">Creative Direction</div>
  <h2 class="section-title">Target & Position</h2>
  <div class="meta-grid">
    <div class="meta-card">
      <div class="meta-label">Target Audience</div>
      <div class="meta-value">{analysis.get("target_audience", "")}</div>
    </div>
    <div class="meta-card">
      <div class="meta-label">Competitive Position</div>
      <div class="meta-value">{analysis.get("competitive_position", "")}</div>
    </div>
    <div class="meta-card">
      <div class="meta-label">Motion Style</div>
      <div class="meta-value">{analysis.get("motion_style", "balanced")} · Complexity {int(analysis.get("complexity", 0.5)*100)}% · Energy {int(analysis.get("energy", 0.5)*100)}%</div>
    </div>
    <div class="meta-card">
      <div class="meta-label">Typography</div>
      <div class="meta-value">{analysis.get("typography", {}).get("heading_style", "sans-serif").capitalize()} headings · {analysis.get("typography", {}).get("body_style", "sans-serif").capitalize()} body · {analysis.get("typography", {}).get("weight_feel", "regular")} weight</div>
    </div>
  </div>
</section>

<!-- DOWNLOAD -->
<section>
  <div class="section-label">Export</div>
  <h2 class="section-title">Download Assets</h2>
  <div class="download-section">
    <a href="visual.html" download class="download-btn">Visual HTML</a>
    <a href="palette.json" download class="download-btn">Palette JSON</a>
    <a href="analysis.json" download class="download-btn">Analysis JSON</a>
    <a href="narrative.json" download class="download-btn">Narrative JSON</a>
    {'<a href="preview.png" download class="download-btn">Preview PNG</a>' if preview_exists else ""}
    {'<a href="manifesto.mp3" download class="download-btn">Manifesto MP3</a>' if manifesto_exists else ""}
  </div>
</section>

<footer>
  Generated by <a href="https://atelier.ko4lax.dev">Atelier</a> ·
  Powered by Kimi K2.5 + p5.js + Hermes Agent ·
  <a href="https://github.com/Dreamvalian/atelier">GitHub</a>
</footer>

</body>
</html>'''

    out_path = os.path.join(base, "index.html")
    with open(out_path, "w") as f:
        f.write(html)

    # Sync to webroot (single source of truth — only this function syncs)
    webroot = os.path.join("/var/www/atelier", os.path.basename(base))
    os.makedirs(webroot, exist_ok=True)
    import shutil
    sync_files = ["index.html", "visual.html", "palette.json", "analysis.json", "narrative.json"]
    if preview_exists:
        sync_files.append("preview.png")
    if manifesto_exists:
        sync_files.append("manifesto.mp3")
    for fname in sync_files:
        src = os.path.join(base, fname)
        if os.path.exists(src):
            shutil.copy2(src, webroot)

    return out_path
