"""Клієнт Google Places API (New). Ключ лише на сервері."""

from __future__ import annotations

import logging
from typing import Any
from urllib.parse import quote

import requests
from django.conf import settings

from .coordinates import coordinate_to_str

logger = logging.getLogger(__name__)

PLACES_BASE = "https://places.googleapis.com/v1"
AUTOCOMPLETE_TIMEOUT = 8
DETAILS_TIMEOUT = 10


class PlacesNotConfigured(Exception):
    pass


class PlacesAPIError(Exception):
    pass


def _api_key() -> str:
    key = getattr(settings, "GOOGLE_PLACES_API_KEY", "") or ""
    if not key.strip():
        raise PlacesNotConfigured(
            "GOOGLE_PLACES_API_KEY не налаштовано. Додай ключ у backend/.env"
        )
    return key.strip()


def _headers(field_mask: str | None = None) -> dict[str, str]:
    headers = {
        "X-Goog-Api-Key": _api_key(),
        "Content-Type": "application/json",
    }
    if field_mask:
        headers["X-Goog-FieldMask"] = field_mask
    return headers


def _humanize_places_error(status_code: int, message: str) -> str:
    lowered = (message or "").lower()
    if status_code == 403 and "blocked" in lowered:
        return (
            "Google заблокував запит: увімкни «Places API (New)» у Library і дозволь його "
            "в обмеженнях API-ключа (або тимчасово зніми restrictions). Також перевір білінг GCP."
        )
    if status_code == 403:
        return f"Доступ заборонено (403): {message}"
    if status_code == 400 and "billing" in lowered:
        return "Увімкни білінг у Google Cloud для цього проєкту."
    return message or f"Помилка Google Places ({status_code})"


def _raise_for_status(response: requests.Response) -> None:
    if response.ok:
        return
    try:
        payload = response.json()
        message = payload.get("error", {}).get("message") or response.text
    except Exception:
        message = response.text or response.reason
    logger.warning("Google Places API error %s: %s", response.status_code, message)
    raise PlacesAPIError(_humanize_places_error(response.status_code, message))


def autocomplete(input_text: str, session_token: str = "") -> list[dict[str, Any]]:
    """Підказки адрес/закладів для поля пошуку."""
    text = (input_text or "").strip()
    if len(text) < 2:
        return []

    body: dict[str, Any] = {
        "input": text,
        "languageCode": "uk",
        "includedRegionCodes": ["ua"],
    }
    if session_token:
        body["sessionToken"] = session_token

    response = requests.post(
        f"{PLACES_BASE}/places:autocomplete",
        json=body,
        headers=_headers(),
        timeout=AUTOCOMPLETE_TIMEOUT,
    )
    _raise_for_status(response)
    data = response.json()

    suggestions = []
    for item in data.get("suggestions", []):
        prediction = item.get("placePrediction") or {}
        place_id = prediction.get("placeId")
        if not place_id:
            continue
        text_block = prediction.get("text") or {}
        label = text_block.get("text") or ""
        structured = prediction.get("structuredFormat") or {}
        main = (structured.get("mainText") or {}).get("text") or ""
        secondary = (structured.get("secondaryText") or {}).get("text") or ""
        suggestions.append(
            {
                "place_id": place_id,
                "description": label or f"{main}, {secondary}".strip(", "),
                "main_text": main,
                "secondary_text": secondary,
            }
        )
    return suggestions


def place_details(place_id: str, session_token: str = "") -> dict[str, Any]:
    """Деталі місця для автозаповнення форми закладу."""
    pid = (place_id or "").strip()
    if not pid:
        raise PlacesAPIError("place_id обовʼязковий")

    field_mask = (
        "id,displayName,formattedAddress,location,"
        "internationalPhoneNumber,nationalPhoneNumber,websiteUri"
    )
    params = {}
    if session_token:
        params["sessionToken"] = session_token

    response = requests.get(
        f"{PLACES_BASE}/places/{quote(pid, safe='')}",
        headers=_headers(field_mask),
        params=params or None,
        timeout=DETAILS_TIMEOUT,
    )
    _raise_for_status(response)
    data = response.json()

    location = data.get("location") or {}
    lat = location.get("latitude")
    lng = location.get("longitude")
    display = data.get("displayName") or {}
    name = display.get("text") or ""

    phone = data.get("internationalPhoneNumber") or data.get("nationalPhoneNumber") or ""

    return {
        "place_id": data.get("id") or pid,
        "name": name,
        "address": data.get("formattedAddress") or "",
        "latitude": coordinate_to_str(lat) if lat is not None else "",
        "longitude": coordinate_to_str(lng) if lng is not None else "",
        "phone_number": phone,
        "website": data.get("websiteUri") or "",
    }
