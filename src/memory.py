"""
Memory system for Atelier — persistent aesthetic preference learning.
"""

import json
import os
from datetime import datetime


MEMORY_DIR = os.path.join(os.path.dirname(__file__), "..", "memory")


def _memory_path(user_id):
    # Sanitize: only allow alphanumeric, hyphens, underscores
    safe_id = "".join(c for c in user_id if c.isalnum() or c in "-_") or "default"
    return os.path.join(MEMORY_DIR, f"{safe_id}.json")


def load_memory(user_id):
    """Load full memory for a user. Returns empty structure if none exists."""
    path = _memory_path(user_id)
    if os.path.exists(path):
        try:
            with open(path) as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            print(f"[Memory] Corrupt memory file for {user_id}, resetting.")
    return {
        "user_id": user_id,
        "sessions": [],
        "preferences": {
            "preferred_hues": [],
            "preferred_secondary_hues": [],
            "preferred_accent_hues": [],
            "avoided_hues": [],
            "style_weights": {
                "minimal": 0.5,
                "organic": 0.5,
                "bold": 0.5,
                "playful": 0.5,
                "luxurious": 0.5,
                "technical": 0.5,
                "warm": 0.5,
                "edgy": 0.5,
                "glitch": 0.5,
                "ink": 0.5,
            },
            "complexity": 0.5,
            "energy": 0.5,
            "mood_weights": {"warm": 0.5, "cool": 0.5, "neutral": 0.5},
            "motion_prefs": {"slow-drift": 0.5, "breathing": 0.5, "dynamic": 0.5, "static": 0.5},
        },
    }


def save_session(user_id, session_data):
    """Save a session and update preferences based on it."""
    os.makedirs(MEMORY_DIR, exist_ok=True)

    memory = load_memory(user_id)

    # Add session
    memory["sessions"].append(session_data)
    # Prune to last 50 sessions to prevent unbounded file growth
    if len(memory["sessions"]) > 50:
        memory["sessions"] = memory["sessions"][-50:]

    # Update preferences from this session's analysis
    analysis = session_data.get("analysis", {})
    prefs = memory["preferences"]

    # Track hues (primary, secondary, accent)
    palette = analysis.get("palette", {})
    for hue_key in ["primary_hue", "secondary_hue", "accent_hue"]:
        hue_val = palette.get(hue_key)
        if hue_val is not None:
            pref_key = f"preferred_{hue_key}s"
            if pref_key not in prefs:
                prefs[pref_key] = []
            if int(hue_val) not in prefs[pref_key]:
                prefs[pref_key].append(int(hue_val))
            prefs[pref_key] = prefs[pref_key][-10:]

    # Update style weights (moving average) — add missing styles dynamically
    personality = analysis.get("brand_personality", "")
    if personality:
        if personality not in prefs["style_weights"]:
            prefs["style_weights"][personality] = 0.5
        # Boost the chosen style, slightly decay others
        for style in prefs["style_weights"]:
            if style == personality:
                prefs["style_weights"][style] = min(1.0, prefs["style_weights"][style] + 0.15)
            else:
                prefs["style_weights"][style] = max(0.0, prefs["style_weights"][style] - 0.02)

    # Update complexity/energy (exponential moving average, alpha=0.3)
    # EMA gives ~70% weight to recent sessions, avoids calcification
    complexity = analysis.get("complexity")
    energy = analysis.get("energy")
    alpha = 0.3
    if complexity is not None:
        prefs["complexity"] = round(prefs["complexity"] * (1 - alpha) + complexity * alpha, 4)
    if energy is not None:
        prefs["energy"] = round(prefs["energy"] * (1 - alpha) + energy * alpha, 4)

    # Update motion prefs
    motion = analysis.get("motion_style", "")
    if motion in prefs["motion_prefs"]:
        for m in prefs["motion_prefs"]:
            if m == motion:
                prefs["motion_prefs"][m] = min(1.0, prefs["motion_prefs"][m] + 0.15)
            else:
                prefs["motion_prefs"][m] = max(0.0, prefs["motion_prefs"][m] - 0.02)

    # Update mood weights from palette mood (warm/cool/neutral)
    mood = palette.get("mood", "")
    if mood and "mood_weights" in prefs:
        if mood not in prefs["mood_weights"]:
            prefs["mood_weights"][mood] = 0.5
        for m in prefs["mood_weights"]:
            if m == mood:
                prefs["mood_weights"][m] = min(1.0, prefs["mood_weights"][m] + 0.15)
            else:
                prefs["mood_weights"][m] = max(0.0, prefs["mood_weights"][m] - 0.02)

    # Save
    with open(_memory_path(user_id), "w") as f:
        json.dump(memory, f, indent=2)


def update_preferences(user_id, feedback):
    """Apply explicit user feedback to preferences.
    
    Args:
        user_id: User identifier
        feedback: dict with optional keys:
            - liked_styles: list of style names they liked
            - disliked_styles: list of style names they disliked
            - preferred_hues: list of hue numbers they prefer
            - avoided_hues: list of hue numbers they dislike
            - complexity_adjustment: float -0.5 to +0.5 adjustment
            - energy_adjustment: float -0.5 to +0.5 adjustment
    """
    memory = load_memory(user_id)
    prefs = memory["preferences"]

    liked = feedback.get("liked_styles", [])
    disliked = feedback.get("disliked_styles", [])
    preferred_hues = feedback.get("preferred_hues", [])
    avoided_hues = feedback.get("avoided_hues", [])
    complexity_adj = feedback.get("complexity_adjustment", 0)
    energy_adj = feedback.get("energy_adjustment", 0)

    # Adjust style weights strongly — add missing styles dynamically
    for style in liked:
        if style not in prefs["style_weights"]:
            prefs["style_weights"][style] = 0.5
        prefs["style_weights"][style] = min(1.0, prefs["style_weights"][style] + 0.2)
    for style in disliked:
        if style not in prefs["style_weights"]:
            prefs["style_weights"][style] = 0.5
        prefs["style_weights"][style] = max(0.0, prefs["style_weights"][style] - 0.2)

    # Add preferred hues
    for hue in preferred_hues:
        if hue not in prefs["preferred_hues"]:
            prefs["preferred_hues"].append(int(hue))
    prefs["preferred_hues"] = prefs["preferred_hues"][-10:]

    # Add avoided hues
    for hue in avoided_hues:
        if hue not in prefs["avoided_hues"]:
            prefs["avoided_hues"].append(int(hue))
    prefs["avoided_hues"] = prefs["avoided_hues"][-10:]

    # Complexity/energy adjustments (direct feedback overrides)
    prefs["complexity"] = max(0, min(1, prefs["complexity"] + complexity_adj))
    prefs["energy"] = max(0, min(1, prefs["energy"] + energy_adj))

    # Track feedback
    if "feedback_history" not in memory:
        memory["feedback_history"] = []
    memory["feedback_history"].append({"date": datetime.now().isoformat(), "feedback": feedback})

    with open(_memory_path(user_id), "w") as f:
        json.dump(memory, f, indent=2)


def get_preferences(user_id):
    """Get current preference summary for use in analysis prompts."""
    memory = load_memory(user_id)
    prefs = memory["preferences"]

    if not memory["sessions"]:
        return None  # No history yet

    # Find dominant style
    dominant_style = max(prefs["style_weights"], key=prefs["style_weights"].get)

    # Find dominant motion
    dominant_motion = max(prefs["motion_prefs"], key=prefs["motion_prefs"].get)

    # Find dominant mood
    mood_weights = prefs.get("mood_weights", {"warm": 0.5, "cool": 0.5, "neutral": 0.5})
    dominant_mood = max(mood_weights, key=mood_weights.get)

    return {
        "dominant_style": dominant_style,
        "style_weights": prefs["style_weights"],
        "preferred_hues": prefs["preferred_hues"][-5:],
        "preferred_secondary_hues": prefs.get("preferred_secondary_hues", [])[-5:],
        "preferred_accent_hues": prefs.get("preferred_accent_hues", [])[-5:],
        "avg_complexity": round(prefs["complexity"], 2),
        "avg_energy": round(prefs["energy"], 2),
        "preferred_motion": dominant_motion,
        "preferred_mood": dominant_mood,
        "mood_weights": mood_weights,
        "sessions_count": len(memory["sessions"]),
    }
