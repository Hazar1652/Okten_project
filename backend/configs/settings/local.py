from .base import *  # noqa: F403

DEBUG = True

ALLOWED_HOSTS = [
    h.strip()
    for h in __import__("os").getenv(
        "DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1,backend"
    ).split(",")
    if h.strip()
]

STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}
