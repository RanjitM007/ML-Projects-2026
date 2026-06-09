"""
Phase 2 — Data Ingestion (Bronze layer, ZIP kept compressed)
Drug Adverse Event Predictor | Source: openFDA FAERS bulk files

Strategy:
  - Pick the SMALLEST drug/event partitions (so each .json.zip stays well
    under GitHub's 100MB file limit and can live in the repo).
  - Download them as .json.zip and KEEP THEM COMPRESSED in data/raw/faers/.
  - We unzip on-the-fly when reading (see read_faers.py), so the repo stays small.

Run this on GitHub Actions (clean network = no corporate SSL issues),
which then commits the zip(s) back to the repo.

Setup:
    pip install requests truststore
    python 01_ingest_fears.py
"""

import json
import requests
from pathlib import Path

# --- Use the OS certificate store (helps on corporate networks) ---
try:
    import truststore
    truststore.inject_into_ssl()
except ImportError:
    pass

# ---------- Config ----------
INDEX_URL = "https://api.fda.gov/download.json"
N_PARTS   = 1          # how many (smallest) partitions to keep in the repo
MAX_MB    = 90         # skip any single zip bigger than this (GitHub limit = 100MB)
RAW_DIR   = Path("data/raw/faers")     # committed to repo (zips only)
# -----------------------------

RAW_DIR.mkdir(parents=True, exist_ok=True)


def get_partitions() -> list:
    """Return drug/event partition descriptors, each with file URL + size_mb."""
    resp = requests.get(INDEX_URL, timeout=60)
    resp.raise_for_status()
    return resp.json()["results"]["drug"]["event"]["partitions"]


def parse_size_mb(part: dict) -> float:
    try:
        return float(part.get("size_mb", 99999))
    except (TypeError, ValueError):
        return 99999.0


def main() -> None:
    parts = get_partitions()
    # Smallest first, and only those under the GitHub file-size limit.
    small = sorted((p for p in parts if parse_size_mb(p) <= MAX_MB),
                   key=parse_size_mb)

    if not small:
        raise SystemExit(f"No partition under {MAX_MB}MB found. Lower the data or use artifacts.")

    print(f"{len(parts)} partitions total; keeping the {N_PARTS} smallest (<= {MAX_MB}MB):\n")

    for i, part in enumerate(small[:N_PARTS]):
        url = part["file"]
        size = parse_size_mb(part)
        zip_path = RAW_DIR / f"faers_part_{i:02d}.json.zip"

        print(f"  [{i+1}] {size:.1f} MB  {url}")
        resp = requests.get(url, timeout=600)
        resp.raise_for_status()
        zip_path.write_bytes(resp.content)
        print(f"      saved -> {zip_path} ({len(resp.content)/1e6:.1f} MB on disk)")

    print(f"\nDone. Zip(s) kept in {RAW_DIR}/ (compressed, ready to commit).")


if __name__ == "__main__":
    main()
