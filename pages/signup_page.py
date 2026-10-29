"""Page object for the NutriScan signup screen."""

from playwright.sync_api import Error, Page, expect


class SignupPage:
    """Expose signup actions and locators through a reusable page object."""

    def __init__(self, page: Page) -> None:
        # Store the isolated Playwright page supplied by the fixture for this test.
        self.page = page

        # Locate the email control using the placeholder verified on the live signup page.
        self.email_input = page.get_by_placeholder("you@example.com")

        # Locate the password control using the placeholder verified on the live signup page.
        self.password_input = page.get_by_placeholder("Min. 8 characters")

        # Locate confirmation using its distinct placeholder verified on the live signup page.
        self.confirm_password_input = page.get_by_placeholder("Re-enter password")

        # Locate the submit action by its accessible button name verified on the live page.
        self.create_account_button = page.get_by_role("button", name="Create account")

    def open(self, base_url: str) -> None:
        """Open the signup route using the configured application URL."""

        # Navigate only this test's browser page to prevent state sharing with other tests.
        self.page.goto(f"{base_url}/signup")

    def fill_signup_form(self, email: str, password: str) -> None:
        """Fill all currently mandatory signup fields for the positive case."""

        # Catch Playwright failures here so the test receives a clear page-object error message.
        try:
            # Enter the unique yopmail address generated for this test run.
            self.email_input.fill(email)

            # Enter the strong password configured for the positive signup case.
            self.password_input.fill(password)

            # Match the confirmation value exactly to satisfy the form validation rule.
            self.confirm_password_input.fill(password)
        except Error as error:
            # Convert a browser interaction failure into a readable test failure with its cause.
            raise AssertionError(f"Unable to fill signup form: {error}") from error

    def submit(self) -> None:
        """Submit the completed signup form."""

        # Catch submit failures so locator, page, or navigation issues are reported clearly.
        try:
            # Click the verified Create account action after all mandatory fields are populated.
            self.create_account_button.click()
        except Error as error:
            # Preserve the original Playwright exception while adding business context.
            raise AssertionError(f"Unable to submit signup form: {error}") from error

    def assert_validation_message(self, expected_message: str) -> None:
        """Assert that the exact application validation message is visible."""

        # Locate the message by exact text so a different or incomplete message fails the test.
        try:
            expect(self.page.get_by_text(expected_message, exact=True)).to_be_visible()
        except (Error, AssertionError) as error:
            # Include the expected contract and current page text in the failure diagnosis.
            raise AssertionError(
                f"Expected validation message was not displayed: '{expected_message}'. "
                f"Current page text: {self.page.locator('body').inner_text()}"
            ) from error

    def assert_email_native_validation(self, expected_text: str) -> None:
        """Assert that the browser email validation contains the expected wording."""

        # Read the browser's native validation message from the inspected email input.
        message = self.email_input.evaluate("element => element.validationMessage")

        # Compare the stable message fragment instead of a locale-specific full sentence.
        assert expected_text in message, (
            f"Expected email validation text '{expected_text}', but received '{message}'"
        )

