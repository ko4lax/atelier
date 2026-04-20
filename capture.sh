#!/bin/bash
set -e
D="/root/atelier/demo/frames"
mkdir -p "$D"
PY=~/.hermes/hermes-agent/venv/bin/python3
PLAY="$PY -c \"
from playwright.sync_api import sync_playwright
import time
with sync_playwright() as p:
    b = p.chromium.launch(headless=True)
    c = b.new_context(viewport={'width':1920,'height':1080})
    p = c.new_page()
    p.goto('https://atelier.ko4lax.dev', wait_until='networkidle')
    p.wait_for_timeout(1500)
    p.screenshot(path='$D/01_home.png')
    
    # Fill in the brief
    p.fill('#brief', 'Minimal luxury watch brand for urban professionals. Clean, sophisticated, timeless aesthetic with premium feel.')
    p.wait_for_timeout(500)
    p.screenshot(path='$D/02_filled.png')
    
    # Submit and capture loading
    p.click('button[type=\"submit\"]', no_wait_after=True)
    p.wait_for_timeout(2000)
    p.screenshot(path='$D/03_loading.png')
    
    # Wait for generation to complete (max 90s)
    p.wait_for_url('**/session/**', timeout=90000)
    p.wait_for_timeout(3000)
    p.screenshot(path='$D/04_result_top.png')
    
    # Scroll to palette
    p.evaluate('window.scrollTo(0, 800)')
    p.wait_for_timeout(1000)
    p.screenshot(path='$D/05_palette.png')
    
    # Scroll to taglines
    p.evaluate('window.scrollTo(0, 1600)')
    p.wait_for_timeout(1000)
    p.screenshot(path='$D/06_taglines.png')
    
    # Scroll to brand story
    p.evaluate('window.scrollTo(0, 2400)')
    p.wait_for_timeout(1000)
    p.screenshot(path='$D/07_story.png')
    
    # Scroll to social voice + feedback
    p.evaluate('window.scrollTo(0, document.body.scrollHeight)')
    p.wait_for_timeout(1000)
    p.screenshot(path='$D/08_feedback.png')
    
    b.close()
    print('DONE')
\""
eval $PLAY
