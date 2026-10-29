"""Safe, reusable positive-case data for signup tests."""

from datetime import datetime, timezone
from uuid import uuid4


# Keep the requested positive-case password in one reusable location for future signup tests.
SIGNUP_PASSWORD = "Aryan@123"

# Keep the OTP supplied for the current test environment available for the OTP page object.
SIGNUP_OTP = "123456"

# Exact validation text verified on the live signup page for blank input.
EXPECTED_REQUIRED_FIELDS_MESSAGE = "Please fill in all fields"

# Exact validation text verified on the live signup page for a short password.
EXPECTED_SHORT_PASSWORD_MESSAGE = "Password must be at least 8 characters long"

# Exact validation text verified on the live signup page for a mismatch.
EXPECTED_PASSWORD_MISMATCH_MESSAGE = "Passwords do not match"

# Stable Chromium validation fragment verified for an invalid email address.
EXPECTED_INVALID_EMAIL_MESSAGE = "missing an '@'"

# Expected security contract for a weak password; the live app currently does not show it.
EXPECTED_WEAK_PASSWORD_MESSAGE = "Password must include uppercase, lowercase, number, and special character"

# Expected feedback contract for an incorrect OTP.
EXPECTED_INVALID_OTP_MESSAGE = "Invalid verification code"

# Expected feedback contract when verification is submitted without an OTP.
EXPECTED_EMPTY_OTP_MESSAGE = "Please enter the verification code"

# Expected feedback contract after requesting a replacement OTP.
EXPECTED_RESEND_MESSAGE = "OTP resent successfully"

# Expected feedback contract when an unverified email is submitted again.
EXPECTED_DUPLICATE_EMAIL_MESSAGE = "An account with this email already exists"


def create_unique_signup_email() -> str:
    """Create a unique yopmail address for every signup attempt."""

    # Combine UTC time and a random suffix so parallel or repeated runs do not reuse an account.
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f")
    random_suffix = uuid4().hex[:8]

    # Return the requested yopmail format while keeping the local part unique.
    return f"aryan_{timestamp}_{random_suffix}@yopmail.com"

