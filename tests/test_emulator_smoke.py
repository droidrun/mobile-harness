from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]


def load_emulator_smoke():
    spec = importlib.util.spec_from_file_location("emulator_smoke", ROOT / "scripts/emulator_smoke.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules["emulator_smoke"] = module
    spec.loader.exec_module(module)
    return module


class EmulatorSmokeTest(unittest.TestCase):
    def test_parse_content_result(self) -> None:
        module = load_emulator_smoke()
        raw = 'Row: 0 result={"status":"success","result":"0.7.13"}'
        self.assertEqual(module.parse_content_result(raw), "0.7.13")

    def test_adb_command_failure_fails_loudly(self) -> None:
        module = load_emulator_smoke()

        def fake_run(cmd, timeout=20):
            if cmd[:5] == ["adb", "-s", "emu", "shell", "pm"]:
                return module.CommandResult(1, "", "adb failed")
            raise AssertionError(cmd)

        with mock.patch.object(module, "choose_serial", return_value="emu"), \
             mock.patch.object(module, "run", side_effect=fake_run), \
             mock.patch("sys.argv", ["emulator_smoke.py", "--serial", "emu"]):
            with self.assertRaisesRegex(RuntimeError, "package listing failed"):
                module.main()

    def test_missing_portal_package_returns_adb_only(self) -> None:
        module = load_emulator_smoke()

        def fake_run(cmd, timeout=20):
            if cmd[:5] == ["adb", "-s", "emu", "shell", "pm"]:
                return module.CommandResult(0, "", "")
            raise AssertionError(cmd)

        with mock.patch.object(module, "choose_serial", return_value="emu"), \
             mock.patch.object(module, "run", side_effect=fake_run), \
             mock.patch("sys.argv", ["emulator_smoke.py", "--serial", "emu"]):
            self.assertEqual(module.main(), 0)

    def test_provider_unavailable_returns_adb_only(self) -> None:
        module = load_emulator_smoke()

        def fake_run(cmd, timeout=20):
            if cmd[:5] == ["adb", "-s", "emu", "shell", "pm"]:
                return module.CommandResult(0, "package:com.mobilerun.portal", "")
            if "content://com.mobilerun.portal/version" in cmd:
                return module.CommandResult(1, "", "provider unavailable")
            raise AssertionError(cmd)

        with mock.patch.object(module, "choose_serial", return_value="emu"), \
             mock.patch.object(module, "run", side_effect=fake_run), \
             mock.patch("sys.argv", ["emulator_smoke.py", "--serial", "emu"]):
            self.assertEqual(module.main(), 0)

    def test_missing_token_fails(self) -> None:
        module = load_emulator_smoke()

        def fake_run(cmd, timeout=20):
            if cmd[:5] == ["adb", "-s", "emu", "shell", "pm"]:
                return module.CommandResult(0, "package:com.mobilerun.portal", "")
            if "content://com.mobilerun.portal/version" in cmd:
                return module.CommandResult(0, 'Row: 0 result={"status":"success","result":"0.7.13"}', "")
            if "content://com.mobilerun.portal/auth_token" in cmd:
                return module.CommandResult(0, 'Row: 0 result={"status":"error","error":"no token"}', "")
            raise AssertionError(cmd)

        with mock.patch.object(module, "choose_serial", return_value="emu"), \
             mock.patch.object(module, "run", side_effect=fake_run), \
             mock.patch("sys.argv", ["emulator_smoke.py", "--serial", "emu"]):
            with self.assertRaisesRegex(RuntimeError, "could not fetch Portal auth token"):
                module.main()

    def test_hybrid_honors_custom_local_port_and_http_auth(self) -> None:
        module = load_emulator_smoke()
        seen_commands: list[list[str]] = []
        seen_urls: list[str] = []

        def fake_run(cmd, timeout=20):
            seen_commands.append(cmd)
            if cmd[:5] == ["adb", "-s", "emu", "shell", "pm"]:
                return module.CommandResult(0, "package:com.mobilerun.portal", "")
            if "content://com.mobilerun.portal/version" in cmd:
                return module.CommandResult(0, 'Row: 0 result={"status":"success","result":"0.7.13"}', "")
            if "content://com.mobilerun.portal/auth_token" in cmd:
                return module.CommandResult(0, 'Row: 0 result={"status":"success","result":"secret"}', "")
            if "content://com.mobilerun.portal/toggle_socket_server" in cmd:
                return module.CommandResult(0, "", "")
            if cmd[:4] == ["adb", "-s", "emu", "forward"]:
                return module.CommandResult(0, "19090", "")
            raise AssertionError(cmd)

        def fake_http_get(url, token=None):
            seen_urls.append(f"{url}|{token}")
            if url.endswith("/ping"):
                return 200, '{"status":"success","result":"pong"}'
            if url.endswith("/version") and token is None:
                return 401, '{"status":"error"}'
            if url.endswith("/version") and token == "secret":
                return 200, '{"status":"success","result":"0.7.13"}'
            if url.endswith("/state") and token == "secret":
                return 200, '{"phone_state":{}}'
            raise AssertionError((url, token))

        with mock.patch.object(module, "choose_serial", return_value="emu"), \
             mock.patch.object(module, "run", side_effect=fake_run), \
             mock.patch.object(module, "http_get", side_effect=fake_http_get), \
             mock.patch("sys.argv", ["emulator_smoke.py", "--serial", "emu", "--local-port", "19090"]):
            self.assertEqual(module.main(), 0)

        self.assertIn(["adb", "-s", "emu", "forward", "tcp:19090", "tcp:8080"], seen_commands)
        self.assertTrue(any("http://127.0.0.1:19090/version|secret" == item for item in seen_urls))


if __name__ == "__main__":
    unittest.main()
