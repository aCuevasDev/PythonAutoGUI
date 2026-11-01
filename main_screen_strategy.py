import pyautogui
from pyscreeze import Box
from button import Button


class MainScreenStrategy:
    def __init__(self, button):
        self.button = button

    def find_button(self) -> Box | None:
        try:
            return pyautogui.locateOnScreen(self.button.image_path, confidence=self.button.confidence)
        except pyautogui.ImageNotFoundException:
            return None