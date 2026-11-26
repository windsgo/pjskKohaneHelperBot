"""Project paths anchored to this package, independent of the working directory."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
ASSETS = ROOT / 'assets'
MASTERDATA = ROOT / 'masterdata'
RUNTIME = ROOT / 'runtime'
OUTPUT = ROOT / 'output'
JOBS = RUNTIME / 'jobs'
STATE = RUNTIME / 'state'
