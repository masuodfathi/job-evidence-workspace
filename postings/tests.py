from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from datetime import timedelta
from django.utils import timezone

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


class PostingListTests(APITestCase):
    def test_empty_list_returns_200(self):
        # Request the list when the test database has no postings.
        response = self.client.get(
            "/api/v1/postings/",
            HTTP_ACCEPT="application/json",
        )

        # An empty collection is still a successful response.
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), [])

    def test_postings_are_returned_newest_first(self):
        # Create two fictional postings in the test database.
        older_posting = Posting.objects.create(
            title="Older Posting",
            company_name="Example Company",
            description="An older job posting.",
            source_url="https://example.com/jobs/older",
        )

        newer_posting = Posting.objects.create(
            title="Newer Posting",
            company_name="Example Company",
            description="A newer job posting.",
            source_url="https://example.com/jobs/newer",
        )

        # Set explicit timestamps so the test does not depend on execution speed.
        now = timezone.now()

        Posting.objects.filter(pk=older_posting.pk).update(
            created_at=now - timedelta(days=1),
        )
        Posting.objects.filter(pk=newer_posting.pk).update(
            created_at=now,
        )

        # Request the posting list.
        response = self.client.get(
            "/api/v1/postings/",
            HTTP_ACCEPT="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify that the newer posting appears before the older one.
        returned_ids = [posting["id"] for posting in response.json()]

        self.assertEqual(returned_ids,[newer_posting.pk, older_posting.pk],
        )