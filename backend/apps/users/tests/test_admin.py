from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class UserAdminApiTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username="superadmin",
            email="superadmin@example.com",
            password="Pass12345!",
            role=User.Role.SUPER_ADMIN,
            is_staff=True,
        )
        self.target = User.objects.create_user(
            username="target",
            email="target@example.com",
            password="Pass12345!",
        )
        self.regular = User.objects.create_user(
            username="regular",
            email="regular@example.com",
            password="Pass12345!",
        )

    def test_list_requires_super_admin(self):
        self.client.force_authenticate(user=self.regular)
        response = self.client.get("/api/users/admin/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_lists_users(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get("/api/users/admin/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        usernames = {item["username"] for item in response.data["results"]}
        self.assertIn("target", usernames)

    def test_admin_can_patch_user(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.patch(
            f"/api/users/admin/{self.target.id}/",
            {"first_name": "Patched"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.target.refresh_from_db()
        self.assertEqual(self.target.first_name, "Patched")

    def test_admin_soft_deletes_other_user(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.delete(f"/api/users/admin/{self.target.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.target.refresh_from_db()
        self.assertFalse(self.target.is_active)

    def test_admin_cannot_soft_delete_self(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.delete(f"/api/users/admin/{self.admin.id}/")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_admin_hard_deletes_other_user(self):
        self.client.force_authenticate(user=self.admin)
        target_id = self.target.id
        response = self.client.delete(f"/api/users/admin/{target_id}/hard-delete/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(User.objects.filter(pk=target_id).exists())
