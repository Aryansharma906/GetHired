#!/usr/bin/env python3
"""Backwards-compatibility redirect to sync_frontierpilot.py."""
import os, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import scripts.sync_frontierpilot as fp
if __name__ == '__main__':
    fp.main()
