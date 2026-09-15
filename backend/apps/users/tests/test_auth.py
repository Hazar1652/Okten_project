from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class AuthApiTests(APITestCase):
    def test_register_returns_tokens_and_user(self):
        response = self.client.post(
            "/api/auth/register/",
            {
                "username": "newuser",
                "email": "new@example.com",
                "password": "StrongPass123!",
                "password_confirm": "StrongPass123!",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertEqual(response.data["user"]["username"], "newuser")
        self.assertEqual(response.data["user"]["role"], User.Role.USER)

    def test_jwt_obtain_pair(self):
        User.objects.create_user(
            username="jwtuser",
            email="jwt@example.com",
            password="StrongPass123!",
        )
        response = self.client.post(
            "/api/auth/token/",
            {"username": "jwtuser", "password": "StrongPass123!"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)

    def test_me_requires_auth(self):
        response = self.client.get("/api/users/me/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_me_get_and_patch(self):
        user = User.objects.create_user(
            username="meuser",
            email="me@example.com",
            password="StrongPass123!",
        )
        self.client.force_authenticate(user=user)
        get_response = self.client.get("/api/users/me/")
        self.assertEqual(get_response.status_code, status.HTTP_200_OK)
        self.assertEqual(get_response.data["username"], "meuser")

        patch_response = self.client.patch(
            "/api/users/me/",
            {"first_name": "Іван"},
            format="json",
        )
        self.assertEqual(patch_response.status_code, status.HTTP_200_OK)
        user.refresh_from_db()
        self.assertEqual(user.first_name, "Іван")
