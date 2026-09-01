from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.test import override_settings
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()

class PlacesAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user("u1", "u1@t.com", "Pass12345!")
        self.client.force_authenticate(user=self.user)

    @patch("apps.venues.views.places_autocomplete.autocomplete")
    def test_autocomplete_requires_auth_off_for_anon(self, mock_auto):
        self.client.force_authenticate(user=None)
        response = self.client.get("/api/places/autocomplete/?q=lviv")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @patch("apps.venues.views.places_autocomplete.autocomplete")
    def test_autocomplete_returns_suggestions(self, mock_auto):
        mock_auto.return_value = [
            {"place_id": "ChIJx", "description": "Lviv", "main_text": "Lviv", "secondary_text": "UA"}
        ]
        response = self.client.get("/api/places/autocomplete/?q=lviv&session_token=abc")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["suggestions"]), 1)

    @override_settings(GOOGLE_PLACES_API_KEY="test-key")
    @patch("apps.venues.google_places.requests.get")
    def test_place_details_rounds_coordinates(self, mock_get):
        from apps.venues.google_places import place_details

        mock_resp = MagicMock()
        mock_resp.ok = True
        mock_resp.json.return_value = {
            "id": "ChIJx",
            "displayName": {"text": "Cafe"},
            "formattedAddress": "Street 1",
            "location": {"latitude": 49.840319199999996, "longitude": 24.027718699999998},
        }
        mock_get.return_value = mock_resp

        data = place_details("ChIJx")
        self.assertEqual(data["latitude"], "49.840319")
        self.assertEqual(data["longitude"], "24.027719")

    @patch("apps.venues.views.places_details.place_details")
    def test_details_returns_normalized_payload(self, mock_details):
        mock_details.return_value = {
            "place_id": "ChIJx",
            "name": "Cafe",
            "address": "Street 1",
            "latitude": "49.84",
            "longitude": "24.03",
            "phone_number": "+380",
            "website": "https://example.com",
        }
        response = self.client.get("/api/places/details/?place_id=ChIJx")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Cafe")
