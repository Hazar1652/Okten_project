from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from rest_framework.test import APIClient

User = get_user_model()

@override_settings(
    GOOGLE_OAUTH_CLIENT_ID="google-client-id.apps.googleusercontent.com",
    FACEBOOK_APP_ID="987654321098765",
    FACEBOOK_APP_SECRET="real_facebook_app_secret_value",
)
class OAuthAuthTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    @patch("apps.users.social.requests.get")
    def test_google_auth_creates_user(self, mock_get):
        mock_get.return_value = MagicMock(
            status_code=200,
            json=lambda: {
                "aud": "google-client-id.apps.googleusercontent.com",
                "email": "new@gmail.com",
                "email_verified": "true",
                "given_name": "Test",
                "family_name": "User",
                "sub": "999",
            },
        )
        response = self.client.post("/api/auth/google/", {"id_token": "fake-token"}, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["is_new"])
        self.assertIn("access", response.data)
        user = User.objects.get(email="new@gmail.com")
        self.assertEqual(user.username, "new")
        self.assertNotEqual(user.username, "999")

    @patch("apps.users.social.requests.get")
    def test_google_auth_logs_in_existing_user(self, mock_get):
        User.objects.create_user(username="existing", email="existing@gmail.com", password="x")
        mock_get.return_value = MagicMock(
            status_code=200,
            json=lambda: {
                "aud": "google-client-id.apps.googleusercontent.com",
                "email": "existing@gmail.com",
                "email_verified": "true",
                "sub": "1",
            },
        )
        response = self.client.post("/api/auth/google/", {"id_token": "fake-token"}, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.data["is_new"])

    def test_oauth_config(self):
        response = self.client.get("/api/auth/oauth-config/")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["google_enabled"])
        self.assertTrue(response.data["facebook_enabled"])

    @override_settings(FACEBOOK_APP_ID="123456789", FACEBOOK_APP_SECRET="your_secret")
    def test_oauth_config_ignores_facebook_placeholders(self):
        response = self.client.get("/api/auth/oauth-config/")
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.data["facebook_enabled"])
        self.assertEqual(response.data["facebook_app_id"], "")
