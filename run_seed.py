"""从项目根运行 seed，供 conda run 使用"""
import sys
from pathlib import Path

root = Path(__file__).resolve().parent
backend = root / "backend"
sys.path.insert(0, str(backend))
import os
os.chdir(backend)

from app.database.seed import run_seed

if __name__ == "__main__":
    run_seed()
