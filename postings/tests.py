from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Posting


class PostingDetailTests(APITestCase):
    def setUp(self):
        # Create a fresh posting in the test database before each test.
        self.posting = Posting.objects.create(
            title="Junior Backend Developer",
            company_name="Example Company",
            description="Build Python APIs and work with PostgreSQL.",
            source_url="https://example.com/jobs/1",
        )

    def test_existing_posting_returns_its_details(self):
        # Build the URL using the route name and the generated ID.
        url = reverse(
            "posting_detail",
            kwargs={"pk": self.posting.pk},
        )

        # Request the posting as JSON.
        response = self.client.get(url, HTTP_ACCEPT="application/json")

        # Verify the status and all fields in the response.
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json(),
            {
                "id": self.posting.pk,
                "title": "Junior Backend Developer",
                "company_name": "Example Company",
                "description": "Build Python APIs and work with PostgreSQL.",
                "source_url": "https://example.com/jobs/1",
                "created_at": self.posting.created_at.isoformat().replace(
                    "+00:00", "Z"
                ),
            },
        )

    def test_missing_posting_returns_404(self):
        # Remove the posting so its ID is guaranteed to be missing.
        missing_pk = self.posting.pk
        self.posting.delete()

        url = reverse(
            "posting_detail",
            kwargs={"pk": missing_pk},
        )

        response = self.client.get(url, HTTP_ACCEPT="application/json")

        # A missing resource should produce 404 instead of 500.
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)