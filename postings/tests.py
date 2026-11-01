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
        self.assertEqual(response.json(), {
            "count": 0,
            "next": None,
            "previous": None,
            "results": [],
            },
        )

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
        returned_ids = [posting["id"] for posting in response.json()['results']]

        self.assertEqual(returned_ids,[newer_posting.pk, older_posting.pk],
        )

    def test_postings_are_split_across_pages(self):
        
        # Create enough postings to require two pages.
        for index in range(21):
            Posting.objects.create(
                title=f"Backend Developer {index}",
                company_name="Demo Company",
                description="Build backend services.",
                source_url=f"https://example.com/jobs/{index}",
            )

        # Request the first page.
        first_response = self.client.get(
            "/api/v1/postings/",
            HTTP_ACCEPT="application/json",
        )

        self.assertEqual(first_response.status_code, status.HTTP_200_OK)
        first_page = first_response.json()

        # Verify the total count, page size, and navigation.
        self.assertEqual(first_page["count"], 21)
        self.assertEqual(len(first_page["results"]), 20)
        self.assertIsNone(first_page["previous"])
        self.assertIsNotNone(first_page["next"])

        # Request the second page.
        second_response = self.client.get(
            "/api/v1/postings/",
            {"page": 2},
            HTTP_ACCEPT="application/json",
        )

        self.assertEqual(second_response.status_code, status.HTTP_200_OK)
        second_page = second_response.json()

        # Only one posting should remain on the final page.
        self.assertEqual(second_page["count"], 21)
        self.assertEqual(len(second_page["results"]), 1)
        self.assertIsNotNone(second_page["previous"])
        self.assertIsNone(second_page["next"])

        # Verify that the pages contain every posting exactly once.
        returned_ids = [posting["id"] for posting in first_page["results"] + second_page["results"]]
        expected_ids = set(Posting.objects.values_list("pk", flat=True))

        self.assertEqual(len(returned_ids), len(set(returned_ids)))
        self.assertEqual(set(returned_ids), expected_ids)

class PostingCreateTests(APITestCase):
    def test_missing_title_returns_400_without_creating_posting(self):
        # Prepare input that is missing the required title.
        payload = {
            "title": "",
            "company_name": "Demo Company",
            "description": "This request must not create a posting.",
            "source_url": "https://example.com/jobs/invalid",
        }

        # Record the number of postings before the request.
        count_before = Posting.objects.count()

        # Send the payload as JSON.
        response = self.client.post(
            "/api/v1/postings/",
            payload,
            format="json",
        )

        # Verify that validation rejected the request.
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertIn("title", response.json())

        # Verify that the request did not create a database record.
        self.assertEqual(Posting.objects.count(), count_before)

    def test_missing_title_returns_400_without_creating_posting(self):
            # Prepare input that is missing the required title.
            payload = {
                "title": "Software Engineer Intern",
                "company_name": "",
                "description": "This request must not create a posting.",
                "source_url": "https://example.com/jobs/invalid",
            }
    
            # Record the number of postings before the request.
            count_before = Posting.objects.count()
    
            # Send the payload as JSON.
            response = self.client.post(
                "/api/v1/postings/",
                payload,
                format="json",
            )
    
            # Verify that validation rejected the request.
            self.assertEqual(
                response.status_code,
                status.HTTP_400_BAD_REQUEST,
            )
            self.assertIn("company_name", response.json())
    
            # Verify that the request did not create a database record.
            self.assertEqual(Posting.objects.count(), count_before)

    def test_valid_input_creates_posting(self):
        # Prepare valid input for a new posting.
        payload = {
            "title": "Python API Developer",
            "company_name": "Demo Company",
            "description": "Develop and test backend APIs.",
            "source_url": "https://example.com/jobs/python-api",
        }

        count_before = Posting.objects.count()

        # Send a JSON request to create the posting.
        response = self.client.post(
            "/api/v1/postings/",
            payload,
            format="json",
        )

        # Verify successful creation and exactly one new record.
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )
        self.assertEqual(Posting.objects.count(), count_before + 1)

        # Retrieve the actual record using the ID returned by the API.
        response_data = response.json()
        saved_posting = Posting.objects.get(pk=response_data["id"])

        # Verify that every submitted value was stored correctly.
        for field, expected_value in payload.items():
            with self.subTest(field=field):
                self.assertEqual(getattr(saved_posting, field), expected_value)

        # Verify that the API returned the submitted values too.
        for field, expected_value in payload.items():
            with self.subTest(response_field=field):
                self.assertEqual(
                    response_data[field],
                    expected_value,
                )

    def test_client_cannot_set_read_only_fields(self):
        # Attempt to provide values for system-managed fields.
        payload = {
            "id": 999999,
            "title": "Backend Developer",
            "company_name": "Demo Company",
            "description": "Build backend services.",
            "source_url": "https://example.com/jobs/backend",
            "created_at": "2000-01-01T00:00:00Z",
        }

        response = self.client.post(
            "/api/v1/postings/",
            payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        # Read the saved record using the server-generated ID.
        response_data = response.json()
        saved_posting = Posting.objects.get(pk=response_data["id"])

        # Confirm that the database generated the ID.
        self.assertNotEqual(saved_posting.pk, payload["id"])

        # Confirm that Django generated the creation timestamp.
        self.assertNotEqual(saved_posting.created_at.year, 2000)

        self.assertNotEqual(response_data["created_at"], payload["created_at"])
        self.assertNotEqual(response_data["id"], payload["id"])