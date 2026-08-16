import hashlib
import hmac
import json
import os
from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse


WEBHOOK_SECRET = "test-webhook-secret"


def _signature(body: bytes, secret: str = WEBHOOK_SECRET) -> str:
    digest = hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()
    return f"sha256={digest}"


class DeployWebhookTests(TestCase):
    def _post(self, *, event="push", ref="refs/heads/main", signature=None):
        body = json.dumps({"ref": ref}).encode("utf-8")
        return self.client.post(
            reverse("deploy-webhook"),
            data=body,
            content_type="application/json",
            HTTP_X_GITHUB_EVENT=event,
            HTTP_X_HUB_SIGNATURE_256=signature or _signature(body),
        )

    def test_hello_world_page_is_available(self):
        response = self.client.get(reverse("hello-world"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Hello World!")
        self.assertContains(response, "/api/products/")

    @patch.dict(os.environ, {"GITHUB_WEBHOOK_SECRET": WEBHOOK_SECRET})
    def test_webhook_rejects_invalid_signature(self):
        response = self._post(signature="sha256=invalid")

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()["detail"], "Invalid webhook signature.")

    @patch.dict(os.environ, {"GITHUB_WEBHOOK_SECRET": WEBHOOK_SECRET})
    @patch("bookstore.views._pull_main_branch")
    @patch("bookstore.views._reload_pythonanywhere")
    def test_ping_validates_webhook_without_deploying(self, reload_mock, pull_mock):
        response = self._post(event="ping")

        self.assertEqual(response.status_code, 200)
        pull_mock.assert_not_called()
        reload_mock.assert_not_called()

    @patch.dict(os.environ, {"GITHUB_WEBHOOK_SECRET": WEBHOOK_SECRET})
    @patch("bookstore.views._pull_main_branch")
    @patch("bookstore.views._reload_pythonanywhere")
    def test_non_push_event_is_ignored(self, reload_mock, pull_mock):
        response = self._post(event="issues")

        self.assertEqual(response.status_code, 202)
        pull_mock.assert_not_called()
        reload_mock.assert_not_called()

    @patch.dict(os.environ, {"GITHUB_WEBHOOK_SECRET": WEBHOOK_SECRET})
    @patch("bookstore.views._pull_main_branch")
    @patch("bookstore.views._reload_pythonanywhere")
    def test_push_outside_main_is_ignored(self, reload_mock, pull_mock):
        response = self._post(ref="refs/heads/feature/test")

        self.assertEqual(response.status_code, 202)
        pull_mock.assert_not_called()
        reload_mock.assert_not_called()

    @patch.dict(os.environ, {"GITHUB_WEBHOOK_SECRET": WEBHOOK_SECRET})
    @patch("bookstore.views._pull_main_branch", return_value="abc123")
    @patch("bookstore.views._reload_pythonanywhere")
    def test_signed_main_push_updates_and_reloads(self, reload_mock, pull_mock):
        response = self._post()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["commit"], "abc123")
        pull_mock.assert_called_once_with()
        reload_mock.assert_called_once_with()
