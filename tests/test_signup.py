"""Tests for signup navigation and signup form controls."""

import allure
from playwright.sync_api import expect

from config.test_data import (
    EXPECTED_INVALID_EMAIL_MESSAGE,
    EXPECTED_INVALID_OTP_MESSAGE,
    EXPECTED_EMPTY_OTP_MESSAGE,
    EXPECTED_DUPLICATE_EMAIL_MESSAGE,
    EXPECTED_PASSWORD_MISMATCH_MESSAGE,
    EXPECTED_REQUIRED_FIELDS_MESSAGE,
    EXPECTED_RESEND_MESSAGE,
    EXPECTED_SHORT_PASSWORD_MESSAGE,
    EXPECTED_WEAK_PASSWORD_MESSAGE,
    SIGNUP_OTP,
    SIGNUP_PASSWORD,
    create_unique_signup_email,
)
from pages.login_page import LoginPage
from pages.home_page import HomePage
from pages.otp_page import OtpPage
from pages.signup_page import SignupPage


def _open_signup_page(login_page: LoginPage, app_base_url: str) -> None:
    """Open signup from login so every test starts with a clean, real user journey."""

    # Navigate to login before signup so this helper does not depend on an existing session.
    login_page.open(app_base_url)

    # Use the verified accessible Sign up link instead of a fragile CSS selector.
    login_page.click_signup()

    # Confirm the integration navigation reached the expected signup route.
    expect(login_page.page).to_have_url(f"{app_base_url}/signup")


def _create_signup_to_otp(
    login_page: LoginPage,
    signup_page: SignupPage,
    app_base_url: str,
) -> str:
    """Create a fresh unverified user and return the email shown on the OTP screen."""

    # Use the real login-to-signup integration path before creating a unique test user.
    _open_signup_page(login_page, app_base_url)

    # Generate an email that cannot collide with another test or previous run.
    email = create_unique_signup_email()

    # Submit valid signup data so the next assertion can focus only on OTP behavior.
    signup_page.fill_signup_form(email, SIGNUP_PASSWORD)
    signup_page.submit()
    expect(signup_page.page).to_have_url(f"{app_base_url}/verify-otp")

    # Return the generated email for duplicate-email and diagnostic messages.
    return email


@allure.epic("NutriScan AI")
@allure.feature("Signup")
@allure.story("Positive signup integration flow")
@allure.title("Positive: complete signup with OTP verification")
@allure.tag("positive", "integration", "affirmation")
def test_user_can_complete_positive_signup(
    login_page: LoginPage,
    signup_page: SignupPage,
    otp_page: OtpPage,
    app_base_url: str,
) -> None:
    """Complete the entire signup journey in one isolated browser page."""

    # Print a visible test start marker so the terminal shows which flow is running.
    print("\n[START] Positive signup test started")

    # Open login first so this single test covers the complete user journey from entry point.
    print("[STEP] Open login page")
    login_page.open(app_base_url)
    print("[PASS] Login page opened")

    # Navigate to signup using the verified login page link in the same browser page.
    print("[STEP] Click on Sign up button/link")
    login_page.click_signup()

    # Confirm the signup route opened before interacting with its form.
    expect(login_page.page).to_have_url(f"{app_base_url}/signup")
    print("[PASS] Signup page opened")

    # Confirm all mandatory signup controls are visible before entering test data.
    expect(signup_page.email_input).to_be_visible()
    expect(signup_page.password_input).to_be_visible()
    expect(signup_page.confirm_password_input).to_be_visible()
    expect(signup_page.create_account_button).to_be_visible()
    print("[PASS] Signup mandatory fields are visible")

    # Generate a fresh yopmail identity so repeated or parallel tests do not collide.
    unique_email = create_unique_signup_email()
    print(f"[STEP] Enter unique email: {unique_email}")

    # Fill every mandatory field with valid positive-case values.
    signup_page.fill_signup_form(unique_email, SIGNUP_PASSWORD)
    print("[PASS] Email, password, and confirm password entered successfully")

    # Submit the completed signup form and wait for the verification route.
    print("[STEP] Click on Create account button")
    signup_page.submit()
    expect(signup_page.page).to_have_url(f"{app_base_url}/verify-otp")
    print("[PASS] Signup form submitted; OTP page opened")

    # Confirm the OTP control is visible before using the stored verification code.
    expect(otp_page.otp_input).to_be_visible()
    print("[STEP] Enter OTP: 123456")

    # Enter and submit the reusable OTP value configured for this environment.
    verified_home_page = otp_page.verify(SIGNUP_OTP, app_base_url)
    print("[STEP] Click on Verify & Continue button")

    # Validate the real post-OTP home page; pytest reports FAILED if either assertion fails.
    verified_home_page.assert_signup_completed(app_base_url)
    print("[PASS] OTP verified and signup completed successfully")
    print("[PASS] Positive signup test finished\n")


@allure.epic("NutriScan AI")
@allure.feature("Signup validation")
@allure.story("Required fields")
@allure.title("Negative: empty required fields show the correct message")
@allure.tag("negative", "validation", "affirmation")
def test_signup_required_fields_block_submission(
    login_page: LoginPage,
    signup_page: SignupPage,
    app_base_url: str,
) -> None:
    """Verify that an empty signup form cannot move to OTP verification."""

    # Start from login and open signup using the same integration path as a real user.
    print("\n[START] Required-fields negative test")
    _open_signup_page(login_page, app_base_url)

    # Submit without data to verify mandatory fields prevent signup progression.
    print("[STEP] Submit signup form without entering mandatory fields")
    signup_page.submit()

    # Staying on signup proves the empty form was rejected before OTP creation.
    expect(signup_page.page).to_have_url(f"{app_base_url}/signup")
    signup_page.assert_validation_message(EXPECTED_REQUIRED_FIELDS_MESSAGE)
    print("[PASS] Empty mandatory fields correctly blocked submission\n")


@allure.epic("NutriScan AI")
@allure.feature("Signup validation")
@allure.story("Email validation")
@allure.title("Negative: invalid email shows native email validation")
@allure.tag("negative", "validation", "affirmation")
def test_signup_invalid_email_blocks_submission(
    login_page: LoginPage,
    signup_page: SignupPage,
    app_base_url: str,
) -> None:
    """Verify that a malformed email cannot move to OTP verification."""

    # Open a fresh signup journey for this negative validation case.
    print("\n[START] Invalid-email negative test")
    _open_signup_page(login_page, app_base_url)

    # Use a malformed email while keeping both password values valid.
    print("[STEP] Enter invalid email and valid matching passwords")
    signup_page.fill_signup_form("not-an-email", SIGNUP_PASSWORD)

    # Submit the invalid form and expect client-side validation to keep the user on signup.
    signup_page.submit()
    expect(signup_page.page).to_have_url(f"{app_base_url}/signup")
    signup_page.assert_email_native_validation(EXPECTED_INVALID_EMAIL_MESSAGE)
    print("[PASS] Invalid email correctly blocked submission\n")


@allure.epic("NutriScan AI")
@allure.feature("Signup validation")
@allure.story("Password length validation")
@allure.title("Negative: short password shows the minimum-length message")
@allure.tag("negative", "validation", "edge", "affirmation")
def test_signup_short_password_blocks_submission(
    login_page: LoginPage,
    signup_page: SignupPage,
    app_base_url: str,
) -> None:
    """Verify that a password shorter than eight characters cannot submit."""

    # Open a fresh signup journey for this password boundary validation case.
    print("\n[START] Short-password negative test")
    _open_signup_page(login_page, app_base_url)

    # This password has seven characters and is intentionally below the required minimum.
    short_password = "Ab@1234"
    print("[STEP] Enter unique email and seven-character password")
    signup_page.fill_signup_form(create_unique_signup_email(), short_password)

    # The invalid short password must not advance to OTP verification.
    signup_page.submit()
    expect(signup_page.page).to_have_url(f"{app_base_url}/signup")
    signup_page.assert_validation_message(EXPECTED_SHORT_PASSWORD_MESSAGE)
    print("[PASS] Short password correctly blocked submission\n")


@allure.epic("NutriScan AI")
@allure.feature("Signup validation")
@allure.story("Password confirmation")
@allure.title("Negative: mismatched passwords show the correct message")
@allure.tag("negative", "validation", "affirmation")
def test_signup_mismatched_passwords_block_submission(
    login_page: LoginPage,
    signup_page: SignupPage,
    app_base_url: str,
) -> None:
    """Verify that different password and confirmation values cannot submit."""

    # Open a fresh signup journey for the confirmation validation case.
    print("\n[START] Password-mismatch negative test")
    _open_signup_page(login_page, app_base_url)

    # Enter valid-length passwords that intentionally do not match each other.
    print("[STEP] Enter valid email and mismatched passwords")
    signup_page.email_input.fill(create_unique_signup_email())
    signup_page.password_input.fill(SIGNUP_PASSWORD)
    signup_page.confirm_password_input.fill("Different@123")

    # The mismatch must keep the browser on signup instead of opening OTP.
    signup_page.submit()
    expect(signup_page.page).to_have_url(f"{app_base_url}/signup")
    signup_page.assert_validation_message(EXPECTED_PASSWORD_MISMATCH_MESSAGE)
    print("[PASS] Mismatched passwords correctly blocked submission\n")


@allure.epic("NutriScan AI")
@allure.feature("Signup validation")
@allure.story("Password boundary")
@allure.title("Edge: exactly eight-character password is accepted by the form")
@allure.tag("edge", "validation", "affirmation")
def test_signup_accepts_eight_character_password_boundary(
    login_page: LoginPage,
    signup_page: SignupPage,
    app_base_url: str,
) -> None:
    """Verify the exact eight-character password boundary is accepted by the form."""

    # Open a fresh signup journey for the lower-boundary positive check.
    print("\n[START] Eight-character password edge test")
    _open_signup_page(login_page, app_base_url)

    # Use exactly eight characters with uppercase, lowercase, a symbol, and digits.
    boundary_password = "Ab@12345"
    print("[STEP] Enter unique email and exactly eight-character password")
    signup_page.fill_signup_form(create_unique_signup_email(), boundary_password)

    # A valid boundary input should leave the submit control enabled for the user.
    expect(signup_page.create_account_button).to_be_enabled()
    print("[PASS] Eight-character password boundary accepted by signup form\n")


@allure.epic("NutriScan AI")
@allure.feature("Signup validation")
@allure.story("Whitespace handling")
@allure.title("Edge: leading and trailing email spaces are normalized")
@allure.tag("edge", "integration", "affirmation")
def test_signup_email_spaces_are_normalized(
    login_page: LoginPage,
    signup_page: SignupPage,
    app_base_url: str,
) -> None:
    """Verify the live app trims email whitespace before opening OTP verification."""

    # Start from a clean login-to-signup journey for the whitespace edge case.
    print("\n[START] Email-whitespace edge test")
    _open_signup_page(login_page, app_base_url)

    # Surround a unique valid email with spaces to verify the observed normalization behavior.
    normalized_email = create_unique_signup_email()
    signup_page.fill_signup_form(f"  {normalized_email}  ", SIGNUP_PASSWORD)
    signup_page.submit()

    # The live app trims the email and proceeds to OTP instead of showing a validation error.
    expect(signup_page.page).to_have_url(f"{app_base_url}/verify-otp")
    print("[PASS] Email spaces were normalized and OTP page opened\n")


@allure.epic("NutriScan AI")
@allure.feature("Signup validation")
@allure.story("Whitespace handling")
@allure.title("Negative: spaces in all fields show the required-fields message")
@allure.tag("negative", "validation", "edge", "affirmation")
def test_signup_spaces_in_all_fields_show_required_message(
    login_page: LoginPage,
    signup_page: SignupPage,
    app_base_url: str,
) -> None:
    """Verify that whitespace-only values are rejected with the exact message."""

    # Start from a clean login-to-signup journey for the whitespace validation case.
    print("\n[START] All-fields-whitespace negative test")
    _open_signup_page(login_page, app_base_url)

    # Enter whitespace in every field and submit the form.
    print("[STEP] Enter spaces in email, password, and confirm password")
    signup_page.email_input.fill(" ")
    signup_page.password_input.fill(" ")
    signup_page.confirm_password_input.fill(" ")
    signup_page.submit()

    # Assert both route protection and the exact validation message observed on the live page.
    expect(signup_page.page).to_have_url(f"{app_base_url}/signup")
    signup_page.assert_validation_message(EXPECTED_REQUIRED_FIELDS_MESSAGE)
    print("[PASS] Spaces in all fields correctly showed required-fields message\n")


@allure.epic("NutriScan AI")
@allure.feature("Signup validation")
@allure.story("Password strength")
@allure.title("Negative: weak simple password must show the password-strength message")
@allure.tag("negative", "security", "validation", "affirmation")
def test_signup_simple_password_shows_strength_message(
    login_page: LoginPage,
    signup_page: SignupPage,
    app_base_url: str,
) -> None:
    """Fail with evidence if a weak simple password is accepted without a message."""

    # Start from a clean login-to-signup journey for the password-strength contract.
    print("\n[START] Simple-password negative test")
    _open_signup_page(login_page, app_base_url)

    # Use an eight-character numeric password that meets length but is not strong.
    weak_password = "12345678"
    print("[STEP] Enter unique email and weak simple password")
    signup_page.fill_signup_form(create_unique_signup_email(), weak_password)
    signup_page.submit()

    # Require the agreed security message; if the app opens OTP, pytest fails and Allure captures it.
    signup_page.assert_validation_message(EXPECTED_WEAK_PASSWORD_MESSAGE)
    print("[PASS] Weak password validation message matched\n")


@allure.epic("NutriScan AI")
@allure.feature("Signup and OTP")
@allure.story("Unverified email reuse")
@allure.title("Negative: unverified email cannot be submitted again")
@allure.tag("negative", "integration", "security", "affirmation")
def test_unverified_user_cannot_reuse_same_email(
    login_page: LoginPage,
    signup_page: SignupPage,
    otp_page: OtpPage,
    app_base_url: str,
) -> None:
    """Verify that returning from OTP does not create a second signup for the same email."""

    # Create the first unverified signup and reach OTP.
    print("\n[START] Unverified-email reuse negative test")
    email = _create_signup_to_otp(login_page, signup_page, app_base_url)

    # Return to signup before OTP verification, matching the user's requested scenario.
    print("[STEP] Go back from OTP screen")
    otp_page.back_link.click()
    expect(signup_page.page).to_have_url(f"{app_base_url}/signup")

    # Submit the same email again without verifying the first OTP.
    print(f"[STEP] Submit the same unverified email again: {email}")
    signup_page.fill_signup_form(email, SIGNUP_PASSWORD)
    signup_page.submit()

    # Require duplicate-email protection and ensure OTP is not opened a second time.
    expect(signup_page.page).to_have_url(f"{app_base_url}/signup")
    signup_page.assert_validation_message(EXPECTED_DUPLICATE_EMAIL_MESSAGE)
    print("[PASS] Unverified email reuse was blocked\n")


@allure.epic("NutriScan AI")
@allure.feature("Signup and OTP")
@allure.story("Wrong OTP")
@allure.title("Negative: wrong OTP shows validation and blocks home access")
@allure.tag("negative", "security", "affirmation")
def test_wrong_otp_does_not_open_home(
    login_page: LoginPage,
    signup_page: SignupPage,
    otp_page: OtpPage,
    app_base_url: str,
) -> None:
    """Verify an incorrect OTP shows the expected message and cannot authenticate."""

    # Create a fresh signup so the OTP screen is reached without shared state.
    print("\n[START] Wrong-OTP negative test")
    _create_signup_to_otp(login_page, signup_page, app_base_url)

    # Enter an intentionally incorrect six-digit code and submit it.
    print("[STEP] Enter wrong OTP: 000000")
    otp_page.fill_code("000000")
    otp_page.click_verify()

    # Verify the wrong code cannot navigate to the authenticated home screen.
    otp_page.assert_not_on_home(app_base_url)
    otp_page.assert_feedback(EXPECTED_INVALID_OTP_MESSAGE)
    print("[PASS] Wrong OTP was rejected and home screen stayed blocked\n")


@allure.epic("NutriScan AI")
@allure.feature("Signup and OTP")
@allure.story("Blank OTP")
@allure.title("Negative: blank OTP shows validation and blocks home access")
@allure.tag("negative", "validation", "affirmation")
def test_blank_otp_does_not_open_home(
    login_page: LoginPage,
    signup_page: SignupPage,
    otp_page: OtpPage,
    app_base_url: str,
) -> None:
    """Verify verification cannot proceed when the OTP field is blank."""

    # Create a fresh signup and reach the OTP screen.
    print("\n[START] Blank-OTP negative test")
    _create_signup_to_otp(login_page, signup_page, app_base_url)

    # Click verify without entering an OTP value.
    print("[STEP] Click Verify & Continue with blank OTP")
    otp_page.click_verify()

    # Require both route protection and the exact blank-code feedback.
    otp_page.assert_not_on_home(app_base_url)
    otp_page.assert_feedback(EXPECTED_EMPTY_OTP_MESSAGE)
    print("[PASS] Blank OTP was rejected and home screen stayed blocked\n")


@allure.epic("NutriScan AI")
@allure.feature("Signup and OTP")
@allure.story("Resend OTP")
@allure.title("Integration: resend OTP shows the correct feedback")
@allure.tag("integration", "affirmation")
def test_resend_otp_shows_feedback(
    login_page: LoginPage,
    signup_page: SignupPage,
    otp_page: OtpPage,
    app_base_url: str,
) -> None:
    """Verify the resend control is available and provides its expected feedback."""

    # Create a fresh signup and reach OTP.
    print("\n[START] Resend-OTP integration test")
    _create_signup_to_otp(login_page, signup_page, app_base_url)

    # Request a replacement verification code.
    print("[STEP] Click Resend")
    otp_page.click_resend()

    # Assert the resend feedback is rendered on the OTP screen.
    otp_page.assert_feedback(EXPECTED_RESEND_MESSAGE)
    print("[PASS] Resend feedback message matched\n")


@allure.epic("NutriScan AI")
@allure.feature("Signup and OTP")
@allure.story("Resend OTP field state")
@allure.title("Edge: resend clears the existing OTP value")
@allure.tag("edge", "integration", "affirmation")
def test_resend_clears_otp_field(
    login_page: LoginPage,
    signup_page: SignupPage,
    otp_page: OtpPage,
    app_base_url: str,
) -> None:
    """Verify requesting a new OTP clears any code already entered."""

    # Create a fresh signup and reach OTP.
    print("\n[START] Resend-clears-field edge test")
    _create_signup_to_otp(login_page, signup_page, app_base_url)

    # Enter a code first to make the field-clearing behavior observable.
    otp_page.fill_code("123456")
    print("[STEP] Click Resend after entering an OTP")
    otp_page.click_resend()

    # Require the field to be empty after resend completes.
    expect(otp_page.otp_input).to_have_value("")
    print("[PASS] Resend cleared the OTP field\n")


@allure.epic("NutriScan AI")
@allure.feature("Signup and OTP")
@allure.story("OTP input contract")
@allure.title("Negative: OTP field accepts numeric characters only")
@allure.tag("negative", "validation", "affirmation")
def test_otp_field_accepts_numbers_only(
    login_page: LoginPage,
    signup_page: SignupPage,
    otp_page: OtpPage,
    app_base_url: str,
) -> None:
    """Verify alphabetic and symbolic characters are not accepted by the OTP control."""

    # Create a fresh signup and reach OTP.
    print("\n[START] OTP-numeric-only negative test")
    _create_signup_to_otp(login_page, signup_page, app_base_url)

    # Attempt to enter a mixed alphanumeric and symbolic code.
    print("[STEP] Enter mixed OTP value: 12ab@3")
    otp_page.fill_code("12ab@3")

    # Assert the resulting field value contains digits only.
    otp_page.assert_numeric_value_only()
    print("[PASS] OTP field rejected non-numeric characters\n")


@allure.epic("NutriScan AI")
@allure.feature("Signup and OTP")
@allure.story("Browser back navigation")
@allure.title("Integration: browser back leaves the authenticated home screen")
@allure.tag("integration", "affirmation")
def test_browser_back_from_home_leaves_home_screen(
    login_page: LoginPage,
    signup_page: SignupPage,
    otp_page: OtpPage,
    home_page: HomePage,
    app_base_url: str,
) -> None:
    """Verify browser Back after signup does not incorrectly retain the home screen."""

    # Create a fresh signup and reach OTP.
    print("\n[START] Browser-back integration test")
    _create_signup_to_otp(login_page, signup_page, app_base_url)

    # Verify the valid OTP and confirm authenticated home content first.
    verified_home_page = otp_page.verify(SIGNUP_OTP, app_base_url)
    verified_home_page.assert_signup_completed(app_base_url)
    print("[STEP] Press browser Back from authenticated home")

    # Navigate back and require that the browser leaves the authenticated root route.
    home_page.go_back()
    expect(home_page.page).not_to_have_url(f"{app_base_url}/")
    print("[PASS] Browser Back left the authenticated home screen\n")


