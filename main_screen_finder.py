import pyautogui

from button import Button
from find_button_strategy import FindButtonStrategy
from pyscreeze import Box


class MainScreenFinder(FindButtonStrategy):
    def find_button(self, button: Button) -> Box | None:
        try:
            return pyautogui.locateOnScreen(
                button.image_path, confidence=button.confidence
            )
        except pyautogui.ImageNotFoundException:
            return None
