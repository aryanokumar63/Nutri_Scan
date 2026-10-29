"""Page object for the NutriScan login screen."""

from playwright.sync_api import Page


class LoginPage:
    """Expose the login page's signup navigation action."""

    def __init__(self, page: Page) -> None:
        # Store the isolated page object created for the current test.
        self.page = page

        # Use the accessible link name verified on the live login page.
        self.signup_link = page.get_by_role("link", name="Sign up")

    def open(self, base_url: str) -> None:
        """Open the application login page."""

        # Start from the configured host and let the page object handle the route.
        self.page.goto(f"{base_url}/login")

    def click_signup(self) -> None:
        """Navigate from login to signup."""

        # Click the verified Sign up link instead of depending on fragile CSS or DOM indexes.
        self.signup_link.click()

