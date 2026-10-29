"""Page object for the email OTP verification screen."""

from playwright.sync_api import Error, Page, expect

from pages.home_page import HomePage


class OtpPage:
    """Expose OTP verification controls through the Page Object Model."""

    def __init__(self, page: Page) -> None:
        # Reuse the same isolated page context that completed signup for this test.
        self.page = page

        # Locate the OTP input using the exact placeholder inspected on the live verification page.
        self.otp_input = page.get_by_placeholder("Enter 6-digit code")

        # Locate the verification action using its accessible name from the live page.
        self.verify_button = page.get_by_role("button", name="Verify & Continue")

        # Locate the resend action so resend behavior can be tested independently.
        self.resend_button = page.get_by_role("button", name="Resend")

        # Locate the back link so an unverified user can be tested against duplicate signup behavior.
        self.back_link = page.get_by_role("link", name="Back")

    def fill_code(self, otp: str) -> None:
        """Enter an OTP value into the verification field."""

        # Catch browser interaction failures and expose a clear OTP page-object error.
        try:
            # Fill the exact value supplied by the test case for wrong, blank, or valid OTP checks.
            self.otp_input.fill(otp)
        except Error as error:
            # Preserve the original Playwright cause while adding OTP context.
            raise AssertionError(f"Unable to enter OTP '{otp}': {error}") from error

    def click_verify(self) -> None:
        """Click Verify & Continue without assuming that the OTP is valid."""

        # Keep click behavior separate so invalid and blank OTP tests can assert their own outcomes.
        try:
            # Submit the current OTP value and let the test validate the resulting route/message.
            self.verify_button.click()
        except Error as error:
            # Report a readable failure if the verification action cannot be clicked.
            raise AssertionError(f"Unable to click Verify & Continue: {error}") from error

    def click_resend(self) -> None:
        """Request a new OTP from the verification screen."""

        # Catch resend interaction failures so the test report identifies the failed action.
        try:
            # Click the verified Resend control and let the test assert its feedback and field state.
            self.resend_button.click()
        except Error as error:
            # Preserve the original Playwright cause while adding resend context.
            raise AssertionError(f"Unable to click Resend: {error}") from error

    def assert_not_on_home(self, base_url: str) -> None:
        """Assert that OTP verification has not opened the authenticated home page."""

        # A wrong, blank, or incomplete OTP must never navigate to the authenticated root route.
        expect(self.page).not_to_have_url(f"{base_url}/")

    def assert_feedback(self, expected_message: str) -> None:
        """Assert exact feedback text rendered by the OTP screen."""

        # Locate the application feedback by exact visible text for deterministic validation.
        try:
            expect(self.page.get_by_text(expected_message, exact=True)).to_be_visible()
        except (Error, AssertionError) as error:
            # Include current screen text so the Allure failure explains a message mismatch.
            raise AssertionError(
                f"Expected OTP feedback '{expected_message}' was not displayed. "
                f"Current page text: {self.page.locator('body').inner_text()}"
            ) from error

    def assert_numeric_value_only(self) -> None:
        """Assert that the OTP field contains digits only."""

        # Read the post-input value after the browser/component has applied its input filtering.
        value = self.otp_input.input_value()

        # Reject any alphabetic or symbolic character from the OTP control.
        assert value.isdigit() or value == "", f"OTP field accepted non-numeric value: '{value}'"

    def verify(self, otp: str, base_url: str) -> HomePage:
        """Enter OTP, submit it, and return the post-signup home page object."""

        # Catch both input and submit failures so the OTP step has a clear diagnostic.
        try:
            # Fill the six-digit code stored in config/test_data.py for this environment.
            self.fill_code(otp)

            # Submit the code only after the OTP input has been populated.
            self.click_verify()

            # Wait for the application to leave OTP verification and open its authenticated home route.
            self.page.wait_for_url(f"{base_url}/")

            # Return a page object responsible for validating successful signup completion.
            return HomePage(self.page)
        except Error as error:
            # Convert low-level browser errors into a readable page-object assertion failure.
            raise AssertionError(f"Unable to verify signup OTP: {error}") from error
