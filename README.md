# AFK Journey Auto Retry

![Python](https://img.shields.io/badge/python-3.11%2B-blue)
![Platform](https://img.shields.io/badge/platform-windows-lightgrey)

A small Python autoclicker that farms AFK Journey stages for you. It replays the stage in a loop by copying a formation from the Records screen, and it fakes human input with randomized timings and click positions so the activity doesn't look like a script.

> [!WARNING]
> This is a personal, educational project. Automating gameplay may violate AFK Journey's Terms of Service. Use it at your own risk — the author is not responsible for any action taken against your account. Please keep it out of competitive and PvP content.

---

## ✨ Features

- **Hands-off stage farming** — clicks Retry, opens Records, copies the first formation it finds, and starts the battle again.
- **Optional battle skipping** — clicks Battle and then Skip, retrying the Skip search in case the button is hidden behind an ultimate animation.
- **Human-like behavior** — clicks land on a random point inside each button, mouse movement and press durations vary every time, and all delays are randomized ranges with longer breaks sprinkled in.
- **Multi-monitor aware** — locates the game window by title, figures out which monitor it lives on, and only searches that screen.
- **Live settings** — tweak timings, confidence, run limits and more from the GUI while the bot is running.
- **Failsafe** — press stop to abort instantly.

## 📋 Requirements

|        |                                                                |
| ------ | -------------------------------------------------------------- |
| OS     | Windows (relies on `pygetwindow`)                              |
| Python | 3.11+ — only needed to run from source or build the exe        |
| Game   | AFK Journey, windowed, **1280x720**, visible and not minimized |

## 💾 Installation

### Prebuilt executable (no Python needed)

1. Download `AFKRetry.zip` from the [releases page](https://github.com/aCuevasDev/PythonAutoGUI/releases).
2. Extract the archive anywhere.
3. Run `AFKRetry.exe`.

> [!IMPORTANT]
> Keep the `images` folder and `settings.toml` next to `AFKRetry.exe`. The app looks up its button templates and settings relative to the executable, so moving the exe out of the folder will break detection or startup.

Windows may warn about an unsigned executable — that's expected for PyInstaller builds; choose _More info → Run anyway_.

### From source

```bash
git clone https://github.com/aCuevasDev/PythonAutoGUI.git
cd PythonAutoGUI
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python gui.py
```

Running from source only needs `requirements.txt` — PyInstaller is only required to package the app.

## 🎮 Usage

### The app

Launch `AFKRetry.exe` (or `python gui.py`). Point **Window title** at your game window (default `AFK Journey`), tune the settings, then press **Start**. The log panel narrates each step (`retry found, clicking`, `skip not found`, …) while the status line tracks progress as `Runs: X / max`.

### Headless

Runs with the settings from `settings.toml` until you hit Ctrl+C:

```bash
python afk_retry.py
```

## 📦 Building the executable

```bash
pip install pyinstaller
python build.py
```

The build produces:

```
dist/AFKRetry/AFKRetry.exe   the app
dist/AFKRetry/images/        button templates, copied automatically
dist/AFKRetry/settings.toml  settings, copied automatically
dist/AFKRetry.zip            the folder above, zipped for release
```

`build.py` optional flags:

| Flag        | Effect                                                       |
| ----------- | ------------------------------------------------------------ |
| `--console` | Keep the terminal window open — handy for seeing tracebacks. |
| `--no-zip`  | Skip creating `AFKRetry.zip`.                                |

The PyInstaller spec and work files are generated into `build/`, so nothing outside `dist/` needs to be kept.

## ⚙️ Settings

All defaults live in `settings.toml`, which is read once at startup. Edit it to change the values the app starts with; changes made in the GUI apply to the current session only.

| Setting             | Default       | What it does                                                                                                          |
| ------------------- | ------------- | --------------------------------------------------------------------------------------------------------------------- |
| Window title        | `AFK Journey` | Title fragment used to find the game window and its monitor.                                                          |
| Stage type          | `Battle`      | Selects the Phantimal Challenge or Battle stage tab before starting the battle.                                       |
| Confidence          | `0.85`        | Image-match threshold (0.5–1.0). Lower it when buttons get missed, raise it when the bot misclicks.                   |
| Skip battles        | off           | Battle → Skip. Turn it **on** to skip battles instead of letting them auto-run.                                       |
| Max runs            | `100`         | Stop after this many iterations.                                                                                      |
| Skip button retries | `3`           | How many times to look for Skip before giving up on a battle.                                                         |
| Wait after Retry    | `5.0 s`       | Pause after Retry so the next screen can load.                                                                        |
| Wait after click    | `0.7 s`       | Pause after every other click.                                                                                        |
| Check interval      | `5–10 s`      | Delay between runs. Automatically divided by 5 when **Skip battles** is on.                                           |
| Delay after run     | `3–6 s`       | Short pause at the end of each run.                                                                                   |
| Break every         | `15–25 runs`  | Take a longer break after this many runs.                                                                             |
| Break length        | `10–20 s`     | How long that break lasts.                                                                                            |

The `[app]` section is deliberately kept out of the GUI: `base_path` (template folder), `resolution` (picks the image variant), and `debug` (prints matches and saves `debug_monitor.png`). The `[options]` section is what the GUI exposes.

## 🔍 How it works

1. Find the game window by title and work out which monitor it's on.
2. Grab that monitor with `mss` — or the whole screen if it's the primary one — and match the button template using OpenCV-backed matching.
3. Click a random point comfortably inside the matched button.
4. Repeat the cycle: `retry` → `records` → `copy` → selected stage tab → `battle` → `skip`.
5. Wait a random amount between runs, and take a longer break every N–M runs.

Templates live in `images/` and are resolved per resolution as `images/<button>-<width>x<height>.png`.

<table>
<tr><td><b>File</b></td><td><b>Role</b></td></tr>
<tr><td><code>gui.py</code></td><td>Tkinter GUI and main entry point</td></tr>
<tr><td><code>afk_retry.py</code></td><td>Bot loop (<code>RetryBot</code>) and headless entry point</td></tr>
<tr><td><code>settings.toml</code></td><td>Settings defaults, read at startup</td></tr>
<tr><td><code>settings.py</code></td><td>Loads <code>settings.toml</code> into the <code>Settings</code> dataclass</td></tr>
<tr><td><code>autogui_service.py</code></td><td>Find + click helpers with randomized input</td></tr>
<tr><td><code>button.py</code></td><td>Button value object (image path, confidence)</td></tr>
<tr><td><code>find_button_strategy.py</code></td><td>Abstract strategy for locating buttons</td></tr>
<tr><td><code>main_screen_finder.py</code></td><td>Strategy for the primary monitor</td></tr>
<tr><td><code>multiple_monitor_finder.py</code></td><td>Strategy for secondary monitors</td></tr>
<tr><td><code>find_monitor_service.py</code></td><td>Window title → monitor index</td></tr>
<tr><td><code>build.py</code></td><td>Packaging script: PyInstaller build, image and settings copy, zip</td></tr>
</table>

## ⚠️ Limitations

- **1280x720 only.** Templates are cropped at that resolution, so other resolutions will fail to match or misclick.
- The game has to stay visible — the bot screenshots it, so minimized or covered windows break detection.
- Windows only.
- Image matching isn't perfect: animations and screen transitions can hide a button for a moment, which is why Skip gets retried.

## 🗺️ Roadmap

- [ ] Scale templates from the game's actual resolution instead of requiring 1280x720.
- [ ] Pick the stage type automatically — farm **Phantimal** or **normal** stages depending on what's available.
