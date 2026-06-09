"""
read_faers.py — read FAERS records straight from the committed .json.zip files.
No extraction step needed; we unzip in memory.

    from read_faers import load_records
    records = load_records()          # list of report dicts
    print(len(records))
"""

import json
import zipfile
import glob
from pathlib import Path

RAW_DIR = Path("data/raw/faers")


def load_records(raw_dir: Path = RAW_DIR) -> list:
    """Read every .json.zip in raw_dir and return a combined list of reports."""
    records = []
    zip_files = sorted(glob.glob(str(raw_dir / "*.json.zip")))
    if not zip_files:
        raise FileNotFoundError(f"No .json.zip found in {raw_dir}. Run the ingestion first.")

    for zp in zip_files:
        with zipfile.ZipFile(zp) as zf:
            inner = zf.namelist()[0]          # each zip holds one JSON file
            with zf.open(inner) as f:
                data = json.load(f)
        records.extend(data.get("results", []))
        print(f"  {zp}: {len(data.get('results', [])):,} records")

    print(f"Total: {len(records):,} records")
    return records


if __name__ == "__main__":
    load_records()