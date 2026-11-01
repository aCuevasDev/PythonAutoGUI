import queue
import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText

from afk_retry import RetryBot
from settings import Settings

# key in Settings, label, minimum allowed, spinbox max, step, unit, integer?
SINGLES = [
    ("max_runs", "Max runs", 1, 9999, 1, "", True),
    ("retries", "Skip button retries", 1, 20, 1, "", True),
    ("wait_after_retry", "Wait after Retry", 0, 60, 0.5, "s", False),
    ("wait_after_click", "Wait after click", 0, 60, 0.1, "s", False),
]
RANGES = [
    ("check_interval", "Check interval (automatically lowered if skip is enabled)", 0.1, 300, 0.5, "s", False),
    ("after_run_delay", "Delay after run", 0.1, 120, 0.5, "s", False),
    ("break_every", "Break every", 1, 500, 1, "runs", True),
    ("break_length", "Break length", 1, 600, 1, "s", True),
]
MAX_LOG_LINES = 500


def _get(var: tk.Variable, current):
    """Read a Tk variable, keeping the current value if the field is half-typed."""
    try:
        return var.get()
    except tk.TclError:
        return current


def _var(is_int: bool, value):
    return tk.IntVar(value=value) if is_int else tk.DoubleVar(value=value)


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("AFK Retry")
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self._close)

        self.settings = Settings()
        self.queue: queue.Queue = queue.Queue()
        self.bot = RetryBot(
            self.settings, self.queue.put, lambda: self.queue.put(None)
        )

        s = self.settings
        self.v_conf = tk.DoubleVar(value=s.confidence)
        self.v_skip = tk.BooleanVar(value=s.skip)
        self.v_title = tk.StringVar(value=s.window_title)
        self.singles = {
            key: _var(is_int, getattr(s, key))
            for key, _, _, _, _, _, is_int in SINGLES
        }
        self.ranges = {
            key: tuple(_var(is_int, v) for v in getattr(s, key))
            for key, _, _, _, _, _, is_int in RANGES
        }

        self._build()

        all_vars = [self.v_conf, self.v_skip, self.v_title, *self.singles.values()]
        for pair in self.ranges.values():
            all_vars.extend(pair)
        for var in all_vars:
            var.trace_add("write", self._apply)

        self._apply()
        self._poll()

    # ---------- UI ----------
    def _spinbox(self, parent, var, maximum, step, is_int):
        opts = {} if is_int else {"format": "%.1f"}
        return ttk.Spinbox(
            parent, from_=0, to=maximum, increment=step,
            textvariable=var, width=7, **opts,
        )

    def _build(self):
        f = ttk.Frame(self, padding=12)
        f.grid()
        r = 0
        ttk.Label(f, text="Window title").grid(row=r, column=0, sticky="w", pady=2)
        ttk.Entry(f, textvariable=self.v_title, width=24).grid(
            row=r, column=1, columnspan=3, sticky="ew", padx=2, 
        )
        r += 1
        ttk.Label(f, text="Confidence (lower if it misses, raise if it misclicks)").grid(row=r, column=0, sticky="w", pady=2)
        r += 1
        ttk.Scale(f, from_=0.5, to=1.0, variable=self.v_conf, length=150).grid(
            row=r, column=0, columnspan=2, sticky="ew", padx=2
        )
        self.lbl_conf = ttk.Label(f, width=5)
        self.lbl_conf.grid(row=r, column=3, sticky="w")
        r += 1

        ttk.Checkbutton(f, text="Skip battles (Turn false if running stages)", variable=self.v_skip).grid(
            row=r, column=0, columnspan=4, sticky="w", pady=2
        )
        r += 1

        for key, label, _, maximum, step, unit, is_int in SINGLES:
            ttk.Label(f, text=label).grid(row=r, column=0, sticky="w", pady=2)
            self._spinbox(f, self.singles[key], maximum, step, is_int).grid(
                row=r, column=1, padx=2
            )
            ttk.Label(f, text=unit).grid(row=r, column=3, sticky="w")
            r += 1

        ttk.Label(f, text="min").grid(row=r, column=1)
        ttk.Label(f, text="max").grid(row=r, column=2)
        r += 1

        for key, label, _, maximum, step, unit, is_int in RANGES:
            ttk.Label(f, text=label).grid(row=r, column=0, sticky="w", pady=2)
            for col, var in enumerate(self.ranges[key], start=1):
                self._spinbox(f, var, maximum, step, is_int).grid(
                    row=r, column=col, padx=2
                )
            ttk.Label(f, text=unit).grid(row=r, column=3, sticky="w")
            r += 1

        buttons = ttk.Frame(f)
        buttons.grid(row=r, column=0, columnspan=4, pady=8)
        self.btn_start = ttk.Button(buttons, text="Start", command=self._start)
        self.btn_start.pack(side="left", padx=4)
        self.btn_stop = ttk.Button(
            buttons, text="Stop", command=self._stop, state="disabled"
        )
        self.btn_stop.pack(side="left", padx=4)
        r += 1

        self.lbl_status = ttk.Label(f)
        self.lbl_status.grid(row=r, column=0, columnspan=4, sticky="w")
        r += 1

        self.log_box = ScrolledText(f, width=44, height=9, state="disabled")
        self.log_box.grid(row=r, column=0, columnspan=4, pady=(4, 0))

    # ---------- GUI -> settings ----------
    def _pair(self, key: str, minimum: float):
        current = getattr(self.settings, key)
        lo_var, hi_var = self.ranges[key]
        lo = max(minimum, _get(lo_var, current[0]))
        hi = max(minimum, _get(hi_var, current[1]))
        return tuple(sorted((lo, hi)))

    def _apply(self, *_args):
        s = self.settings
        s.confidence = round(_get(self.v_conf, s.confidence), 2)
        s.skip = _get(self.v_skip, s.skip)
        s.window_title = _get(self.v_title, s.window_title)
        for key, _label, minimum, *_rest in SINGLES:
            current = getattr(s, key)
            setattr(s, key, max(minimum, _get(self.singles[key], current)))
        for key, _label, minimum, *_rest in RANGES:
            setattr(s, key, self._pair(key, minimum))
        self.lbl_conf.config(text=f"{s.confidence:.2f}")

    # ---------- actions ----------
    def _start(self):
        self._apply()
        self._set_running(True)
        self.bot.start()

    def _stop(self):
        self.btn_stop.config(state="disabled")
        self.bot.stop()

    def _set_running(self, running: bool):
        self.btn_start.config(state="disabled" if running else "normal")
        self.btn_stop.config(state="normal" if running else "disabled")

    def _write_log(self, msg: str):
        self.log_box.config(state="normal")
        self.log_box.insert("end", msg + "\n")
        if int(self.log_box.index("end-1c").split(".")[0]) > MAX_LOG_LINES:
            self.log_box.delete("1.0", "101.0")
        self.log_box.see("end")
        self.log_box.config(state="disabled")

    def _poll(self):
        # The bot runs in another thread, so it talks to the GUI via a queue
        while True:
            try:
                msg = self.queue.get_nowait()
            except queue.Empty:
                break
            if msg is None:  # bot finished
                self._set_running(False)
            else:
                self._write_log(msg)

        self.lbl_status.config(
            text=f"Runs: {self.bot.runs} / {self.settings.max_runs}"
        )
        self.after(200, self._poll)

    def _close(self):
        self.bot.stop()
        self.destroy()


if __name__ == "__main__":
    App().mainloop()