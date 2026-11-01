import random
import time

import pyautogui

from button import Button
from pyautogui import Box

# ---- Settings ----
BASE_PATH = "images"          # where to find the button images
IMAGE = "retry.png"          # tight crop of the Retry button
RESOLUTION = (1280, 720)      # screen resolution to check for
CONFIDENCE = 0.7            # lower if it misses, raise if it misclicks
MAX_RUNS = 50                # stop after this many retries
CHECK_INTERVAL = (2.4, 8.8)  # seconds between screen checks
AFTER_CLICK_DELAY = (3.0, 6.0)  # pause after clicking (fight loading)
BREAK_EVERY = (15, 25)       # take a longer break every N-M runs
BREAK_LENGTH = (10, 20)      # seconds

DEV = True                      # take screenshots for debugging

pyautogui.FAILSAFE = True    # move mouse to a screen corner to abort
pyautogui.PAUSE = 0

def testing():
    print("Testing mode: taking a screenshot of the current screen.")
    pyautogui.screenshot("full.png")



def main():
    runs = 0
    next_break = random.randint(*BREAK_EVERY)
    button = Button(f"{BASE_PATH}/{IMAGE}-{RESOLUTION[0]}x{RESOLUTION[1]}.png", confidence=CONFIDENCE, resolution=RESOLUTION)

    while runs < MAX_RUNS:
        if(DEV):
            testing()
        box = find_button(button)

        if box:
            click_in_box(box)
            runs += 1
            print(f"Retry #{runs}")

            if runs >= next_break:
                pause = random.uniform(*BREAK_LENGTH)
                print(f"Break for {pause:.0f}s")
                time.sleep(pause)
                next_break = runs + random.randint(*BREAK_EVERY)
            else:
                time.sleep(random.uniform(*AFTER_CLICK_DELAY))

        time.sleep(random.uniform(*CHECK_INTERVAL))

    print("Reached MAX_RUNS, stopping.")


if __name__ == "__main__":
    main()