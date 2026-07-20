from pathlib import Path
from datetime import date
from faker import Faker

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

FAKE_TR = Faker("tr_TR")
CUSTOM_DATE = date(2026, 6, 12)