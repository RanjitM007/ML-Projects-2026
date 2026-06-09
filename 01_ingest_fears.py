"""
Phase 2 (alternative) — Bulk Download (Bronze layer)
Drug Adverse Event Predictor | Source: openFDA FAERS bulk files

Why bulk instead of the API?
  - No 25,000-record skip limit -> you can get a large dataset.
  - No API key needed.
  - If Python SSL still fails on your corporate network, you can download the
    same .json.zip files MANUALLY from https://open.fda.gov/data/downloads/
    (browser bypasses the corporate-cert problem), drop them in
    data/bronze/faers_zip/, and just run the EXTRACT step below.

How it works:
  1. Reads the file index from https://api.fda.gov/download.json
  2. Picks the first N partitions of drug/event
  3. Downloads each .json.zip and extracts the JSON into data/bronze/faers/

Setup:
    pip install requests truststore
    python 01_bulk_download_faers.py
"""

import json
import zipfile
import io
import requests
from pathlib import Path

# --- Use the OS certificate store (fixes corporate SSL errors) ---
try:
    import truststore
    truststore.inject_into_ssl()
except ImportError:
    pass

# ---------- Config ----------
INDEX_URL  = "https://api.fda.gov/download.json"
N_PARTS    = 3                       # how many partition files to pull (each = many thousands of records)
OUT_DIR    = Path("data/bronze/faers")
ZIP_DIR    = Path("data/bronze/faers_zip")   # raw zips (also where manual downloads go)
# -----------------------------

OUT_DIR.mkdir(parents=True, exist_ok=True)
ZIP_DIR.mkdir(parents=True, exist_ok=True)


def get_partitions() -> list:
    """Return the list of drug/event partition file descriptors."""
    resp = requests.get(INDEX_URL, timeout=60)
    resp.raise_for_status()
    index = resp.json()
    return index["results"]["drug"]["event"]["partitions"]


def download_and_extract(part: dict, i: int) -> int:
    """Download one .json.zip partition and write its JSON to bronze. Returns record count."""
    url = part["file"]
    zip_path = ZIP_DIR / f"faers_part_{i:04d}.json.zip"

    print(f"  [{i+1}] downloading {url}")
    resp = requests.get(url, timeout=300)
    resp.raise_for_status()
    zip_path.write_bytes(resp.content)

    with zipfile.ZipFile(io.BytesIO(resp.content)) as zf:
        inner_name = zf.namelist()[0]           # each zip holds one JSON file
        with zf.open(inner_name) as f:
            data = json.load(f)

    results = data.get("results", [])
    out_file = OUT_DIR / f"faers_part_{i:04d}.json"
    out_file.write_text(json.dumps(results))
    print(f"      extracted {len(results):,} records -> {out_file}")
    return len(results)


def main() -> None:
    parts = get_partitions()
    print(f"drug/event has {len(parts)} partitions available. Pulling first {N_PARTS}.\n")

    total = 0
    for i, part in enumerate(parts[:N_PARTS]):
        total += download_and_extract(part, i)

    print(f"\nDone. {total:,} raw reports written to {OUT_DIR}/")


if __name__ == "__main__":
    main()
