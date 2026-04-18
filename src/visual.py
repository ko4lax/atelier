"""
Visual generation for Atelier — p5.js generative art based on brand analysis.

BUG FIXES:
- All p5.js fill()/background()/stroke() calls now use HSB numeric values,
  not hex strings (hex was misinterpreted in HSB colorMode — p5.js parses
  "#ff0000" as H=255,S=100,B=100 instead of red).
- Bold template: fixed double fill() call in center glow (second overwrote first).
- generate_palette_colors: now writes HSB-aware palette; hex colors converted
  to {h, s, b} objects for safe p5.js injection.
"""

import os
import json


VISUAL_MODES = {
    "minimal": {
        "description": "Geometric compositions with clean lines, negative space, and controlled motion",
        "template": "minimal",
    },
    "organic": {
        "description": "Flowing curves, noise-driven patterns, breathing animations, natural textures",
        "template": "organic",
    },
    "bold": {
        "description": "High contrast, particle systems, dynamic motion, explosive energy",
        "template": "bold",
    },
}


def hue_to_hex(hue, sat=70, bri=85):
    """Convert HSB to hex color string."""
    import colorsys
    h = hue / 360.0
    s = sat / 100.0
    v = bri / 100.0
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    return f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"


def _hex_to_hsb(hex_color):
    """Convert hex color string to HSB dict for p5.js injection."""
    hex_color = hex_color.lstrip("#")
    r = int(hex_color[0:2], 16) / 255.0
    g = int(hex_color[2:4], 16) / 255.0
    b = int(hex_color[4:6], 16) / 255.0
    import colorsys
    H, S, V = colorsys.rgb_to_hsv(r, g, b)
    return {"h": round(H * 360), "s": round(S * 100), "b": round(V * 100)}


def generate_palette_colors(analysis):
    """Generate palette dict with hex + HSB values for p5.js.
    
    The 'hsb' object uses the BRAND palette values directly for h/s/b
    (saturation/brightness as the brand intended), NOT re-computed from hex.
    The 'hex' object is for CSS/display only.
    """
    palette = analysis.get("palette", {})
    primary_hue = palette.get("primary_hue", 210)
    secondary_hue = palette.get("secondary_hue", (primary_hue + 30) % 360)
    accent_hue = palette.get("accent_hue", (primary_hue + 180) % 360)
    sat = palette.get("saturation", 50)
    bri = palette.get("brightness", 80)

    # Derive bg/muted from primary (shifted lightness)
    bg_sat = max(10, sat - 40)
    bg_bri = max(8, bri - 70)
    muted_sat = max(5, sat - 30)
    muted_bri = max(30, bri - 30)
    text_bri = 95
    text_sat = 15

    bg_hex = hue_to_hex(primary_hue, bg_sat, bg_bri)
    primary_hex = hue_to_hex(primary_hue, sat, bri)
    secondary_hex = hue_to_hex(secondary_hue, max(20, sat - 15), bri)
    accent_hex = hue_to_hex(accent_hue, min(100, sat + 20), bri)
    text_hex = hue_to_hex(primary_hue, text_sat, text_bri)
    muted_hex = hue_to_hex(primary_hue, muted_sat, muted_bri)

    return {
        "hex": {
            "bg": bg_hex,
            "primary": primary_hex,
            "secondary": secondary_hex,
            "accent": accent_hex,
            "text": text_hex,
            "muted": muted_hex,
        },
        # Use raw brand palette values for HSB — NOT re-computed from hex
        # (hex conversion loses the original saturation/brightness modifiers)
        "hsb": {
            "bg":     {"h": primary_hue, "s": bg_sat,     "b": bg_bri},
            "primary": {"h": primary_hue, "s": sat,         "b": bri},
            "secondary": {"h": secondary_hue, "s": max(20, sat - 15), "b": bri},
            "accent": {"h": accent_hue,  "s": min(100, sat + 20), "b": bri},
            "text":   {"h": primary_hue, "s": text_sat,   "b": text_bri},
            "muted":  {"h": primary_hue, "s": muted_sat,  "b": muted_bri},
        },
        # Raw brand palette values (for direct template use)
        "raw": {
            "primary_hue": primary_hue,
            "secondary_hue": secondary_hue,
            "accent_hue": accent_hue,
            "sat": sat,
            "bri": bri,
        },
    }


def _minimal_template(colors, analysis):
    """Minimal p5.js visual — geometric, clean, spacious."""
    complexity = analysis.get("complexity", 0.5)
    energy = analysis.get("energy", 0.3)
    motion = analysis.get("motion_style", "slow-drift")

    num_shapes = int(5 + complexity * 15)
    speed = 0.2 + energy * 0.8
    has_motion = motion != "static"

    # HSB values for p5.js (safe — no hex misinterpretation)
    bg = colors["hsb"]["bg"]
    primary = colors["hsb"]["primary"]
    accent = colors["hsb"]["accent"]

    return f'''<!DOCTYPE html>
<html><head><meta charset="UTF-8">
<title>Atelier — Minimal</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/p5.js/1.11.3/p5.min.js"></script>
<style>html,body{{margin:0;padding:0;overflow:hidden;background:{colors["hex"]["bg"]};}}</style>
</head><body><script>
p5.disableFriendlyErrors = true;
const HSB = {json.dumps(colors["hsb"])};
const N = {num_shapes};
const SPEED = {speed};
const MOTION = {str(has_motion).lower()};
let shapes = [];

function setup() {{
  createCanvas(windowWidth, windowHeight);
  colorMode(HSB, 360, 100, 100, 100);
  noStroke();
  for (let i = 0; i < N; i++) {{
    shapes.push({{
      x: random(width * 0.15, width * 0.85),
      y: random(height * 0.15, height * 0.85),
      size: random(40, min(width, height) * 0.25),
      type: floor(random(3)),
      phase: random(TWO_PI),
      speed: random(0.3, 1) * SPEED,
      hueShift: random(-20, 20),
    }});
  }}
}}

function draw() {{
  background({bg["h"]}, {bg["s"]}, {bg["b"]});
  let t = MOTION ? millis() * 0.001 : 0;

  for (let s of shapes) {{
    push();
    let ox = MOTION ? sin(t * s.speed + s.phase) * 20 : 0;
    let oy = MOTION ? cos(t * s.speed * 0.7 + s.phase) * 15 : 0;
    translate(s.x + ox, s.y + oy);

    // Shadow (low-opacity black)
    fill(0, 0, 0, 8);
    if (s.type === 0) ellipse(4, 4, s.size);
    else if (s.type === 1) rect(-s.size/2 + 4, -s.size/2 + 4, s.size, s.size);
    else rect(-s.size/2 + 4, -s.size/3 + 4, s.size, s.size * 0.66);

    // Shape (primary brand color)
    fill({primary["h"]}, {primary["s"]}, {primary["b"]});
    if (s.type === 0) ellipse(0, 0, s.size);
    else if (s.type === 1) rect(-s.size/2, -s.size/2, s.size, s.size);
    else rect(-s.size/2, -s.size/3, s.size, s.size * 0.66);
    pop();
  }}

  // Accent line
  stroke({accent["h"]}, {accent["s"]}, {accent["b"]});
  strokeWeight(1);
  let lx = width * 0.3 + (MOTION ? sin(t * 0.5) * 50 : 0);
  line(lx, height * 0.2, lx, height * 0.8);
  noStroke();
}}

function windowResized() {{ resizeCanvas(windowWidth, windowHeight); }}
function keyPressed() {{ if (key === 's') saveCanvas('atelier-minimal', 'png'); }}
</script></body></html>'''


def _organic_template(colors, analysis):
    """Organic p5.js visual — flow fields, curves, breathing."""
    complexity = analysis.get("complexity", 0.5)
    energy = analysis.get("energy", 0.5)

    num_particles = int(200 + complexity * 500)
    noise_scale = 0.003 + (1 - complexity) * 0.005

    bg = colors["hsb"]["bg"]
    primary = colors["hsb"]["primary"]
    accent = colors["hsb"]["accent"]

    return f'''<!DOCTYPE html>
<html><head><meta charset="UTF-8">
<title>Atelier — Organic</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/p5.js/1.11.3/p5.min.js"></script>
<style>html,body{{margin:0;padding:0;overflow:hidden;background:{colors["hex"]["bg"]};}}</style>
</head><body><script>
p5.disableFriendlyErrors = true;
const HSB = {json.dumps(colors["hsb"])};
const N = {num_particles};
const NS = {noise_scale};
let particles = [];

function setup() {{
  createCanvas(windowWidth, windowHeight);
  colorMode(HSB, 360, 100, 100, 100);
  for (let i = 0; i < N; i++) {{
    particles.push({{
      x: random(width), y: random(height),
      hueShift: random(-15, 15), alpha: random(15, 40),
      life: random(100, 400), age: 0,
    }});
  }}
  background({bg["h"]}, {bg["s"]}, {bg["b"]});
}}

function draw() {{
  background({bg["h"]}, {bg["s"]}, {bg["b"]});
  let t = millis() * 0.0003;

  for (let p of particles) {{
    let angle = noise(p.x * NS, p.y * NS, t) * TWO_PI * 2;
    p.x += cos(angle) * 1.5;
    p.y += sin(angle) * 1.5;
    p.age++;

    // Wrap bounds
    if (p.x < 0) p.x = width;
    if (p.x > width) p.x = 0;
    if (p.y < 0) p.y = height;
    if (p.y > height) p.y = 0;

    // Reset dead particles
    if (p.age > p.life) {{
      p.x = random(width); p.y = random(height);
      p.age = 0; p.life = random(100, 400);
    }}

    let a = p.alpha * (1 - p.age / p.life);
    // Particle: primary hue shifted by noise, brand saturation/brightness
    let ph = ({primary["h"]} + p.hueShift + 360) % 360;
    stroke(ph, {primary["s"]}, {primary["b"]}, a);
    strokeWeight(1.2);
    point(p.x, p.y);
  }}
}}

function windowResized() {{ resizeCanvas(windowWidth, windowHeight); background({bg["h"]}, {bg["s"]}, {bg["b"]}); }}
function keyPressed() {{ if (key === 's') saveCanvas('atelier-organic', 'png'); }}
</script></body></html>'''


def _bold_template(colors, analysis):
    """Bold p5.js visual — particles, high contrast, explosive."""
    complexity = analysis.get("complexity", 0.5)
    energy = analysis.get("energy", 0.8)

    num_particles = int(100 + complexity * 300)

    bg = colors["hsb"]["bg"]
    primary = colors["hsb"]["primary"]
    accent = colors["hsb"]["accent"]
    secondary = colors["hsb"]["secondary"]
    raw = colors["raw"]

    # Particle hues: mix primary, accent, and secondary brand hues
    hue_array = [
        raw["primary_hue"],
        raw["accent_hue"],
        (raw["primary_hue"] + 30) % 360,
        (raw["accent_hue"] + 15) % 360,
    ]

    return f'''<!DOCTYPE html>
<html><head><meta charset="UTF-8">
<title>Atelier — Bold</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/p5.js/1.11.3/p5.min.js"></script>
<style>html,body{{margin:0;padding:0;overflow:hidden;background:{colors["hex"]["bg"]};}}</style>
</head><body><script>
p5.disableFriendlyErrors = true;
const HSB = {json.dumps(colors["hsb"])};
const RAW = {json.dumps(colors["raw"])};
const N = {num_particles};
const HUE_ARRAY = {json.dumps(hue_array)};
let particles = [];

function setup() {{
  createCanvas(windowWidth, windowHeight);
  colorMode(HSB, 360, 100, 100, 100);
  for (let i = 0; i < N; i++) {{
    particles.push({{
      x: width/2, y: height/2,
      vx: random(-6, 6), vy: random(-6, 6),
      size: random(3, 12),
      hue: random(HUE_ARRAY),
      life: random(60, 200), age: 0,
    }});
  }}
  background({bg["h"]}, {bg["s"]}, {bg["b"]});
}}

function draw() {{
  background({bg["h"]}, {bg["s"]}, {bg["b"]});

  for (let i = particles.length - 1; i >= 0; i--) {{
    let p = particles[i];
    p.x += p.vx;
    p.y += p.vy;
    p.vx *= 0.99;
    p.vy *= 0.99;
    p.age++;

    let lifeRatio = p.age / p.life;
    let a = 80 * (1 - lifeRatio);
    let sz = p.size * (1 - lifeRatio * 0.5);
    fill(p.hue, {primary["s"]}, {primary["b"]}, a);
    noStroke();
    ellipse(p.x, p.y, sz);

    if (p.age > p.life || p.x < -50 || p.x > width+50 || p.y < -50 || p.y > height+50) {{
      particles.splice(i, 1);
      particles.push({{
        x: width/2 + random(-30,30), y: height/2 + random(-30,30),
        vx: random(-6, 6), vy: random(-6, 6),
        size: random(3, 12),
        hue: random(HUE_ARRAY),
        life: random(60, 200), age: 0,
      }});
    }}
  }}

  // Center glow — radial gradient using brand accent color
  noStroke();
  for (let r = 80; r > 0; r -= 4) {{
    let a = map(r, 80, 0, 1, 25);
    fill({accent["h"]}, {accent["s"]}, {accent["b"]}, a);
    ellipse(width/2, height/2, r * 2);
  }}
}}

function windowResized() {{ resizeCanvas(windowWidth, windowHeight); }}
function keyPressed() {{
  if (key === 's') saveCanvas('atelier-bold', 'png');
  if (key === ' ') {{
    for (let p of particles) {{
      p.vx = random(-8, 8); p.vy = random(-8, 8);
    }}
  }}
}}
</script></body></html>'''


TEMPLATES = {
    "minimal": _minimal_template,
    "organic": _organic_template,
    "bold": _bold_template,
}


def generate_visual(analysis, output_dir):
    """Generate p5.js visual from brand analysis. Returns info dict."""
    personality = analysis.get("brand_personality", "minimal")
    # weight_feel lives at top level of analysis (typography.weight_feel was a schema field)
    weight_feel = analysis.get("weight_feel", "") or analysis.get("typography", {}).get("weight_feel", "")
    energy = analysis.get("energy", 0.5)

    # Map personality + weight_feel to visual mode
    mode_map = {
        "minimal": "minimal",
        "technical": "minimal",
        "luxurious": "minimal",
        "organic": "organic",
        "warm": "organic",
        "bold": "bold",
        "edgy": "bold",
        "playful": "bold",
    }
    if weight_feel in ("bold", "edgy"):
        mode = "bold"
    elif energy >= 0.8:
        mode = "bold"
    else:
        mode = mode_map.get(personality, "minimal")

    colors = generate_palette_colors(analysis)
    template_fn = TEMPLATES[mode]
    html = template_fn(colors, analysis)

    # Write visual HTML
    filepath = os.path.join(output_dir, "visual.html")
    with open(filepath, "w") as f:
        f.write(html)

    # NOTE: palette.json is written by atelier.py (HSB raw format) — not here.
    # This avoids schema conflicts and double-writes.
    # NOTE: webroot sync happens once in assemble.py — not here.

    return {
        "file": filepath,
        "mode": mode,
        "colors": colors,
        "description": VISUAL_MODES[mode]["description"],
    }
