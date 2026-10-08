"""Where my project's files live. Everything is relative to the project folder, so the
code works on any computer without changing paths."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

RAW_ZIP = ROOT / 'data' / 'raw' / 'openipf-latest.zip'
# The row-level files have lifters' names in them, so I keep them in a folder git ignores.
INTERIM = ROOT / 'data' / 'interim'
# Only summary numbers (counts and percentages) go here, so it's safe to commit.
REPORTS = ROOT / 'reports'
