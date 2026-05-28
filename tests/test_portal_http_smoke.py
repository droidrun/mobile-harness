from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]


def load_portal_http_smoke():
    spec = importlib.util.spec_from_file_location("portal_http_smoke", ROOT / "scripts/portal_http_smoke.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules["portal_http_smoke"] = module
    spec.loader.exec_module(module)
    return module


class PortalHttpSmokeTest(unittest.TestCase):
    def test_missing_url_or_token_blocks_with_user_message(self) -> None:
        module = load_portal_http_smoke()
        result = module.run_from_values(None, None)
        self.assertFalse(result.ok)
        self.assertEqual(result.mode, "blocked")
        self.assertIn("requires MOBILE_HARNESS_PORTAL_URL and MOBILE_HARNESS_PORTAL_TOKEN", result.message)

    def test_wrong_token_fails_authenticated_version(self) -> None:
        module = load_portal_http_smoke()

        def fake_request(_base_url, path, token=None):
            if path == "/ping":
                return 200, b'{"result":"pong"}', {}
            if path == "/version" and token is None:
                return 401, b'{"status":"error"}', {}
            if path == "/version":
                return 401, b'{"status":"error"}', {}
            raise AssertionError(path)

        with mock.patch.object(module, "_request", side_effect=fake_request):
            result = module.run_from_values("http://127.0.0.1:18080", "wrong-token")

        self.assertFalse(result.ok)
        self.assertEqual(result.message, "Authenticated /version failed")

    def test_success_requires_screenshot_png_signature(self) -> None:
        module = load_portal_http_smoke()

        def fake_request(_base_url, path, token=None):
            if path == "/ping":
                return 200, b'{"result":"pong"}', {}
            if path == "/version" and token is None:
                return 401, b'{"status":"error"}', {}
            if path == "/version":
                return 200, b'{"status":"success","result":"0.7.13"}', {}
            if path == "/state":
                return 200, b'{"status":"success","result":"phone_state"}', {}
            if path == "/screenshot":
                return 200, b'{"status":"success","result":"iVBORw0KGgo="}', {"content-type": "application/json"}
            raise AssertionError(path)

        with mock.patch.object(module, "_request", side_effect=fake_request):
            result = module.run_from_values("http://127.0.0.1:18080", "token")

        self.assertTrue(result.ok)
        self.assertEqual(result.mode, "portal-http-only")
        self.assertTrue(result.checks["screenshot_png_signature"])


if __name__ == "__main__":
    unittest.main()
