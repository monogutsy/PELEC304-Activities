"""PythonAnywhere settings; read the private config outside the repository."""
import json

from django.core.exceptions import ImproperlyConfigured

from .settings import *  # noqa: F403

config_path = Path(os.environ.get(
    "DJANGO_CONFIG_FILE", Path.home() / ".config" / "pelec304" / "config.json"
))
if not config_path.is_file():
    raise ImproperlyConfigured("Create the private config described in DEPLOYMENT.md.")
config = json.loads(config_path.read_text(encoding="utf-8"))
SECRET_KEY = config.get("secret_key", "")
if not isinstance(SECRET_KEY, str) or len(SECRET_KEY) < 50:
    raise ImproperlyConfigured("The production secret_key must have at least 50 characters.")

DEBUG = False
ALLOWED_HOSTS = ["monogutsy.pythonanywhere.com"]
CSRF_TRUSTED_ORIGINS = ["https://monogutsy.pythonanywhere.com"]
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_HSTS_SECONDS = 31536000
# Keep subdomain coverage and browser preload as separate hosting decisions.
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False
