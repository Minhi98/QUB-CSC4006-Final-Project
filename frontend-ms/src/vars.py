import os

HEADERS = {'Accept': 'application/json'}

SECRET_KEY = os.environ.get('SECRET_KEY', None)
assert SECRET_KEY is not None, "Set env var SECRET_KEY for CSRF Protection"

INTEGRATION = os.environ.get("INTEGRATION_URL", "")
assert INTEGRATION is not None, "Set the integration url so requests can be made."