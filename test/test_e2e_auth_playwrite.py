import os
import time
import uuid
import subprocess

import httpx
import pytest
from playwright.sync_api import sync_playwright

BASE_URL = os.getenv("E2E_BASE_URL", "http://127.0.0.1:8000")

@pytest.fixture(scope="session", autouse=True)
def run_server():
    proc = subprocess.Popen(
        ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    for _ in range(30):
        try:
            r = httpx.get(f"{BASE_URL}/docs", timeout=1.0)
            if r.status_code == 200:
                break
        except Exception:
            time.sleep(1)
    else:
        proc.terminate()
        raise RuntimeError("Server did not start in time")

    yield

    proc.terminate()
    try:
        proc.wait(timeout=10)
    except subprocess.TimeoutExpired:
        proc.kill()

def test_register_success():
    unique_suffix = uuid.uuid4().hex[:8]
    email = f"e2e_{unique_suffix}@example.com"
    username = f"e2euser_{unique_suffix}"
    password = "password123"

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(f"{BASE_URL}/register")

        page.fill('input[name="email"]', email)
        page.fill('input[name="username"]', username)
        page.fill('input[name="password"]', password)
        page.fill('input[name="confirmPassword"]', password)
        page.click('button[type="submit"]')

        page.wait_for_timeout(1000)
        message = page.text_content("#message")
        assert "Registration successful" in message

        token = page.evaluate("() => window.localStorage.getItem('authToken')")
        assert token is not None

        browser.close()

def test_register_short_password_shows_error():
    email = "badpass@example.com"
    username = "baduser"
    short_password = "123"

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(f"{BASE_URL}/register")

        page.fill('input[name="email"]', email)
        page.fill('input[name="username"]', username)
        page.fill('input[name="password"]', short_password)
        page.fill('input[name="confirmPassword"]', short_password)
        page.click('button[type="submit"]')

        page.wait_for_timeout(500)
        error_text = page.text_content("#error")
        assert "Password must be at least" in error_text

        browser.close()

def test_login_success():
    unique_suffix = uuid.uuid4().hex[:8]
    email = f"login_{unique_suffix}@example.com"
    username = f"loginuser_{unique_suffix}"
    password = "password123"

    # Register user via API
    resp = httpx.post(
        f"{BASE_URL}/register",
        json={"username": username, "email": email, "password": password},
        timeout=3.0,
    )
    assert resp.status_code in (200, 201)

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(f"{BASE_URL}/login")

        page.fill('input[name="identifier"]', username)
        page.fill('input[name="password"]', password)
        page.click('button[type="submit"]')

        page.wait_for_timeout(1000)
        message = page.text_content("#message")
        assert "Login successful" in message

        token = page.evaluate("() => window.localStorage.getItem('authToken')")
        assert token is not None

        browser.close()

def test_login_wrong_password_shows_error():
    unique_suffix = uuid.uuid4().hex[:8]
    email = f"wrongpw_{unique_suffix}@example.com"
    username = f"wrongpwuser_{unique_suffix}"
    password = "password123"

    # Register correct user via API
    resp = httpx.post(
        f"{BASE_URL}/register",
        json={"username": username, "email": email, "password": password},
        timeout=3.0,
    )
    assert resp.status_code in (200, 201)

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(f"{BASE_URL}/login")

        page.fill('input[name="identifier"]', username)
        page.fill('input[name="password"]', "not_the_right_password")
        page.click('button[type="submit"]')

        page.wait_for_timeout(1000)
        error_text = page.text_content("#error")
        assert "Invalid credentials" in error_text

        browser.close()
