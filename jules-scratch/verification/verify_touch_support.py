import os
from pathlib import Path
from playwright.sync_api import sync_playwright, expect, Locator

def swipe(locator: Locator, direction: str):
    """
    Simulates a swipe gesture on a given Playwright Locator by dispatching
    touchstart, touchmove, and touchend events with the required properties,
    including screenX/Y for compatibility with the application's event handlers.
    """
    box = locator.bounding_box()
    if box is None:
        raise Exception("Cannot get bounding box for element to swipe.")

    start_x = box['x'] + box['width'] / 2
    start_y = box['y'] + box['height'] / 2

    if direction == 'left':
        end_x = start_x - 100
        end_y = start_y
    elif direction == 'right':
        end_x = start_x + 100
        end_y = start_y
    else:
        raise ValueError("Swipe direction must be 'left' or 'right'")

    # Dispatch touchstart
    start_touch = [{'identifier': 0, 'clientX': start_x, 'clientY': start_y, 'screenX': start_x, 'screenY': start_y}]
    locator.dispatch_event('touchstart', {
        'touches': start_touch,
        'changedTouches': start_touch,
        'targetTouches': start_touch
    })

    # Dispatch touchend - the app logic only needs start and end points
    end_touch = [{'identifier': 0, 'clientX': end_x, 'clientY': end_y, 'screenX': end_x, 'screenY': end_y}]
    locator.dispatch_event('touchend', {
        'touches': [],
        'changedTouches': end_touch,
        'targetTouches': []
    })


def run_verification():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(**p.devices['iPhone 11 Pro'])
        page = context.new_page()

        file_path = f"file://{Path('index.html').resolve()}"
        page.goto(file_path)

        gallery_section = page.locator("#creacion-ia")
        gallery_section.scroll_into_view_if_needed()

        first_image = gallery_section.locator("img").first
        first_image.click()

        lightbox = page.locator("#lightbox")
        expect(lightbox).to_be_visible()

        page.screenshot(path="jules-scratch/verification/verification.png")

        initial_image_src = page.locator("#lb-image").get_attribute("src")

        swipe(lightbox, "left")

        # Add a small delay to allow for the image to change
        page.wait_for_timeout(500)

        expect(page.locator("#lb-image")).not_to_have_attribute("src", initial_image_src if initial_image_src else "")

        page.screenshot(path="jules-scratch/verification/verification_swiped.png")

        browser.close()

if __name__ == "__main__":
    run_verification()