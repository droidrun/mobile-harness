#!/usr/bin/env python3
"""Smoke-test Portal HTTP-only access from environment variables."""

from __future__ import annotations

import base64
import binascii
import json
import os
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass, asdict


URL_ENV = "MOBILE_HARNESS_PORTAL_URL"
TOKEN_ENV = "MOBILE_HARNESS_PORTAL_TOKEN"
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


@dataclass
class Result:
    ok: bool
    mode: str
    message: str
    checks: dict[str, object]


def _request(base_url: str, path: str, token: str | None = None) -> tuple[int, bytes, dict[str, str]]:
    url = base_url.rstrip("/") + path
    request = urllib.request.Request(url)
    if token:
        request.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            headers = {k.lower(): v for k, v in response.headers.items()}
            return response.status, response.read(), headers
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read(), {k.lower(): v for k, v in exc.headers.items()}


def _has_png_payload(body: bytes) -> bool:
    if body.startswith(PNG_SIGNATURE):
        return True
    try:
        payload = json.loads(body.decode("utf-8"))
        result = payload.get("result")
        if not isinstance(result, str):
            return False
        decoded = base64.b64decode(result, validate=True)
        return decoded.startswith(PNG_SIGNATURE)
    except (UnicodeDecodeError, json.JSONDecodeError, binascii.Error):
        return False


def run_from_values(base_url: str | None, token: str | None) -> Result:
    if not base_url or not token:
        return Result(
            ok=False,
            mode="blocked",
            message=(
                f"Portal HTTP-only requires {URL_ENV} and {TOKEN_ENV}; ask the user "
                "for the Portal base URL and bearer token."
            ),
            checks={"url_present": bool(base_url), "token_present": bool(token)},
        )

    checks: dict[str, object] = {"url_present": True, "token_present": True}

    ping_code, ping_body, _ = _request(base_url, "/ping")
    checks["ping_status"] = ping_code
    checks["ping_has_pong"] = b"pong" in ping_body
    if ping_code != 200 or b"pong" not in ping_body:
        return Result(False, "portal-http-only", "Portal /ping failed", checks)

    unauth_code, _, _ = _request(base_url, "/version")
    checks["unauth_version_status"] = unauth_code
    if unauth_code != 401:
        return Result(False, "portal-http-only", "Unauthenticated /version must return 401", checks)

    version_code, version_body, _ = _request(base_url, "/version", token)
    checks["auth_version_status"] = version_code
    checks["auth_version_has_success"] = b'"status":"success"' in version_body
    if version_code != 200 or b'"status":"success"' not in version_body:
        return Result(False, "portal-http-only", "Authenticated /version failed", checks)

    state_code, state_body, _ = _request(base_url, "/state", token)
    checks["state_status"] = state_code
    checks["state_has_phone_state"] = b"phone_state" in state_body or b"phoneState" in state_body
    if state_code != 200 or not checks["state_has_phone_state"]:
        return Result(False, "portal-http-only", "Authenticated /state failed", checks)

    screenshot_code, screenshot_body, screenshot_headers = _request(base_url, "/screenshot", token)
    checks["screenshot_status"] = screenshot_code
    checks["screenshot_content_type"] = screenshot_headers.get("content-type", "")
    checks["screenshot_png_signature"] = _has_png_payload(screenshot_body)
    if screenshot_code != 200 or not checks["screenshot_png_signature"]:
        return Result(False, "portal-http-only", "Authenticated /screenshot failed", checks)

    return Result(True, "portal-http-only", "Portal HTTP-only access verified", checks)


def main() -> int:
    result = run_from_values(os.environ.get(URL_ENV), os.environ.get(TOKEN_ENV))
    print(json.dumps(asdict(result), sort_keys=True))
    return 0 if result.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
