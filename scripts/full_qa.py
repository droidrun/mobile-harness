#!/usr/bin/env python3
"""Run the full mobile-harness-android QA matrix."""

from __future__ import annotations

import argparse
import base64
import http.client
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass, field
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT.parent
PORTAL_PACKAGE = "com.mobilerun.portal"
PORTAL_APK = WORK / "mobilerun-portal/app/build/outputs/apk/debug/com.mobilerun.portal-0.7.13-debug.apk"
REPORT_PATH = ROOT / "tmp/full-qa-report.json"


@dataclass
class Step:
    name: str
    ok: bool
    detail: str = ""
    data: dict[str, object] = field(default_factory=dict)


@dataclass
class Command:
    code: int
    stdout: str
    stderr: str


class QAError(RuntimeError):
    pass


class QA:
    def __init__(self, serial: str, local_port: int, codex: str, run_agent_eval: bool) -> None:
        self.serial = serial
        self.local_port = local_port
        self.codex = codex
        self.run_agent_eval = run_agent_eval
        self.steps: list[Step] = []
        self.baseline: dict[str, object] = {}
        self.portal_token: str | None = None
        self.portal_url = f"http://127.0.0.1:{local_port}"

    def record(self, name: str, ok: bool, detail: str = "", **data: object) -> None:
        self.steps.append(Step(name=name, ok=ok, detail=detail, data=data))
        status = "PASS" if ok else "FAIL"
        print(f"{status}: {name}{(': ' + detail) if detail else ''}")

    def command(self, args: list[str], *, cwd: Path = ROOT, timeout: int = 60, env: dict[str, str] | None = None) -> Command:
        proc = subprocess.run(
            args,
            cwd=str(cwd),
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
            check=False,
        )
        return Command(proc.returncode, proc.stdout.strip(), proc.stderr.strip())

    def adb(self, *args: str, timeout: int = 60) -> Command:
        return self.command(["adb", "-s", self.serial, *args], timeout=timeout)

    def adb_shell(self, *args: str, timeout: int = 60) -> Command:
        return self.adb("shell", *args, timeout=timeout)

    def http(self, path: str, token: str | None = None, method: str = "GET", body: bytes | None = None) -> tuple[int, bytes, dict[str, str]]:
        request = urllib.request.Request(self.portal_url.rstrip("/") + path, data=body, method=method)
        if token:
            request.add_header("Authorization", f"Bearer {token}")
        if body is not None:
            request.add_header("Content-Type", "application/json")
        for attempt in range(5):
            try:
                with urllib.request.urlopen(request, timeout=10) as response:
                    return response.status, response.read(), {k.lower(): v for k, v in response.headers.items()}
            except urllib.error.HTTPError as exc:
                return exc.code, exc.read(), {k.lower(): v for k, v in exc.headers.items()}
            except (urllib.error.URLError, ConnectionResetError, http.client.RemoteDisconnected) as exc:
                if attempt == 4:
                    raise QAError(f"HTTP request failed for {path}: {exc}") from exc
                time.sleep(0.5 * (attempt + 1))
        raise QAError(f"HTTP request failed for {path}")

    def require(self, condition: bool, message: str) -> None:
        if not condition:
            raise QAError(message)

    def parse_content_result(self, raw: str) -> str:
        match = re.search(r"result=(\{.*\})", raw)
        self.require(match is not None, f"unparseable content provider output: {raw}")
        data = json.loads(match.group(1))
        self.require(data.get("status") == "success", f"content provider returned error: {raw}")
        result = data.get("result")
        return result if isinstance(result, str) else json.dumps(result)

    def has_png_payload(self, body: bytes) -> bool:
        if body.startswith(b"\x89PNG\r\n\x1a\n"):
            return True
        try:
            payload = json.loads(body.decode("utf-8"))
            result = payload.get("result")
            if not isinstance(result, str):
                return False
            return base64.b64decode(result, validate=True).startswith(b"\x89PNG\r\n\x1a\n")
        except Exception:
            return False

    def run_all(self) -> None:
        REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
        self.record_baseline()
        self.static_checks()
        self.unit_tests()
        if self.run_agent_eval:
            self.agent_eval()
        self.live_adb_only()
        self.install_and_prepare_portal()
        self.live_hybrid()
        self.live_portal_http_only()
        self.blocked_mode()
        self.restore_portal_state()
        self.final_git_check()

    def record_baseline(self) -> None:
        devices = self.command(["adb", "devices", "-l"])
        packages = self.adb_shell("pm", "list", "packages", PORTAL_PACKAGE)
        a11y = self.adb_shell("settings", "get", "secure", "enabled_accessibility_services")
        imes = self.adb_shell("ime", "list", "-s")
        self.baseline = {
            "devices": devices.stdout,
            "portal_packages": packages.stdout,
            "accessibility_services": a11y.stdout,
            "imes": imes.stdout,
        }
        self.require(devices.code == 0 and self.serial in devices.stdout, f"{self.serial} is not online")
        self.record("baseline", True, serial=self.serial, portal_installed=PORTAL_PACKAGE in packages.stdout)

    def static_checks(self) -> None:
        validate = self.command(["python3", "scripts/validate_docs.py"])
        self.require(validate.code == 0, validate.stderr or validate.stdout)

        ignored_credential = self.command(["git", "check-ignore", "credentials/com.example.app.md"])
        ignored_memory = self.command(["git", "check-ignore", "memory/index.md"])
        self.require(ignored_credential.code == 0, "credentials/<package>.md must be ignored")
        self.require(ignored_memory.code == 0, "memory/index.md must be ignored")

        forbidden_pattern = "|".join(
            [
                r"com\.droidrun\.portal",
                "w" + "s://",
                "w" + "ss://",
                r"MOBILE_HARNESS_PORTAL_TOKEN=[A-Za-z0-9_-]+",
            ]
        )
        forbidden = self.command(["rg", "-n", forbidden_pattern, "."])
        self.require(forbidden.code != 0, forbidden.stdout)

        tracked = self.command(["git", "ls-files"])
        tracked_files = set(tracked.stdout.splitlines())
        self.require("credentials/TEMPLATE.md" in tracked_files, "credentials template must be tracked")
        self.require("memory/README.md" in tracked_files, "memory README must be tracked")

        self.record("static checks", True)

    def unit_tests(self) -> None:
        result = self.command(["python3", "-m", "unittest", "discover", "-s", "tests", "-v"], timeout=120)
        self.require(result.code == 0, result.stdout + "\n" + result.stderr)
        self.record("unit tests", True)

    def agent_eval(self) -> None:
        result = self.command(
            [
                "python3",
                "tests/agent_eval/run_agent_eval.py",
                "--codex",
                self.codex,
                "--parallel",
                "4",
                "--timeout",
                "180",
            ],
            timeout=2400,
        )
        self.require(result.code == 0, result.stdout + "\n" + result.stderr)
        self.record("agent eval", True)

    def live_adb_only(self) -> None:
        uninstall = self.command(["adb", "-s", self.serial, "uninstall", PORTAL_PACKAGE], timeout=120)
        if uninstall.code != 0 and "Unknown package" not in (uninstall.stdout + uninstall.stderr):
            raise QAError(uninstall.stdout + uninstall.stderr)

        time.sleep(1)
        packages = self.adb_shell("pm", "list", "packages", PORTAL_PACKAGE)
        self.require(PORTAL_PACKAGE not in packages.stdout, "Portal package still present after uninstall")

        screenshot = self.adb_shell("screencap", "-p", "/sdcard/mobile-harness-adb-only.png", timeout=30)
        self.require(screenshot.code == 0, "ADB screencap failed")
        screenshot_ls = self.adb_shell("ls", "-l", "/sdcard/mobile-harness-adb-only.png", timeout=30)
        self.require(screenshot_ls.code == 0 and "mobile-harness-adb-only.png" in screenshot_ls.stdout, "ADB screencap output missing")
        self.adb_shell("rm", "/sdcard/mobile-harness-adb-only.png", timeout=30)

        ui = self.command(["adb", "-s", self.serial, "exec-out", "uiautomator", "dump", "/dev/tty"], timeout=30)
        self.require(ui.code == 0 and "hierarchy" in ui.stdout, "ADB uiautomator dump failed")

        for cmd in [
            ["adb", "-s", self.serial, "shell", "input", "tap", "540", "1200"],
            ["adb", "-s", self.serial, "shell", "input", "swipe", "540", "1700", "540", "900", "200"],
            ["adb", "-s", self.serial, "shell", "input", "keyevent", "4"],
            ["adb", "-s", self.serial, "shell", "pm", "list", "packages"],
        ]:
            result = self.command(cmd, timeout=30)
            self.require(result.code == 0, f"ADB command failed: {' '.join(cmd)} {result.stderr}")

        smoke = self.command(["python3", "scripts/emulator_smoke.py", "--serial", self.serial], timeout=120)
        self.require(smoke.code == 0 and "mode: ADB-only" in smoke.stdout, smoke.stdout + smoke.stderr)
        self.record("live ADB-only", True)

    def install_and_prepare_portal(self) -> None:
        self.require(PORTAL_APK.is_file(), f"Portal APK missing: {PORTAL_APK}")
        install = self.command(["adb", "-s", self.serial, "install", "-r", "-g", str(PORTAL_APK)], timeout=180)
        self.require(install.code == 0 and "Success" in install.stdout, install.stdout + install.stderr)

        self.adb_shell("settings", "put", "secure", "enabled_accessibility_services", "com.mobilerun.portal/.service.MobilerunAccessibilityService")
        self.adb_shell("settings", "put", "secure", "accessibility_enabled", "1")
        ime_enable = self.adb_shell("ime", "enable", "com.mobilerun.portal/.input.MobilerunKeyboardIME")
        self.require(ime_enable.code == 0 or "already" in ime_enable.stdout.lower(), ime_enable.stdout + ime_enable.stderr)

        start = self.adb_shell("am", "start", "-n", "com.mobilerun.portal/.ui.MainActivity")
        self.require(start.code == 0, start.stdout + start.stderr)
        time.sleep(2)

        token_result = self.adb_shell("content", "query", "--uri", "content://com.mobilerun.portal/auth_token")
        self.portal_token = self.parse_content_result(token_result.stdout)
        self.require(bool(self.portal_token), "Portal auth token missing")

        enable = self.adb_shell(
            "content",
            "insert",
            "--uri",
            "content://com.mobilerun.portal/toggle_socket_server",
            "--bind",
            "enabled:b:true",
            "--bind",
            "port:i:8080",
        )
        self.require(enable.code == 0, enable.stdout + enable.stderr)

        forward = self.command(["adb", "-s", self.serial, "forward", f"tcp:{self.local_port}", "tcp:8080"])
        self.require(forward.code == 0, forward.stdout + forward.stderr)
        self.record("Portal install and setup", True)

    def live_hybrid(self) -> None:
        self.require(self.portal_token is not None, "Portal token not initialized")
        smoke = self.command(["python3", "scripts/emulator_smoke.py", "--serial", self.serial, "--local-port", str(self.local_port)], timeout=180)
        self.require(smoke.code == 0 and "mode: Hybrid" in smoke.stdout and "portal_http: ok" in smoke.stdout, smoke.stdout + smoke.stderr)

        screenshot_code, screenshot_body, _ = self.http("/screenshot", self.portal_token)
        self.require(screenshot_code == 200 and self.has_png_payload(screenshot_body), "Portal screenshot failed")

        tap_body = json.dumps({"x": 540, "y": 1200}).encode()
        tap_code, tap_response, _ = self.http("/action/tap", self.portal_token, method="POST", body=tap_body)
        self.require(tap_code == 200 and b'"status":"success"' in tap_response, f"Portal tap failed: {tap_response!r}")

        app_body = json.dumps({"package": "com.android.settings"}).encode()
        app_code, app_response, _ = self.http("/action/app", self.portal_token, method="POST", body=app_body)
        self.require(app_code == 200 and b'"status":"success"' in app_response, f"Portal app launch failed: {app_response!r}")
        time.sleep(2)

        state_code, state_body, _ = self.http("/state", self.portal_token)
        self.require(state_code == 200 and b"com.android.settings" in state_body, "Settings did not become foreground")
        self.record("live Hybrid", True)

    def live_portal_http_only(self) -> None:
        self.require(self.portal_token is not None, "Portal token not initialized")
        env = os.environ.copy()
        env["MOBILE_HARNESS_PORTAL_URL"] = self.portal_url
        env["MOBILE_HARNESS_PORTAL_TOKEN"] = self.portal_token

        ok = self.command(["python3", "scripts/portal_http_smoke.py"], env=env, timeout=60)
        self.require(ok.code == 0, ok.stdout + ok.stderr)

        missing_env = os.environ.copy()
        missing_env.pop("MOBILE_HARNESS_PORTAL_URL", None)
        missing_env.pop("MOBILE_HARNESS_PORTAL_TOKEN", None)
        blocked = self.command(["python3", "scripts/portal_http_smoke.py"], env=missing_env, timeout=60)
        self.require(blocked.code == 1 and "Portal HTTP-only requires" in blocked.stdout, blocked.stdout + blocked.stderr)

        wrong_env = env.copy()
        wrong_env["MOBILE_HARNESS_PORTAL_TOKEN"] = "wrong-token"
        wrong = self.command(["python3", "scripts/portal_http_smoke.py"], env=wrong_env, timeout=60)
        self.require(wrong.code == 1 and "Authenticated /version failed" in wrong.stdout, wrong.stdout + wrong.stderr)

        self.record("live Portal HTTP-only", True)

    def blocked_mode(self) -> None:
        missing_env = os.environ.copy()
        missing_env.pop("MOBILE_HARNESS_PORTAL_URL", None)
        missing_env.pop("MOBILE_HARNESS_PORTAL_TOKEN", None)
        result = self.command(["python3", "scripts/portal_http_smoke.py"], env=missing_env, timeout=60)
        self.require(result.code == 1 and "ask the user for the Portal base URL and bearer token" in result.stdout, result.stdout + result.stderr)
        self.record("blocked mode", True)

    def restore_portal_state(self) -> None:
        start = self.adb_shell("am", "start", "-n", "com.mobilerun.portal/.ui.MainActivity")
        self.require(start.code == 0, start.stdout + start.stderr)
        self.adb_shell("settings", "put", "secure", "enabled_accessibility_services", "com.mobilerun.portal/.service.MobilerunAccessibilityService")
        self.adb_shell("settings", "put", "secure", "accessibility_enabled", "1")
        self.adb_shell("ime", "enable", "com.mobilerun.portal/.input.MobilerunKeyboardIME")
        enable = self.adb_shell(
            "content",
            "insert",
            "--uri",
            "content://com.mobilerun.portal/toggle_socket_server",
            "--bind",
            "enabled:b:true",
            "--bind",
            "port:i:8080",
        )
        self.require(enable.code == 0, enable.stdout + enable.stderr)
        self.record("restore Portal state", True)

    def final_git_check(self) -> None:
        result = self.command(["git", "status", "--short"])
        self.require(result.stdout.strip() == "", result.stdout)
        self.record("git clean", True)

    def write_report(self) -> None:
        report = {
            "ok": all(step.ok for step in self.steps),
            "serial": self.serial,
            "local_port": self.local_port,
            "baseline": self.baseline,
            "steps": [asdict(step) for step in self.steps],
        }
        REPORT_PATH.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
        print(f"report: {REPORT_PATH}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--serial", default="emulator-5554")
    parser.add_argument("--local-port", type=int, default=18080)
    parser.add_argument("--codex", default=shutil.which("codex") or "/opt/homebrew/bin/codex")
    parser.add_argument("--skip-agent-eval", action="store_true")
    args = parser.parse_args()

    qa = QA(args.serial, args.local_port, args.codex, run_agent_eval=not args.skip_agent_eval)
    try:
        qa.run_all()
        return 0
    except Exception as exc:
        qa.record("full QA", False, str(exc))
        return 1
    finally:
        qa.write_report()


if __name__ == "__main__":
    raise SystemExit(main())
