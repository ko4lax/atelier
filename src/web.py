"""
Atelier Web UI — Flask frontend for the AI Creative Director.

Endpoints:
  GET  /              — Home page (brief form)
  POST /generate      — Run pipeline, redirect to session
  GET  /session/<id>  — View generated brand guide
  POST /feedback      — Submit feedback to memory system
  GET  /api/generate  — JSON API for programmatic access
"""

import os
import sys
import json
import uuid
from datetime import datetime

from flask import Flask, request, redirect, url_for, render_template_string, jsonify, send_from_directory

# Add src to path for imports
sys.path.insert(0, os.path.dirname(__file__))
from atelier import run_atelier
from memory import load_memory, update_preferences, get_preferences

app = Flask(__name__)
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "output")

HOME_HTML = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Atelier — AI Creative Director</title>
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=Playfair+Display:ital,wght@0,400;0,700;1,400&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    font-family: 'Space Grotesk', sans-serif;
    background: #0a0a0f; color: #e8e8ec;
    min-height: 100vh; display: flex; flex-direction: column;
    align-items: center; justify-content: center;
    padding: 2rem;
  }
  .container { max-width: 640px; width: 100%; }
  .logo {
    font-family: 'Playfair Display', serif;
    font-size: 3.5rem; font-weight: 700;
    margin-bottom: 0.5rem;
    background: linear-gradient(135deg, #fff 60%, #888);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  }
  .subtitle {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem; color: #666;
    letter-spacing: 0.15em; text-transform: uppercase;
    margin-bottom: 3rem;
  }
  .form-group { margin-bottom: 1.5rem; }
  label {
    display: block; font-size: 0.7rem;
    font-family: 'JetBrains Mono', monospace;
    color: #888; letter-spacing: 0.1em;
    text-transform: uppercase; margin-bottom: 0.5rem;
  }
  textarea, input[type="text"] {
    width: 100%; padding: 1rem;
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 10px; color: #e8e8ec;
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1rem; resize: vertical;
    transition: border-color 0.2s;
  }
  textarea:focus, input[type="text"]:focus {
    outline: none; border-color: rgba(255,255,255,0.3);
  }
  textarea { min-height: 120px; }
  .btn {
    display: inline-flex; align-items: center; gap: 0.5rem;
    padding: 0.8rem 2rem;
    background: #4a9eff; color: #0a0a0f;
    border: none; border-radius: 8px;
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.95rem; font-weight: 600;
    cursor: pointer; transition: opacity 0.2s, transform 0.2s;
  }
  .btn:hover { opacity: 0.85; transform: translateY(-1px); }
  .btn:disabled { opacity: 0.4; cursor: not-allowed; }
  .examples {
    margin-top: 3rem; padding-top: 2rem;
    border-top: 1px solid rgba(255,255,255,0.07);
  }
  .examples-title {
    font-size: 0.65rem; font-family: 'JetBrains Mono', monospace;
    color: #555; letter-spacing: 0.1em; text-transform: uppercase;
    margin-bottom: 1rem;
  }
  .example {
    display: inline-block; padding: 0.4rem 0.8rem;
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 100px; font-size: 0.8rem; color: #888;
    margin: 0.25rem; cursor: pointer; transition: border-color 0.2s;
  }
  .example:hover { border-color: rgba(255,255,255,0.2); color: #bbb; }
  .loading { display: none; margin-top: 1rem; color: #666; font-size: 0.85rem; }
  .loading.active { display: block; }
</style>
</head>
<body>
<div class="container">
  <div class="logo">Atelier</div>
  <div class="subtitle">AI Creative Director</div>

  <form method="POST" action="/generate" id="gen-form">
    <div class="form-group">
      <label>Brand Brief</label>
      <textarea name="brief" placeholder="Describe your brand, product, or vision. Be specific or be vague — Atelier reads between the lines." required></textarea>
    </div>
    <div class="form-group">
      <label>User ID (for memory)</label>
      <input type="text" name="user_id" value="default" placeholder="your-name">
    </div>
    <button type="submit" class="btn" id="submit-btn">Generate Identity</button>
    <div class="loading" id="loading">Generating... this takes 15-30 seconds.</div>
  </form>

  <div class="examples">
    <div class="examples-title">Try these</div>
    <span class="example" onclick="fill('minimal luxury watch brand for professionals')">minimal luxury watch</span>
    <span class="example" onclick="fill('organic coffee shop with warm vibes and community feel')">organic coffee shop</span>
    <span class="example" onclick="fill('bold rebellious streetwear brand for Gen Z')">bold streetwear</span>
    <span class="example" onclick="fill('glitchy cyberpunk VR game for hardcore gamers')">glitchy cyberpunk game</span>
    <span class="example" onclick="fill('ink-wash tea ceremony brand with zen aesthetics')">ink tea ceremony</span>
  </div>
</div>
<script>
function fill(text) {
  document.querySelector('textarea[name="brief"]').value = text;
}
document.getElementById('gen-form').addEventListener('submit', function() {
  document.getElementById('submit-btn').disabled = true;
  document.getElementById('loading').classList.add('active');
});
</script>
</body>
</html>'''


@app.route("/")
def home():
    return HOME_HTML


@app.route("/generate", methods=["POST"])
def generate():
    brief = request.form.get("brief", "").strip()
    user_id = request.form.get("user_id", "default").strip()

    if not brief:
        return redirect(url_for("home"))

    try:
        result = run_atelier(brief, user_id)
        if result is None:
            return "Generation failed — check API key and try again.", 500
        session_id = result["session_id"]
        return redirect(url_for("session_page", session_id=session_id))
    except Exception as e:
        return f"Error: {e}", 500


@app.route("/session/<session_id>")
def session_page(session_id):
    session_dir = os.path.join(OUTPUT_DIR, session_id)
    index_path = os.path.join(session_dir, "index.html")

    if not os.path.exists(index_path):
        return "Session not found", 404

    with open(index_path) as f:
        html = f.read()

    # Inject feedback form before </body> and base tag for relative assets
    base_tag = f'<base href="/session/{session_id}/">'
    html = html.replace("</head>", base_tag + "\n</head>")
    feedback_html = f'''
<!-- Feedback Section -->
<section style="padding: 4rem 2rem; border-top: 1px solid rgba(255,255,255,0.07); max-width: 800px; margin: 0 auto;">
  <div style="font-size: 0.7rem; font-family: 'JetBrains Mono', monospace; color: #4a9eff; letter-spacing: 0.15em; text-transform: uppercase; margin-bottom: 0.75rem;">Your Feedback</div>
  <h2 style="font-family: 'Playfair Display', serif; font-size: 1.8rem; font-weight: 700; margin-bottom: 1.5rem;">Help Atelier Learn Your Taste</h2>
  <form method="POST" action="/feedback" style="display: grid; gap: 1.5rem;">
    <input type="hidden" name="session_id" value="{session_id}">
    <div>
      <label style="display: block; font-size: 0.75rem; font-family: 'JetBrains Mono', monospace; color: #888; margin-bottom: 0.5rem; text-transform: uppercase; letter-spacing: 0.1em;">Overall Rating</label>
      <div style="display: flex; gap: 0.5rem;">
        <button type="submit" name="rating" value="love" style="padding: 0.5rem 1.2rem; background: rgba(74,255,74,0.15); border: 1px solid rgba(74,255,74,0.3); border-radius: 8px; color: #4aff4a; cursor: pointer; font-size: 0.85rem;">Love it</button>
        <button type="submit" name="rating" value="like" style="padding: 0.5rem 1.2rem; background: rgba(74,158,255,0.15); border: 1px solid rgba(74,158,255,0.3); border-radius: 8px; color: #4a9eff; cursor: pointer; font-size: 0.85rem;">Like it</button>
        <button type="submit" name="rating" value="meh" style="padding: 0.5rem 1.2rem; background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); border-radius: 8px; color: #888; cursor: pointer; font-size: 0.85rem;">Meh</button>
        <button type="submit" name="rating" value="dislike" style="padding: 0.5rem 1.2rem; background: rgba(255,74,74,0.15); border: 1px solid rgba(255,74,74,0.3); border-radius: 8px; color: #ff4a4a; cursor: pointer; font-size: 0.85rem;">Not for me</button>
      </div>
    </div>
  </form>
</section>

<div style="text-align: center; padding: 2rem; font-size: 0.8rem; color: #555;">
  <a href="/" style="color: #4a9eff; text-decoration: none;">Generate another identity</a>
</div>
'''
    html = html.replace("</body>", feedback_html + "\n</body>")
    return html


@app.route("/session/<session_id>/<path:filename>")
def session_static(session_id, filename):
    """Serve static assets from a session directory (visual.html, JSON, MP3, PNG)."""
    session_dir = os.path.join(OUTPUT_DIR, session_id)
    if not os.path.isdir(session_dir):
        return "Session not found", 404
    return send_from_directory(session_dir, filename)


@app.route("/feedback", methods=["POST"])
def feedback():
    session_id = request.form.get("session_id", "")
    rating = request.form.get("rating", "")

    if not session_id:
        return "Missing session_id", 400

    # Load session data to find user_id
    session_dir = os.path.join(OUTPUT_DIR, session_id)
    analysis_path = os.path.join(session_dir, "analysis.json")

    if not os.path.exists(analysis_path):
        return "Session not found", 404

    with open(analysis_path) as f:
        analysis = json.load(f)

    # Find user from memory (scan sessions)
    user_id = "default"
    memory_dir = os.path.join(os.path.dirname(__file__), "..", "memory")
    for fname in os.listdir(memory_dir):
        if fname.endswith(".json"):
            uid = fname.replace(".json", "")
            mem = load_memory(uid)
            for s in mem.get("sessions", []):
                if s.get("session_id") == session_id:
                    user_id = uid
                    break

    # Map rating to feedback
    feedback_data = {}
    if rating == "love":
        personality = analysis.get("brand_personality", "")
        if personality:
            feedback_data["liked_styles"] = [personality]
        feedback_data["complexity_adjustment"] = 0
        feedback_data["energy_adjustment"] = 0
    elif rating == "like":
        personality = analysis.get("brand_personality", "")
        if personality:
            feedback_data["liked_styles"] = [personality]
    elif rating == "dislike":
        personality = analysis.get("brand_personality", "")
        if personality:
            feedback_data["disliked_styles"] = [personality]
        feedback_data["complexity_adjustment"] = -0.1 if analysis.get("complexity", 0.5) > 0.5 else 0.1
        feedback_data["energy_adjustment"] = -0.1 if analysis.get("energy", 0.5) > 0.5 else 0.1

    if feedback_data:
        update_preferences(user_id, feedback_data)

    # Redirect back to session with thank you
    return f'''<!DOCTYPE html>
<html><head><meta charset="UTF-8">
<title>Feedback Received</title>
<meta http-equiv="refresh" content="2;url=/session/{session_id}">
<style>
  body {{ font-family: 'Space Grotesk', sans-serif; background: #0a0a0f; color: #e8e8ec;
         display: flex; align-items: center; justify-content: center; min-height: 100vh; text-align: center; }}
  .msg {{ font-size: 1.2rem; }}
  .sub {{ font-size: 0.85rem; color: #666; margin-top: 0.5rem; }}
</style>
</head>
<body>
<div>
  <div class="msg">Feedback saved. Atelier is learning.</div>
  <div class="sub">Redirecting back...</div>
</div>
</body></html>'''


@app.route("/api/generate", methods=["POST"])
def api_generate():
    """JSON API endpoint for programmatic access."""
    data = request.get_json(silent=True) or {}
    brief = data.get("brief", "").strip()
    user_id = data.get("user_id", "default").strip()

    if not brief:
        return jsonify({"error": "brief is required"}), 400

    try:
        result = run_atelier(brief, user_id)
        if result is None:
            return jsonify({"error": "generation failed"}), 500
        return jsonify({
            "session_id": result["session_id"],
            "url": f"/session/{result['session_id']}",
            "personality": result["analysis"].get("brand_personality"),
            "mode": result["visual"]["mode"],
            "taglines": result["narrative"].get("taglines", []),
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("ATELIER_PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
