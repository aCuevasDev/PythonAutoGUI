from dataclasses import dataclass
import sys
from pathlib import Path


@dataclass
class Settings:
    # Not exposed in the GUI
    def app_dir() -> Path:
        # Folder of the .exe when packaged, folder of the script otherwise
        if getattr(sys, "frozen", False):
            return Path(sys.executable).parent
        return Path(__file__).parent
    
    base_path: str = str(app_dir() / "images") # where to find the button images
    resolution: tuple = (1280, 720) # game resolution to check for
    debug: bool = False 

    # Exposed in the GUI
    confidence: float = 0.9 # lower if it misses, raise if it misclicks
    max_runs: int = 50 # stop after this many iterations
    check_interval: tuple = (5, 10) # seconds between screen checks
    after_run_delay: tuple = (3.0, 6.0) # pause after each run
    break_every: tuple = (15, 25) # take a longer break every N-M runs
    break_length: tuple = (10, 20) # seconds
    wait_after_retry: float = 5.0 # seconds to wait after clicking Retry before checking for the next button
    wait_after_click: float = 0.5 # seconds to wait after clicking a button before checking for the next button
    skip: bool = False # skip battles
    mode: str = "Battle" # stage type to select
    retries: int = 3 # number of retries for finding the skip button
    window_title: str = "AFK Journey" # title of the game window to find the monitor for

    # Out of scope for now
    # @property
    # def image_path(self) -> str:
    #     w, h = self.resolution
    #     return f"{self.base_path}/{self.image}-{w}x{h}.png"
