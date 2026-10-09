import sys
from pathlib import Path

# Make serve.py and the tests package importable from any working directory.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
