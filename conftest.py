import os


def pytest_sessionstart(session) -> None:
    """Set environment variables for test session."""

    # Use a pytest temporary directory for cache, instead of the user's cache
    p = session.config._tmp_path_factory.mktemp("pint-cache", numbered=False)
    os.environ.setdefault("IAM_UNITS_CACHE", str(p))

    # Preserve behaviour expected by test_units[EUR_2005--]
    os.environ.setdefault("IAM_UNITS_CURRENCY", "EXC,2005")
