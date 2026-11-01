import mss
import pygetwindow as gw


def find_monitor_of_window(title_part: str) -> int | None:
    windows = gw.getWindowsWithTitle(title_part)
    if not windows:
        return None

    win = windows[0]
    if win.isMinimized:
        return None  # minimized windows report fake coordinates

    cx = win.left + win.width // 2
    cy = win.top + win.height // 2

    with mss.mss() as sct:
        for i, mon in enumerate(sct.monitors[1:], start=1):
            if (mon["left"] <= cx < mon["left"] + mon["width"]
                    and mon["top"] <= cy < mon["top"] + mon["height"]):
                return i
    return None


