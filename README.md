# NutriScan Signup POM Tests

This project uses pytest and Playwright with a Page Object Model structure.

## Structure

- `config/settings.py` keeps the application URL in one place.
- `pages/login_page.py` stores the inspected login-to-signup locator.
- `pages/signup_page.py` stores the inspected signup form locators.
- `pages/otp_page.py` stores the inspected OTP input and verification locators.
- `pages/home_page.py` validates the authenticated home page after OTP verification.
- `config/test_data.py` generates unique `@yopmail.com` emails and stores the positive-case password/OTP.
- `tests/conftest.py` provides isolated fixtures for every test.
- `tests/test_signup.py` contains the signup navigation and control checks.

## Signup test coverage

- Positive/integration: complete login-to-signup-to-OTP-to-home flow.
- Negative: empty mandatory fields, invalid email, short password, and mismatched passwords.
- Edge: exact eight-character password boundary.
- Affirmation: route, control visibility, OTP screen, and authenticated home assertions.
- OTP coverage: unverified-email reuse, wrong OTP, blank OTP, resend feedback, resend field clearing,
  numeric-only input, and browser-back behavior from the authenticated home page.

## Allure report

Pytest writes a clean result set to `allure-results` on every run. Failed tests receive a unique full-page
PNG screenshot in `test-artifacts/screenshots` and the same image is attached to their Allure result.

```powershell
allure.cmd generate allure-results -o allure-report
```

## Setup

```powershell
pip install -r requirements.txt
playwright install chromium
```

## Run

```powershell
pytest
```

The positive signup flow uses a fresh email on every run, fills `Aryan@123`, confirms the same password,
submits the form, enters OTP `123456`, and verifies that the authenticated home page opens. Any failed
navigation or assertion makes pytest report the test as `FAILED` with a readable error message.

To run against another environment:

```powershell
$env:NUTRISCAN_BASE_URL = "https://example.test"
pytest
```

