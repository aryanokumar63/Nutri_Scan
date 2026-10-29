"""Shared pytest fixtures for isolated Playwright tests."""

from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

import allure
import pytest
from playwright.sync_api import Page

from config.settings import BASE_URL
from pages.home_page import HomePage
from pages.login_page import LoginPage
from pages.otp_page import OtpPage
from pages.signup_page import SignupPage


def pytest_configure(config: pytest.Config) -> None:
    """Create a unique screenshot folder for this pytest session."""

    # Use a timestamp and random suffix so screenshots from separate runs never collide.
    run_id = f"{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}_{uuid4().hex[:8]}"

    # Store failed-test screenshots outside Allure's result files while attaching each to Allure.
    screenshot_dir = Path(config.rootpath) / "test-artifacts" / "screenshots" / run_id
    screenshot_dir.mkdir(parents=True, exist_ok=True)
    config._signup_screenshot_dir = screenshot_dir


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo[object]):
    """Attach a unique full-page screenshot to Allure whenever a test fails."""

    # Let pytest create the normal test report before deciding whether a screenshot is needed.
    outcome = yield
    report = outcome.get_result()

    # Capture only call-phase failures, avoiding duplicate setup/teardown screenshots.
    if report.when != "call" or not report.failed:
        return

    # Retrieve the isolated Playwright page supplied by pytest-playwright.
    page = item.funcargs.get("page")
    if page is None:
        return

    # Sanitize the test id so the screenshot filename is readable and filesystem-safe.
    safe_test_name = "".join(character if character.isalnum() else "_" for character in item.nodeid)
    screenshot_path = item.config._signup_screenshot_dir / f"{safe_test_name}.png"

    try:
        # Save a unique full-page screenshot for direct sharing outside the Allure report.
        page.screenshot(path=str(screenshot_path), full_page=True)

        # Attach the same screenshot to the failed test's Allure result.
        allure.attach.file(
            str(screenshot_path),
            name=f"{item.name} - failure screenshot",
            attachment_type=allure.attachment_type.PNG,
        )
    except Exception as error:
        # Preserve the original test failure while recording why screenshot capture was unavailable.
        allure.attach(str(error), name="Screenshot capture error", attachment_type=allure.attachment_type.TEXT)


@pytest.fixture
def login_page(page: Page) -> LoginPage:
    """Provide a fresh login page object backed by pytest-playwright's isolated page."""

    # pytest-playwright creates a new browser context and page for each test invocation.
    return LoginPage(page)


@pytest.fixture
def signup_page(page: Page) -> SignupPage:
    """Provide a fresh signup page object backed by an isolated browser page."""

    # Returning a new page object per test prevents locator and browser state collisions.
    return SignupPage(page)


@pytest.fixture
def otp_page(page: Page) -> OtpPage:
    """Provide an OTP page object for the current test's isolated browser page."""

    # Keep OTP interactions on the same isolated page that performed signup.
    return OtpPage(page)


@pytest.fixture
def home_page(page: Page) -> HomePage:
    """Provide a home page object for browser-back validation."""

    # Keep browser history assertions on the same isolated page as the OTP flow.
    return HomePage(page)


@pytest.fixture
def app_base_url() -> str:
    """Provide the configured application host to tests and page objects."""

    # Use a project-specific fixture name to avoid pytest-base-url's reserved base_url fixture.
    return BASE_URL

