import random
import threading
from typing import Callable

import pyautogui

from autogui_service import AutoGuiService
from button import Button
from find_monitor_service import find_monitor_of_window
from main_screen_finder import MainScreenFinder
from multiple_monitor_finder import MultipleMonitorFinder
from settings import Settings


pyautogui.FAILSAFE = True  # move mouse to a screen corner to abort
pyautogui.PAUSE = 0

TIME_REDUCED_IF_SKIP = 5  # reduce wait times by this factor if skip is enabled


class RetryBot:
    """Runs the retry loop in a background thread. Settings are read live."""

    def __init__(
        self,
        settings: Settings,
        log: Callable[[str], None] = print,
        on_finished: Callable[[], None] = lambda: None,
    ):
        self.settings = settings
        self.runs = 0
        self._log = log
        self._on_finished = on_finished
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None

    # ---------- control ----------
    @property
    def running(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    def start(self):
        if self.running:
            return
        self._stop.clear()
        self.runs = 0
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        self._stop.set()

    def join(self, timeout: float | None = None):
        if self._thread:
            self._thread.join(timeout)

    # ---------- loop ----------
    def _run(self):
        s = self.settings
        try:
            monitor = find_monitor_of_window(s.window_title.strip())
            if monitor is None:
                self._log(f'"{s.window_title.strip()}" window not found (or minimized)')
                return

            if monitor == 1:
                finder = MainScreenFinder()
            else:
                finder = MultipleMonitorFinder(monitor=monitor, dev=s.debug)
            service = AutoGuiService(finder, dev=s.debug)

            self._log(f"Started on monitor {monitor}")
            next_break = random.randint(*s.break_every)

            while self.runs < s.max_runs and not self._stop.is_set():
                self._log(f"Run #{self.runs + 1}")
                self._iteration(service)
                if self._stop.is_set():
                    break
                self.runs += 1

                if self.runs >= next_break:
                    pause = random.uniform(*s.break_length)
                    self._log(f"Break for {pause:.0f}s")
                    if self._stop.wait(pause):
                        break
                    next_break = self.runs + random.randint(*s.break_every)
                elif self._stop.wait(random.uniform(*s.after_run_delay)):
                    break

                low, high = s.check_interval
                wait = random.uniform(low / TIME_REDUCED_IF_SKIP, high / TIME_REDUCED_IF_SKIP) if s.skip else random.uniform(low, high)
                if self._stop.wait(wait):
                    break

            self._log("Reached max runs" if self.runs >= s.max_runs else "Stopped")
        except pyautogui.FailSafeException:
            self._log("Failsafe triggered (mouse in a corner), stopped")
        except Exception as e:
            self._log(f"Error: {e}")
        finally:
            self._on_finished()

    def _iteration(self, service: AutoGuiService):
        s = self.settings

        for name, wait in (
            ("retry", s.wait_after_retry),
            ("records", s.wait_after_click),
            ("copy", s.wait_after_click),
        ):
            if self._stop.is_set():
                return
            self._try_click(service, name, wait)

        if not s.skip:
            self._try_click(service, "autobattle", s.wait_after_click)
            self._try_click(service, "autobattlecomplete", s.wait_after_click)
            return
        
        # if skip is enabled, click the battle button and then the skip button (if it appears)
        self._try_click(service, "battle", s.wait_after_click)
        if self._stop.wait(2):  # give the skip button time to appear
            return
        for _ in range(s.retries):
            if self._stop.wait(1):
                return
            if self._try_click(service, "skip", s.wait_after_click):
                break

    def _try_click(
        self,
        service: AutoGuiService,
        name: str,
        wait: float,
    ) -> bool:
        s = self.settings
        w, h = s.resolution
        button = Button(
            f"{s.base_path}/{name}-{w}x{h}.png",
            confidence=s.confidence,
            resolution=s.resolution,
        )
        box = service.find_button(button)
        if not box:
            self._log(f"{name} not found")
            return False
        self._log(f"{name} found, clicking")
        service.click_in_box(box, wait_after_click=wait)
        return True


def main():
    """Run without the GUI. Ctrl+C to stop."""
    bot = RetryBot(Settings())
    bot.start()
    try:
        while bot.running:
            bot.join(0.5)
    except KeyboardInterrupt:
        bot.stop()
        bot.join()


if __name__ == "__main__":
    main()