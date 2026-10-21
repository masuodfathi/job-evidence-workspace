from django.test import SimpleTestCase


class HealthCheckTests(SimpleTestCase):
    def test_health_endpoint_returns_ok(self):
        # Send a test request without starting a web server.
        response = self.client.get("/api/v1/health/")

        # Verify that the request succeeds.
        self.assertEqual(response.status_code, 200)

        # Verify the expected JSON response.
        self.assertEqual(response.json(), {"status": "ok"})