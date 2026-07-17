"""Desktop input and screen capture helper for the replay OCR truth loop.

Coordinates are physical pixels on the virtual desktop (handoff.md basis:
primary display 3072x1920 at 150% scaling). The process declares DPI awareness
before any user32 geometry call so SetCursorPos, GetSystemMetrics, and PIL
ImageGrab all agree on physical pixels; without this, Windows virtualizes
coordinates to the 2048x1280 logical space and every handoff coordinate lands
in the wrong place.

CLI runs a sequence of steps in one process invocation, e.g.:

    python -m vg.tools.desktop_auto info "click:2730,1668" sleep:2 "shot:C:/tmp/menu.png"
"""

from __future__ import annotations

import argparse
import ctypes
import json
import time
from ctypes import wintypes
from pathlib import Path
from typing import Dict, List, Tuple

MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_RIGHTDOWN = 0x0008
MOUSEEVENTF_RIGHTUP = 0x0010
KEYEVENTF_KEYUP = 0x0002
INPUT_MOUSE = 0
INPUT_KEYBOARD = 1

VK_MAP = {
    "enter": 0x0D,
    "esc": 0x1B,
    "tab": 0x09,
    "space": 0x20,
}

ULONG_PTR = wintypes.WPARAM


class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", wintypes.LONG),
        ("dy", wintypes.LONG),
        ("mouseData", wintypes.DWORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ULONG_PTR),
    ]


class KEYBDINPUT(ctypes.Structure):
    _fields_ = [
        ("wVk", wintypes.WORD),
        ("wScan", wintypes.WORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ULONG_PTR),
    ]


class _INPUTUNION(ctypes.Union):
    _fields_ = [("mi", MOUSEINPUT), ("ki", KEYBDINPUT)]


class INPUT(ctypes.Structure):
    _fields_ = [("type", wintypes.DWORD), ("union", _INPUTUNION)]


def _user32() -> ctypes.WinDLL:
    return ctypes.WinDLL("user32", use_last_error=True)


def ensure_dpi_aware() -> None:
    try:
        ctypes.WinDLL("shcore").SetProcessDpiAwareness(2)
    except Exception:
        _user32().SetProcessDPIAware()


def _send_mouse_flags(flags: int) -> None:
    inp = INPUT(type=INPUT_MOUSE)
    inp.union.mi = MOUSEINPUT(0, 0, 0, flags, 0, 0)
    sent = _user32().SendInput(1, ctypes.byref(inp), ctypes.sizeof(INPUT))
    if sent != 1:
        raise OSError(f"SendInput failed: {ctypes.get_last_error()}")


def move_cursor(x: int, y: int) -> None:
    if not _user32().SetCursorPos(int(x), int(y)):
        raise OSError(f"SetCursorPos failed: {ctypes.get_last_error()}")


def click(x: int, y: int, button: str = "left", presses: int = 1) -> None:
    down, up = {
        "left": (MOUSEEVENTF_LEFTDOWN, MOUSEEVENTF_LEFTUP),
        "right": (MOUSEEVENTF_RIGHTDOWN, MOUSEEVENTF_RIGHTUP),
    }[button]
    move_cursor(x, y)
    time.sleep(0.08)
    for i in range(presses):
        _send_mouse_flags(down)
        time.sleep(0.04)
        _send_mouse_flags(up)
        if i + 1 < presses:
            time.sleep(0.12)


def press_key(name: str) -> None:
    vk = VK_MAP[name]
    inp = INPUT(type=INPUT_KEYBOARD)
    inp.union.ki = KEYBDINPUT(vk, 0, 0, 0, 0)
    _user32().SendInput(1, ctypes.byref(inp), ctypes.sizeof(INPUT))
    time.sleep(0.04)
    inp.union.ki = KEYBDINPUT(vk, 0, KEYEVENTF_KEYUP, 0, 0)
    _user32().SendInput(1, ctypes.byref(inp), ctypes.sizeof(INPUT))


def primary_screen_size() -> Tuple[int, int]:
    u = _user32()
    return int(u.GetSystemMetrics(0)), int(u.GetSystemMetrics(1))


def capture(path: str, bbox: Tuple[int, int, int, int] | None = None) -> Dict[str, object]:
    from PIL import ImageGrab

    if bbox is None:
        width, height = primary_screen_size()
        bbox = (0, 0, width, height)
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    image = ImageGrab.grab(bbox=bbox, all_screens=True)
    image.save(output)
    return {"path": str(output.resolve()), "bbox": list(bbox), "size_bytes": output.stat().st_size}


def parse_step(step: str) -> Tuple[str, List[str]]:
    op, _, arg = step.partition(":")
    op = op.strip().lower()
    args = [part.strip() for part in arg.split(",")] if arg else []
    if op in {"click", "dblclick", "rclick", "move"}:
        if len(args) != 2 or not all(part.lstrip("-").isdigit() for part in args):
            raise ValueError(f"{op} requires X,Y integers: {step!r}")
    elif op == "sleep":
        if len(args) != 1:
            raise ValueError(f"sleep requires seconds: {step!r}")
        float(args[0])
    elif op == "shot":
        if not arg:
            raise ValueError(f"shot requires a path: {step!r}")
        args = [arg.strip()]
    elif op == "key":
        if len(args) != 1 or args[0] not in VK_MAP:
            raise ValueError(f"key requires one of {sorted(VK_MAP)}: {step!r}")
    elif op != "info":
        raise ValueError(f"Unknown step: {step!r}")
    return op, args


def run_step(op: str, args: List[str]) -> Dict[str, object]:
    if op == "click":
        click(int(args[0]), int(args[1]))
    elif op == "dblclick":
        click(int(args[0]), int(args[1]), presses=2)
    elif op == "rclick":
        click(int(args[0]), int(args[1]), button="right")
    elif op == "move":
        move_cursor(int(args[0]), int(args[1]))
    elif op == "sleep":
        time.sleep(float(args[0]))
    elif op == "key":
        press_key(args[0])
    elif op == "shot":
        return {"step": "shot", **capture(args[0])}
    elif op == "info":
        width, height = primary_screen_size()
        point = wintypes.POINT()
        _user32().GetCursorPos(ctypes.byref(point))
        return {
            "step": "info",
            "primary_size": [width, height],
            "cursor": [int(point.x), int(point.y)],
        }
    return {"step": op, "args": args}


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a sequence of desktop input/capture steps.")
    parser.add_argument(
        "steps",
        nargs="+",
        help="Steps: click:X,Y dblclick:X,Y rclick:X,Y move:X,Y sleep:SEC shot:PATH key:NAME info",
    )
    args = parser.parse_args()

    parsed = [parse_step(step) for step in args.steps]
    ensure_dpi_aware()
    results = [run_step(op, step_args) for op, step_args in parsed]
    print(json.dumps(results, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
