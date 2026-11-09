import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path


def app_dir() -> Path:
    # Folder of the .exe when packaged, folder of the script otherwise
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).parent


CONFIG_PATH = app_dir() / "settings.toml"

with CONFIG_PATH.open("rb") as f:
    _config = tomllib.load(f)


@dataclass
class Settings:
    # Not exposed in the GUI
    base_path: str = str(app_dir() / _config["app"]["base_path"])
    resolution: tuple = tuple(_config["app"]["resolution"])
    debug: bool = _config["app"]["debug"]

    # Exposed in the GUI
    confidence: float = _config["options"]["confidence"]
    confidence_battle_phantimal: float = _config["options"]["confidence_battle_phantimal"]
    max_runs: int = _config["options"]["max_runs"]
    check_interval: tuple = tuple(_config["options"]["check_interval"])
    after_run_delay: tuple = tuple(_config["options"]["after_run_delay"])
    break_every: tuple = tuple(_config["options"]["break_every"])
    break_length: tuple = tuple(_config["options"]["break_length"])
    wait_after_retry: float = _config["options"]["wait_after_retry"]
    wait_after_click: float = _config["options"]["wait_after_click"]
    skip: bool = _config["options"]["skip"]
    mode: str = _config["options"]["mode"]
    retries: int = _config["options"]["retries"]
    window_title: str = _config["options"]["window_title"]

    # Out of scope for now
    # @property
    # def image_path(self) -> str:
    #     w, h = self.resolution
    #     return f"{self.base_path}/{self.image}-{w}x{h}.png"
