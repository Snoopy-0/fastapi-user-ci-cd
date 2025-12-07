import os
import time
import uuid
import subprocess

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
    time.sleep(2.0)
    yield
    proc.terminate()
    proc.wait(timeout=5)

def register_and_login(page, username: str, email: str, password: str):
    # Register
    page.goto(f"{BASE_URL}/register")
    page.fill('input[name="username"]', username)
    page.fill('input[name="email"]', email)
    page.fill('input[name="password"]', password)
    page.click('button[type="submit"]')
    page.wait_for_timeout(1000)

    # Login
    page.goto(f"{BASE_URL}/login")
    page.fill('input[name="identifier"]', username)
    page.fill('input[name="password"]', password)
    page.click('button[type="submit"]')
    page.wait_for_timeout(1000)

def test_calculation_bread_positive():
    uniq = str(uuid.uuid4())[:8]
    username = f"user_{uniq}"
    email = f"{username}@example.com"
    password = "mysecret123"

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        register_and_login(page, username, email, password)

        # Go to calculations page
        page.goto(f"{BASE_URL}/calculations.html")

        # CREATE (Add)
        page.fill("#a", "2")
        page.fill("#b", "3")
        page.select_option("#type", "add")
        page.click('button[type="submit"]')
        page.wait_for_timeout(1000)

        # Check that result row appears
        rows = page.query_selector_all("#calc-table-body tr")
        assert len(rows) >= 1
        first_row_text = rows[0].text_content()
        assert "2" in first_row_text
        assert "3" in first_row_text
        assert "add" in first_row_text
        assert "5" in first_row_text

        # EDIT (update to multiply)
        rows[0].query_selector(".edit-btn").click()
        page.wait_for_timeout(500)
        page.fill("#b", "4")
        page.select_option("#type", "multiply")
        page.click('button[type="submit"]')
        page.wait_for_timeout(1000)

        rows = page.query_selector_all("#calc-table-body tr")
        first_row_text = rows[0].text_content()
        assert "multiply" in first_row_text
        assert "8" in first_row_text  # 2 * 4

        # DELETE
        rows[0].query_selector(".delete-btn").click()
        page.wait_for_timeout(1000)
        rows_after = page.query_selector_all("#calc-table-body tr")
        # could be 0 or fewer; just assert no row with "2 4 multiply 8"
        for r in rows_after:
            assert "multiply" not in r.text_content()

        browser.close()

def test_calculation_negative_divide_by_zero():
    uniq = str(uuid.uuid4())[:8]
    username = f"user_{uniq}"
    email = f"{username}@example.com"
    password = "mysecret123"

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        register_and_login(page, username, email, password)
        page.goto(f"{BASE_URL}/calculations.html")

        page.fill("#a", "10")
        page.fill("#b", "0")
        page.select_option("#type", "divide")
        page.click('button[type="submit"]')
        page.wait_for_timeout(1000)

        error_text = page.text_content("#error")
        assert "Division by zero" in error_text

        browser.close()

def test_calculation_unauthorized_access():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        # Directly visit calculations without logging in
        page.goto(f"{BASE_URL}/calculations.html")
        page.wait_for_timeout(1000)

        page.fill("#a", "1")
        page.fill("#b", "2")
        page.select_option("#type", "add")
        page.click('button[type="submit"]')
        page.wait_for_timeout(1000)

        error_text = page.text_content("#error")
        # Your frontend sets "You are not logged in." on 401s
        assert "not logged in" in error_text.lower()

        browser.close()
