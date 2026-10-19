#!/usr/bin/env python3
"""Headless smoke test for the Jupiter TUI installer (demo mode, no hardware touched).

Usage: JUPITER_DEMO=1 python3 tests/tui_smoke.py [screenshot_dir]
Run it from the repository root. It drives the wizard through every screen,
checks validation, runs the fake installer and writes SVG screenshots.
"""
from __future__ import annotations

import asyncio
import importlib.machinery
import importlib.util
import os
import sys
from pathlib import Path

os.environ["JUPITER_DEMO"] = "1"
os.environ.setdefault("JUPITER_DEMO_ONLINE", "0")

ROOT = Path(__file__).resolve().parent.parent
SETUP = ROOT / "installer" / "jupiter-setup"
SHOTS = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / ".build" / "screenshots"
SHOTS.mkdir(parents=True, exist_ok=True)

loader = importlib.machinery.SourceFileLoader("jupiter_setup", str(SETUP))
spec = importlib.util.spec_from_loader("jupiter_setup", loader)
mod = importlib.util.module_from_spec(spec)
sys.modules["jupiter_setup"] = mod  # dataclasses needs the module registered
loader.exec_module(mod)

from textual.widgets import Button, Input, RadioSet, Select  # noqa: E402


def shot(app, name: str) -> None:
    app.save_screenshot(filename=f"{name}.svg", path=str(SHOTS))


async def click(pilot, selector: str) -> None:
    await pilot.click(selector)
    await pilot.pause(0.3)


async def main() -> None:
    failures: list[str] = []
    app = mod.JupiterSetup()
    async with app.run_test(size=(110, 46)) as pilot:
        await pilot.pause(0.5)
        screen = app.screen
        assert type(screen).__name__ == "WelcomeScreen", type(screen).__name__
        shot(app, "01-welcome")

        # Offline in demo mode -> network screen is shown (ethernet/online would skip it).
        await click(pilot, "#begin")
        await pilot.pause(0.5)
        if type(app.screen).__name__ != "NetworkScreen":
            failures.append("expected NetworkScreen when offline")
        shot(app, "02-network")

        # Connect with a password-protected network.
        app.screen.query_one("#ssid", Select).value = "HomeNet-5G"
        app.screen.query_one("#wifi-pass", Input).value = "secret123"
        await click(pilot, "#connect")
        await pilot.pause(0.8)
        shot(app, "03-network-connected")
        await click(pilot, "#continue")

        # Disk screen
        await pilot.pause(0.3)
        if type(app.screen).__name__ != "DiskScreen":
            failures.append("expected DiskScreen after network")
        shot(app, "04-disk")
        await click(pilot, "#continue")

        # User screen: validation first.
        await pilot.pause(0.3)
        if type(app.screen).__name__ != "UserScreen":
            failures.append("expected UserScreen")
        await click(pilot, "#continue")
        error = str(app.screen.query_one("#error").render())
        if "Computer name" in error or "Username" not in error:
            # Empty username must be rejected with a username error.
            failures.append(f"empty username accepted/unexpected error: {error!r}")
        app.screen.query_one("#username", Input).value = "ada"
        app.screen.query_one("#password", Input).value = "pass1234"
        app.screen.query_one("#password2", Input).value = "different"
        await click(pilot, "#continue")
        if "do not match" not in str(app.screen.query_one("#error").render()):
            failures.append("password mismatch not detected")
        app.screen.query_one("#password2", Input).value = "pass1234"
        app.screen.query_one("#fullname", Input).value = "Ada Lovelace"
        shot(app, "05-user")
        await click(pilot, "#continue")

        # Driver screen: demo default is Mesa; switch to NVIDIA.
        await pilot.pause(0.3)
        if type(app.screen).__name__ != "DriverScreen":
            failures.append("expected DriverScreen")
        shot(app, "06-driver")
        app.screen.query_one("#drv-nvidia").value = True
        await click(pilot, "#continue")

        # Review: install disabled until ERASE typed.
        await pilot.pause(0.3)
        if type(app.screen).__name__ != "ReviewScreen":
            failures.append("expected ReviewScreen")
        if not app.screen.query_one("#install", Button).disabled is True:
            failures.append("install button should be disabled before typing ERASE")
        app.screen.query_one("#confirm", Input).value = "ERASE"
        await pilot.pause(0.2)
        shot(app, "07-review")
        await click(pilot, "#install")

        # Install screen runs the (demo) installer and enables Reboot.
        for _ in range(60):
            await pilot.pause(0.2)
            if not app.screen.query_one("#reboot", Button).disabled:
                break
        if app.screen.query_one("#reboot", Button).disabled:
            failures.append("install did not finish in demo mode")
        shot(app, "08-install-done")

        answers = app.answers
        if answers.driver != "nvidia" or answers.username != "ada" or answers.disk != "/dev/nvme0n1":
            failures.append(f"unexpected answers: {answers}")

    # Answers file must be root-only and sourceable.
    tmp = Path(os.environ.get("TMPDIR", "/tmp")) / "jupiter-answers-test.env"
    answers.write(tmp)
    mode = oct(tmp.stat().st_mode & 0o777)
    if mode != "0o600":
        failures.append(f"answers file mode {mode}, expected 0o600")
    tmp.unlink(missing_ok=True)

    if failures:
        print("FAILED:")
        for item in failures:
            print(" -", item)
        raise SystemExit(1)
    print(f"TUI smoke test passed. Screenshots in {SHOTS}")


if __name__ == "__main__":
    asyncio.run(main())
