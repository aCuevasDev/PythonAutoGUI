import random
import time

import pyautogui
from pyscreeze import Box
from button import Button
from find_button_strategy import FindButtonStrategy
import find_button_strategy


class AutoGuiService:
    def __init__(self, find_button_strategy: FindButtonStrategy):
        self._find_button_strategy = find_button_strategy


def find_button(button: Button) -> Box | None:
    if(DEV):
        print(f"Searching for button: {button.image_path} with confidence {button.confidence} and resolution {button.resolution}")
    return self._find_button_strategy.find_button(button)




def click_in_box(box: Box):
    # Random point inside the button, staying away from the edges
    margin_x = box.width * 0.2
    margin_y = box.height * 0.2
    x = random.uniform(box.left + margin_x, box.left + box.width - margin_x)
    y = random.uniform(box.top + margin_y, box.top + box.height - margin_y)
    pyautogui.moveTo(x, y, duration=random.uniform(0.15, 0.5))
    time.sleep(random.uniform(0.05, 0.2))
    pyautogui.click()