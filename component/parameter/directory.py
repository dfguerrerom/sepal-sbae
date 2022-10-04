from pathlib import Path

__all__ = [
    "BASE_DIR",
    "ROOT_DIR",
    "SAMPLES_DIR",
]

BASE_DIR = Path("~", "module_results").expanduser()
ROOT_DIR = BASE_DIR / "sbae-ui"
SAMPLES_DIR = ROOT_DIR / "samples"

BASE_DIR.mkdir(exist_ok=True)
ROOT_DIR.mkdir(parents=True, exist_ok=True)
SAMPLES_DIR.mkdir(parents=True, exist_ok=True)
