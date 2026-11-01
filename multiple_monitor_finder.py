import mss
import pyautogui
from PIL import Image
from pyscreeze import Box

from button import Button
from find_button_strategy import FindButtonStrategy


class MultipleMonitorFinder(FindButtonStrategy):
    def __init__(self, monitor: int = 2, dev: bool = False):
        # mss numbering: 0 = all screens combined, 1 = primary, 2+ = the others
        self._monitor = monitor
        self.dev = dev

    def find_button(self, button: Button) -> Box | None:
        with mss.mss() as sct:
            if self._monitor >= len(sct.monitors):
                raise ValueError(
                    f"Monitor {self._monitor} not found, available: 1..{len(sct.monitors) - 1}"
                )
            mon = sct.monitors[self._monitor]  # dict: left, top, width, height
            shot = sct.grab(mon)
            screen = Image.frombytes("RGB", shot.size, shot.bgra, "raw", "BGRX")

        if self.dev:
            screen.save("debug_monitor.png")

        try:
            box = pyautogui.locate(
                button.image_path, screen, confidence=button.confidence
            )
        except pyautogui.ImageNotFoundException:
            return None

        if box is None:
            return None

        # Match is relative to the monitor image: shift to desktop coordinates
        return Box(
            box.left + mon["left"],
            box.top + mon["top"],
            box.width,
            box.height,
        )