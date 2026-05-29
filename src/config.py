import os
import json
import datetime as dt

# -- Theme constants --
BG_PRIMARY = "#0d1117"
BG_SECONDARY = "#161b22"
BG_BUTTON = "#21262d"
BG_BUTTON_HOVER = "#30363d"
TEXT_PRIMARY = "#c9d1d9"
TEXT_MUTED = "#7d8590"
COLOR_PAINTED = "#39d353"
COLOR_HOVER = "#4cff6a"
COLOR_RED = "#da3633"
COLOR_RED_HOVER = "#f85149"
COLOR_GEN = "#238636"
COLOR_GEN_HOVER = "#2ea043"

BOX_SIZE = 24
BOX_GAP = 4
TOP_MARGIN = 25
LEFT_MARGIN = 40

MIN_YEAR = 1970
MAX_YEAR = 9999


class Config:
    def __init__(self):
        self.config_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), ".pwg_config"
        )
        self.week_start = "sunday"
        self.year = dt.datetime.now().year
        self.dir = os.path.abspath(
            os.path.join(os.path.dirname(os.path.dirname(__file__)), ".paintwithgit")
        )
        self.load()

    def clamp_year(self, year):
        try:
            return max(MIN_YEAR, min(MAX_YEAR, int(year)))
        except (ValueError, TypeError):
            return dt.datetime.now().year

    def load(self):
        try:
            with open(self.config_path, "r") as f:
                data = json.loads(f.read())
                if "year" in data:
                    self.year = self.clamp_year(data["year"])
                if "week_start" in data:
                    self.week_start = data["week_start"]
                if "dir" in data and os.path.isabs(data["dir"]):
                    self.dir = data["dir"]
        except Exception:
            pass

    def save(self):
        try:
            with open(self.config_path, "w") as f:
                json.dump({
                    "year": self.year,
                    "week_start": self.week_start,
                    "dir": self.dir,
                }, f)
        except Exception:
            pass
