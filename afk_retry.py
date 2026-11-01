import random
import time

import pyautogui

from autogui_service import AutoGuiService
from button import Button
from find_monitor_service import find_monitor_of_window
from main_screen_finder import MainScreenFinder
from multiple_monitor_finder import MultipleMonitorFinder

# ---- Settings ----
BASE_PATH = "images"          # where to find the button images
# IMAGE = "retry"          # tight crop of the Retry button
RESOLUTION = (1280, 720)      # screen resolution to check for
CONFIDENCE = 0.9            # lower if it misses, raise if it misclicks
MAX_RUNS = 50                # stop after this many retries
CHECK_INTERVAL = (20, 30)  # seconds between screen checks
AFTER_CLICK_DELAY = (3.0, 6.0)  # pause after clicking (fight loading)
BREAK_EVERY = (15, 25)       # take a longer break every N-M runs
BREAK_LENGTH = (10, 20)      # seconds
WAIT_AFTER_RETRY = 5  # seconds to wait after clicking Retry before checking for the next button
WAIT_AFTER_CLICK = 0.5  # seconds to wait after clicking a button before checking for the next button
SKIP = True  # skip battles


DEV = True                      # take screenshots for debugging

pyautogui.FAILSAFE = True    # move mouse to a screen corner to abort
pyautogui.PAUSE = 0

def testing():
    print("Testing mode: taking a screenshot of the current screen.")
    pyautogui.screenshot("full.png")



def main():
    runs = 0
    MONITOR = find_monitor_of_window("AFK Journey") # 1 = primary, 2 = second monitor...
    buttonRetry = Button(f"{BASE_PATH}/retry-{RESOLUTION[0]}x{RESOLUTION[1]}.png", confidence=CONFIDENCE, resolution=RESOLUTION)
    buttonAutobattle = Button(f"{BASE_PATH}/autobattle-{RESOLUTION[0]}x{RESOLUTION[1]}.png", confidence=CONFIDENCE, resolution=RESOLUTION)
    buttonRecords = Button(f"{BASE_PATH}/records-{RESOLUTION[0]}x{RESOLUTION[1]}.png", confidence=CONFIDENCE, resolution=RESOLUTION)
    buttonCopy = Button(f"{BASE_PATH}/copy-{RESOLUTION[0]}x{RESOLUTION[1]}.png", confidence=CONFIDENCE, resolution=RESOLUTION)

    if MONITOR == 1:
        service = AutoGuiService(MainScreenFinder(), dev=DEV) 
    else:
        service = AutoGuiService(MultipleMonitorFinder(monitor=MONITOR, dev=DEV), dev=DEV)
        # service = AutoGuiService(MultipleMonitorFinder(0, dev=DEV), dev=DEV)

    while runs < MAX_RUNS:
        # if(DEV):
        #     testing()
        print(f"Retry #{runs}")

        retry_box = service.find_button(buttonRetry)

        if retry_box:
            print("Retry button found, clicking...")
            service.click_in_box(retry_box, wait_after_click=WAIT_AFTER_RETRY)

        boxRecords = service.find_button(buttonRecords)
        if boxRecords:
            print("Records button found, clicking...")
            service.click_in_box(boxRecords, wait_after_click=WAIT_AFTER_CLICK)

        boxCopy = service.find_button(buttonCopy)
        if boxCopy:
            print("Copy button found, clicking...")
            service.click_in_box(boxCopy, wait_after_click=WAIT_AFTER_CLICK)

        boxAutobattle = service.find_button(buttonAutobattle)
        if boxAutobattle:
            print("Autobattle button found, clicking...")
            service.click_in_box(boxAutobattle, wait_after_click=WAIT_AFTER_CLICK)

        if SKIP:
            boxSkip = service.find_button(Button(f"{BASE_PATH}/skip-{RESOLUTION[0]}x{RESOLUTION[1]}.png", confidence=CONFIDENCE, resolution=RESOLUTION))
            if boxSkip:
                print("Skip button found, clicking...")
                service.click_in_box(boxSkip, wait_after_click=WAIT_AFTER_CLICK)


        runs += 1
        end_iteration(runs)
        low, high = CHECK_INTERVAL
        wait_time = random.uniform(low / 3, high / 3) if SKIP else random.uniform(low, high)
        time.sleep(wait_time)

    print("Reached MAX_RUNS, stopping.")

def end_iteration(runs: int):
    next_break = random.randint(*BREAK_EVERY)

    if runs >= next_break:
        pause = random.uniform(*BREAK_LENGTH)
        print(f"Break for {pause:.0f}s")
        time.sleep(pause)
        next_break = runs + random.randint(*BREAK_EVERY)
    else:
        time.sleep(random.uniform(*AFTER_CLICK_DELAY))


if __name__ == "__main__":
    main()