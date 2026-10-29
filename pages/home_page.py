"""Page object for the authenticated NutriScan home page."""

from playwright.sync_api import Error, Page, expect


class HomePage:
    """Represent the page shown after successful OTP verification."""

    def __init__(self, page: Page) -> None:
        # Reuse the same isolated browser page after OTP verification completes.
        self.page = page

        # This heading is the verified authenticated-home marker from the live application.
        self.dashboard_heading = page.get_by_role("heading", name="Know exactly what's in your food")

    def assert_signup_completed(self, base_url: str) -> None:
        """Fail the test unless OTP verification opened the authenticated home page."""

        # Catch browser assertion errors and expose a signup-specific failure message.
        try:
            # Confirm the browser left the OTP route and reached the application home route.
            expect(self.page).to_have_url(f"{base_url}/")

            # Confirm authenticated home content is visible after successful signup verification.
            expect(self.dashboard_heading).to_be_visible()
        except (Error, AssertionError) as error:
            # Preserve the original Playwright details while clearly marking signup as incomplete.
            raise AssertionError(f"Signup did not complete after OTP verification: {error}") from error

    def go_back(self) -> None:
        """Navigate backward using the browser history."""

        # Use browser history to validate the user's Back action after signup completion.
        self.page.go_back()


