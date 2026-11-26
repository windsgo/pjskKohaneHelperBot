"""Locate the real MySekai capture used by end-to-end render tests.

Set SEKAI_TEST_CAPTURE when the capture lives outside the project. Tests that
need it raise SystemExit('SKIP ...') so a missing private sample does not look
like a code failure.
"""
import os
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
NAME='[428] response_mkcn-prod-public-60001-1..com_mysekai'
CANDIDATES=[ROOT/NAME,Path('D:/self/测试烤森逆向')/NAME]


def require_capture():
    override=os.environ.get('SEKAI_TEST_CAPTURE')
    if override:
        path=Path(override)
        if path.is_file():return path
        raise SystemExit(f'SKIP: SEKAI_TEST_CAPTURE does not exist: {path}')
    for path in CANDIDATES:
        if path.is_file():return path
    raise SystemExit(f'SKIP: no MySekai capture named {NAME}; set SEKAI_TEST_CAPTURE to run this test')
