#!/usr/bin/env python3
"""Smoke-test ADB and public Portal HTTP assumptions against an emulator."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass


PORTAL_PACKAGE = "com.mobilerun.portal"
PORTAL_AUTH_URI = f"content://{PORTAL_PACKAGE}/auth_token"
PORTAL_VERSION_URI = f"content://{PORTAL_PACKAGE}/version"
PORTAL_SOCKET_URI = f"content://{PORTAL_PACKAGE}/toggle_socket_server"


@dataclass
class CommandResult:
    code: int
    stdout: str
    stderr: str


def run(cmd: list[str], timeout: int = 20) -> CommandResult:
    proc = subprocess.run(
        cmd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=timeout,
        check=False,
    )
    return CommandResult(proc.returncode, proc.stdout.strip(), proc.stderr.strip())


def parse_content_result(raw: str) -> str | None:
    match = re.search(r"result=(\{.*\})", raw)
    if not match:
        return None
    data = json.loads(match.group(1))
    if data.get("status") != "success":
        return None
    result = data.get("result")
    return result if isinstance(result, str) else json.dumps(result)


def http_get(url: str, token: str | None = None) -> tuple[int, str]:
    request = urllib.request.Request(url)
    if token:
        request.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            return response.status, response.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode("utf-8", errors="replace")


def choose_serial(explicit: str | None) -> str:
    if explicit:
        return explicit
    result = run(["adb", "devices", "-l"])
    if result.code != 0:
        raise RuntimeError(f"adb devices failed: {result.stderr}")
    for line in result.stdout.splitlines()[1:]:
        parts = line.split()
        if len(parts) >= 2 and parts[1] == "device":
            return parts[0]
    raise RuntimeError("no online adb device found")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--serial", help="ADB serial to test")
    parser.add_argument("--local-port", type=int, default=18080)
    args = parser.parse_args()

    serial = choose_serial(args.serial)
    print(f"serial: {serial}")

    packages = run(["adb", "-s", serial, "shell", "pm", "list", "packages", PORTAL_PACKAGE])
    if packages.code != 0:
        raise RuntimeError(f"package listing failed: {packages.stderr or packages.stdout}")
    if PORTAL_PACKAGE not in packages.stdout:
        print("mode: ADB-only (Portal package not installed)")
        return 0

    version_raw = run(["adb", "-s", serial, "shell", "content", "query", "--uri", PORTAL_VERSION_URI])
    if version_raw.code != 0:
        print("mode: ADB-only (Portal provider unavailable)")
        print(version_raw.stderr or version_raw.stdout)
        return 0
    version = parse_content_result(version_raw.stdout)
    if not version:
        raise RuntimeError(f"could not parse Portal version: {version_raw.stdout}")
    print(f"portal_version: {version}")

    token_raw = run(["adb", "-s", serial, "shell", "content", "query", "--uri", PORTAL_AUTH_URI])
    token = parse_content_result(token_raw.stdout)
    if not token:
        raise RuntimeError("could not fetch Portal auth token through ADB")
    print("portal_token: present")

    enable = run(
        [
            "adb",
            "-s",
            serial,
            "shell",
            "content",
            "insert",
            "--uri",
            PORTAL_SOCKET_URI,
            "--bind",
            "enabled:b:true",
            "--bind",
            "port:i:8080",
        ]
    )
    if enable.code != 0:
        raise RuntimeError(f"could not enable Portal HTTP: {enable.stderr or enable.stdout}")

    local = str(args.local_port)
    forward = run(["adb", "-s", serial, "forward", f"tcp:{local}", "tcp:8080"])
    if forward.code != 0:
        raise RuntimeError(f"adb forward failed: {forward.stderr or forward.stdout}")

    base_url = f"http://127.0.0.1:{local}"
    ping_code, ping_body = http_get(f"{base_url}/ping")
    if ping_code != 200 or "pong" not in ping_body:
        raise RuntimeError(f"/ping failed: {ping_code} {ping_body}")

    unauth_code, _ = http_get(f"{base_url}/version")
    if unauth_code != 401:
        raise RuntimeError(f"/version without token should be 401, got {unauth_code}")

    auth_code, auth_body = http_get(f"{base_url}/version", token)
    if auth_code != 200 or version not in auth_body:
        raise RuntimeError(f"/version with token failed: {auth_code} {auth_body}")

    state_code, state_body = http_get(f"{base_url}/state", token)
    if state_code != 200:
        raise RuntimeError(f"/state with token failed: {state_code} {state_body}")

    print("mode: Hybrid")
    print("portal_http: ok")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
