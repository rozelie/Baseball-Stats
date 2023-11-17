"""Local project path constants."""
from pathlib import Path

DATA_DIR = Path("/tmp/retrosheet")
PROJECT_ROOT = Path(__file__).parents[1]
DOTENV = PROJECT_ROOT / ".env"
