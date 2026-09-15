from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from apps.common.models import SitePage, TopCategory
from apps.venues.models import Tag

User = get_user_model()


class SitePageApiTests(APITestCase):
    def setUp(self):
        self.page = SitePage.objects.create(
            slug="about",
            title="Про нас",
            content="Okten content",
        )

    def test_list_pages(self):
        response = self.client.get("/api/pages/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(response.data["count"], 1)

    def test_retrieve_page_by_slug(self):
        response = self.client.get("/api/pages/about/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Про нас")


class TopCategoryApiTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username="tadmin",
            email="tadmin@example.com",
            password="Pass12345!",
            role=User.Role.SUPER_ADMIN,
        )
        self.user = User.objects.create_user(
            username="tuser",
            email="tuser@example.com",
            password="Pass12345!",
        )
        self.tag = Tag.objects.create(name="Кафе", slug="cafe-cat")
        self.category = TopCategory.objects.create(
            name="Топ кафе",
            tag=self.tag,
            order=1,
            is_active=True,
        )

    def test_list_active_categories_public(self):
        TopCategory.objects.create(name="Hidden", order=2, is_active=False)
        response = self.client.get("/api/top-categories/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        names = [item["name"] for item in response.data["results"]]
        self.assertIn("Топ кафе", names)
        self.assertNotIn("Hidden", names)

    def test_retrieve_category(self):
        response = self.client.get(f"/api/top-categories/{self.category.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Топ кафе")

    def test_admin_can_create_category(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(
            "/api/top-categories/",
            {"name": "Нова", "tag_id": self.tag.id, "order": 3, "is_active": True},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_regular_user_cannot_create_category(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            "/api/top-categories/",
            {"name": "Hack", "order": 9},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
