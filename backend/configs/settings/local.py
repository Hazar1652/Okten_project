import os

from dotenv import load_dotenv

from .base import *  # noqa: F403

load_dotenv(BASE_DIR / ".env")

DEBUG = True

ALLOWED_HOSTS = [
    h.strip()
    for h in os.getenv(
        "DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1,backend"
    ).split(",")
    if h.strip()
]
