"""Central configuration for the NutriScan UI test suite."""

import os


# Read the application URL from the environment so CI or another test target can override it.
BASE_URL = os.getenv("NUTRISCAN_BASE_URL", "https://dev-nutriscan.itechnolabs.tech")

# Keep the signup route in one place so page objects and tests do not duplicate URL strings.
SIGNUP_PATH = "/signup"
