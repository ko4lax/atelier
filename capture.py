from playwright.sync_api import sync_playwright
import time, os

D = "/root/atelier/demo/frames"
os.makedirs(D, exist_ok=True)

with sync_playwright() as pw:
    browser = pw.chromium.launch(headless=True)
    ctx = browser.new_context(viewport={"width": 1920, "height": 1080})
    page = ctx.new_page()

    # 1. Home page
    page.goto("https://atelier.ko4lax.dev", wait_until="networkidle")
    page.wait_for_timeout(2000)
    page.screenshot(path=f"{D}/01_home.png")
    print("Captured: home")

    # 2. Fill brief
    page.fill('textarea[name="brief"]', "Minimal luxury watch brand for urban professionals. Clean, sophisticated, timeless aesthetic with premium feel.")
    page.wait_for_timeout(800)
    page.screenshot(path=f"{D}/02_filled.png")
    print("Captured: filled")

    # 3. Submit (don't wait for nav)
    page.click("button[type='submit']", no_wait_after=True)
    page.wait_for_timeout(3000)
    page.screenshot(path=f"{D}/03_loading.png")
    print("Captured: loading")

    # 4. Wait for result page
    page.wait_for_url("**/session/**", timeout=90000)
    page.wait_for_timeout(4000)
    page.screenshot(path=f"{D}/04_result_top.png")
    print("Captured: result top")

    # 5-8. Scroll captures
    sections = [
        (800, "05_palette"),
        (1600, "06_taglines"),
        (2400, "07_story"),
    ]
    for scroll_y, name in sections:
        page.evaluate("window.scrollTo({top: %d, behavior: 'smooth'})" % scroll_y)
        page.wait_for_timeout(1200)
        page.screenshot(path=f"{D}/{name}.png")
        print(f"Captured: {name}")

    # 8. Bottom with feedback
    page.evaluate("window.scrollTo({top: document.body.scrollHeight, behavior: 'smooth'})")
    page.wait_for_timeout(1200)
    page.screenshot(path=f"{D}/08_feedback.png")
    print("Captured: feedback")

    # 9. Click positive feedback for memory demo
    try:
        page.click('button[value="love"]', timeout=5000, no_wait_after=True)
        page.wait_for_timeout(3000)
        page.screenshot(path=f"{D}/09_feedback_clicked.png")
        print("Captured: feedback clicked")
    except Exception as e:
        print(f"Feedback click skipped: {e}")
        page.screenshot(path=f"{D}/09_feedback_clicked.png")

    # 10. Go back home for memory demo
    page.goto("https://atelier.ko4lax.dev", wait_until="networkidle")
    page.wait_for_timeout(2000)
    page.screenshot(path=f"{D}/10_home_again.png")
    print("Captured: home again")

    browser.close()
    print("ALL DONE")
