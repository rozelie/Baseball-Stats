"""Local project path constants."""
from pathlib import Path

COBP_DIR = Path.home() / ".cobp"
DATA_DIR = COBP_DIR / "data"

for dir in [COBP_DIR, DATA_DIR]:
    dir.mkdir(exist_ok=True, parents=True)

PROJECT_ROOT = Path(__file__).parents[1]
DOTENV = PROJECT_ROOT / ".env"
