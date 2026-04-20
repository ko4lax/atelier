#!/usr/bin/env python3
"""Animated Atelier demo video compiler.
Creates Ken Burns effect clips, animated title cards, and compiles with transitions."""

import subprocess, os, sys, json

D = "/root/atelier/demo"
FRAMES = f"{D}/frames"
CLIPS = f"{D}/clips"
OUT = f"{D}/atelier-demo-animated.mp4"
W, H = 1920, 1080
FPS = 30
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

os.makedirs(CLIPS, exist_ok=True)

def cmd(c, label=""):
    r = subprocess.run(c, shell=True, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"  ✗ {label}: {r.stderr[:200]}")
        return False
    return True

def probe_dur(path):
    r = subprocess.run(
        f'ffprobe -v error -show_entries format=duration -of json "{path}"',
        shell=True, capture_output=True, text=True
    )
    try:
        return float(json.loads(r.stdout)["format"]["duration"])
    except:
        return 0

# ─────────────────────────────────────────────
# STEP 1: Title cards
# ─────────────────────────────────────────────
print("[1/3] Title cards")

titles = [
    ("title_intro", 5, "ATELIER", "AI Creative Director Agent", "#d4a574", "#888888"),
    ("title_how", 4.5, "How It Works", "Brief \u2192 Kimi Analysis \u2192 Visual Identity", "#ffffff", "#777777"),
    ("title_kimi", 5, "Powered by Kimi", "Moonshot AI's frontier model for creative analysis", "#7eb8da", "#777777"),
    ("title_memory", 4.5, "Persistent Memory", "Learns your aesthetic preferences over time", "#ffffff", "#777777"),
    ("title_modes", 4.5, "5 Visual Modes", "Minimal \u00b7 Organic \u00b7 Bold \u00b7 Glitch \u00b7 Ink", "#ffffff", "#777777"),
    ("title_end", 7, "ATELIER", "atelier.ko4lax.dev  |  github.com/Dreamvalian/atelier\nHermes Agent Creative Hackathon 2026", "#d4a574", "#888888"),
]

for name, dur, title, sub, tc, sc in titles:
    out = f"{CLIPS}/{name}.mp4"
    if os.path.exists(out) and probe_dur(out) > 0:
        print(f"  ✓ {name} (cached)")
        continue

    te = title.replace("'", "\u2019").replace(":", "\\:")
    se_lines = sub.split("\n")

    vf = f""  # Input provides the color, we add drawtext + fade
    # Title: centered, fade in at 0.3s over 0.6s
    vf += f"drawtext=text='{te}':fontsize=72:fontcolor={tc}:"
    vf += f"fontfile={FONT_BOLD}:x=(w-text_w)/2:y=(h-text_h)/2-50:"
    vf += f"alpha='if(lt(t\\,0.3)\\,0\\,if(lt(t\\,0.9)\\,(t-0.3)/0.6\\,1))',"

    # Subtitle lines
    for i, line in enumerate(se_lines):
        le = line.replace("'", "\u2019").replace(":", "\\:")
        yoff = 50 + i * 40
        vf += f"drawtext=text='{le}':fontsize=26:fontcolor={sc}:"
        vf += f"fontfile={FONT}:x=(w-text_w)/2:y=(h-text_h)/2+{yoff}:"
        vf += f"alpha='if(lt(t\\,0.6)\\,0\\,if(lt(t\\,1.2)\\,(t-0.6)/0.6\\,1))',"

    # Fade in/out
    vf += f"fade=t=in:st=0:d=0.4,fade=t=out:st={dur-0.5}:d=0.5"

    ok = cmd(
        f'ffmpeg -y -f lavfi -i "color=c=0x080810:s={W}x{H}:d={dur}:r={FPS}" -vf "{vf}" '
        f'-c:v libx264 -pix_fmt yuv420p -preset fast -t {dur} "{out}" 2>/dev/null',
        name
    )
    print(f"  {'✓' if ok else '✗'} {name}")

# ─────────────────────────────────────────────
# STEP 2: Ken Burns clips from screenshots
# ─────────────────────────────────────────────
print("\n[2/3] Ken Burns clips")

clips_def = [
    ("scene_home",     "01_home.png",     6,   1.0, 1.08, ""),
    ("scene_filled",   "02_filled.png",   7,   1.0, 1.05, "User submits a creative brief..."),
    ("scene_loading",  "03_loading.png",  5,   1.0, 1.15, "Kimi analyzes brand DNA..."),
    ("scene_result",   "04_result_top.png",7,  1.0, 1.06, "Brand Identity Generated"),
    ("scene_palette",  "05_palette.png",  6,   1.0, 1.07, "Color palette from brand essence"),
    ("scene_taglines", "06_taglines.png", 6,   1.08,1.0,  "Taglines, social voice, brand story"),
    ("scene_story",    "07_story.png",    6,   1.0, 1.08, ""),
    ("scene_feedback", "08_feedback.png", 6,   1.0, 1.06, "Feedback shapes future generations"),
]

for name, frame, dur, z0, z1, caption in clips_def:
    out = f"{CLIPS}/{name}.mp4"
    src = f"{FRAMES}/{frame}"
    if os.path.exists(out) and probe_dur(out) > 0:
        print(f"  ✓ {name} (cached)")
        continue

    if not os.path.exists(src):
        print(f"  ✗ {name}: missing {frame}")
        continue

    total_f = int(dur * FPS)
    # Zoom expression: linear interpolation
    zexpr = f"{z0}+({z1}-{z0})*on/{total_f}"

    vf = f"scale={int(W*1.35)}:{int(H*1.35)},"
    vf += f"zoompan=z='{zexpr}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
    vf += f":d={total_f}:s={W}x{H}:fps={FPS},"

    if caption:
        ce = caption.replace("'", "\u2019").replace(":", "\\:")
        vf += f"drawtext=text='{ce}':fontsize=24:fontcolor=#cccccc:"
        vf += f"box=1:boxcolor=black@0.65:boxborderw=10:"
        vf += f"fontfile={FONT}:x=(w-text_w)/2:y=h-80:"
        vf += f"alpha='if(lt(t\\,0.5)\\,0\\,if(lt(t\\,1.0)\\,(t-0.5)/0.5\\,1))',"

    vf += f"fade=t=in:st=0:d=0.5,fade=t=out:st={dur-0.5}:d=0.5"

    ok = cmd(
        f'ffmpeg -y -loop 1 -i "{src}" -vf "{vf}" '
        f'-c:v libx264 -pix_fmt yuv420p -preset fast -t {dur} "{out}" 2>/dev/null',
        name
    )
    print(f"  {'✓' if ok else '✗'} {name}")

# ─────────────────────────────────────────────
# STEP 2.5: Terminal / Kimi API scene
# ─────────────────────────────────────────────
print("\n[2.5] Terminal scene (Kimi API)")

# Create a terminal-style scene showing Kimi API call
term_dur = 7
term_out = f"{CLIPS}/scene_terminal.mp4"
if not (os.path.exists(term_out) and probe_dur(term_out) > 0):
    # Build terminal text lines that "appear" via drawtext at different times
    lines = [
        (0.0, "$ atelier --brief 'minimal luxury watch'", "#00ff41"),
        (0.8, "Analyzing brand DNA...", "#7eb8da"),
        (1.5, "Connecting to Kimi API (moonshot-v1-128k)...", "#7eb8da"),
        (2.2, "Model: kimi-k2.5 | Thinking: disabled", "#888888"),
        (3.0, "Extracting brand personality...", "#ffffff"),
        (3.8, "Deriving color palette from emotional analysis...", "#ffffff"),
        (4.5, "Generating 3 taglines + brand narrative...", "#ffffff"),
        (5.2, "Building p5.js visual identity...", "#d4a574"),
        (6.0, "Done. Brand identity complete.", "#00ff41"),
    ]

    vf = ""
    for i, (t, text, color) in enumerate(lines):
        te = text.replace("'", "\u2019").replace(":", "\\:")
        y = 60 + i * 42
        # Each line fades in at its time
        fade_start = t
        fade_end = t + 0.4
        vf += f"drawtext=text='{te}':fontsize=22:fontcolor={color}:"
        vf += f"fontfile={FONT}:x=60:y={y}:"
        vf += f"enable='gte(t\\,{fade_start})':"
        vf += f"alpha='if(lt(t\\,{fade_end})\\,(t-{fade_start})/{fade_end-fade_start}\\,1)',"

    vf += f"fade=t=in:st=0:d=0.3,fade=t=out:st={term_dur-0.5}:d=0.5"

    ok = cmd(
        f'ffmpeg -y -f lavfi -i "color=c=0x0d1117:s={W}x{H}:d={term_dur}:r={FPS}" -vf "{vf}" '
        f'-c:v libx264 -pix_fmt yuv420p -preset fast -t {term_dur} "{term_out}" 2>/dev/null',
        "scene_terminal"
    )
    print(f"  {'✓' if ok else '✗'} scene_terminal")

# ─────────────────────────────────────────────
# STEP 3: Compile with concat + global polish
# ─────────────────────────────────────────────
print("\n[3/3] Compiling final video")

# Ordered scene list
order = [
    "title_intro",       # ATELIER title
    "title_how",         # How It Works
    "scene_home",        # Home page
    "scene_filled",      # Brief filled
    "scene_loading",     # Generating
    "scene_terminal",    # Kimi API terminal (Track proof)
    "title_kimi",        # Powered by Kimi
    "scene_result",      # Result hero
    "scene_palette",     # Palette
    "scene_taglines",    # Taglines
    "scene_story",       # Brand story
    "title_memory",      # Memory
    "scene_feedback",    # Feedback
    "title_modes",       # Visual modes
    "title_end",         # End card
]

# Verify all clips exist
missing = []
for name in order:
    p = f"{CLIPS}/{name}.mp4"
    if not os.path.exists(p) or probe_dur(p) == 0:
        missing.append(name)

if missing:
    print(f"✗ Missing clips: {missing}")
    sys.exit(1)

# Write concat file
concat_file = f"{CLIPS}/concat.txt"
total_dur = 0
with open(concat_file, "w") as f:
    for name in order:
        p = f"{CLIPS}/{name}.mp4"
        d = probe_dur(p)
        total_dur += d
        f.write(f"file '{p}'\n")

print(f"  Clips: {len(order)}, Duration: {total_dur:.1f}s")

# Compile with concat + final polish
# Add subtle film grain and final fade
fade_out_start = total_dur - 1.0
cmd_str = (
    f'ffmpeg -y -f concat -safe 0 -i "{concat_file}" '
    f'-vf "eq=brightness=0.02:saturation=1.05,'
    f'fade=t=in:st=0:d=0.3,'
    f'fade=t=out:st={fade_out_start:.2f}:d=1.0,'
    f'format=yuv420p" '
    f'-c:v libx264 -crf 18 -preset medium -pix_fmt yuv420p '
    f'-movflags +faststart '
    f'"{OUT}" 2>&1'
)

r = subprocess.run(cmd_str, shell=True, capture_output=True, text=True)

if r.returncode == 0 and os.path.exists(OUT):
    size = os.path.getsize(OUT)
    final_dur = probe_dur(OUT)
    print(f"\n{'='*50}")
    print(f"✓ DONE: {OUT}")
    print(f"  Duration: {final_dur:.1f}s ({final_dur/60:.1f} min)")
    print(f"  Size: {size/1024:.0f} KB ({size/1024/1024:.1f} MB)")
    print(f"  Resolution: {W}x{H}")
    print(f"  Clips: {len(order)}")
    print(f"{'='*50}")
else:
    print(f"\n✗ Compile failed: {r.stderr[-300:]}")
    sys.exit(1)
