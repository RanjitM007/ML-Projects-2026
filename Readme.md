# Drug Adverse Event Predictor

An end-to-end **healthcare data engineering + ML + MLOps** project. It ingests
real adverse-event reports from the FDA's openFDA / FAERS system, builds a clean
data pipeline, trains a model to flag **serious** adverse events, and serves it
behind an API with a pharmacovigilance dashboard.

> Built to demonstrate the full lifecycle: **data ingestion → pipeline →
> modeling → MLOps → serving**, on a healthcare dataset.

---

## Problem

Given an adverse-event report (patient profile + drug[s] + reaction[s]),
predict whether the outcome is **serious** (death / hospitalization /
life-threatening / disabling) vs **not serious**. This is framed as a binary
classification problem.

**Honest data caveats (important):** FAERS data is *not* validated, a report
existing does **not** prove the drug caused the event, and duplicate /
incomplete reports occur. So this project predicts the *seriousness of a
reported event* — it does **not** claim drug→effect causation.

---

## Data source

[openFDA Drug Adverse Event API / FAERS](https://open.fda.gov/apis/drug/event/)
— FDA Adverse Event Reporting System, 2004–present, updated quarterly.

Two ways to get the data (this repo uses bulk zips):

| Method | When |
|--------|------|
| **Bulk zip** (`data/raw/faers/*.json.zip`) | Default. No API key, no skip limit. Read on-the-fly. |
| **REST API** (`api.fda.gov/drug/event.json`) | For live/incremental pulls. Needs free key for high volume. |

The bulk zip is downloaded by a **GitHub Actions** workflow (clean network =
no corporate SSL issues) and committed back to the repo, kept compressed so it
stays small.

---

## Folder structure

```
drug-adverse-event-predictor/
├── .github/
│   └── workflows/
│       └── ingest-faers.yml      # CI: downloads FAERS zip, commits to repo
├── data/
│   ├── raw/
│   │   └── faers/
│   │       └── *.json.zip        # committed (small, compressed)
│   ├── bronze/                   # generated, git-ignored
│   ├── silver/                   # generated, git-ignored
│   └── gold/                     # generated, git-ignored
├── src/
│   ├── 01_ingest_fears.py        # download smallest FAERS partition (zip)
│   ├── read_faers.py             # unzip + read records on the fly
│   ├── 02_parse_flatten.py       # Phase 3 — flatten nested JSON  (coming)
│   ├── 03_features.py            # Phase 4 — feature engineering   (coming)
│   ├── 04_train.py               # Phase 5 — model training        (coming)
│   ├── 05_evaluate.py            # Phase 6 — eval + SHAP            (coming)
│   └── 06_serve.py               # Phase 7 — serving API           (coming)
├── notebooks/
│   └── eda.ipynb                 # exploratory analysis            (coming)
├── models/                       # saved models, git-ignored       (coming)
├── app/                          # pharmacovigilance dashboard      (coming)
├── tests/                        # unit tests                       (coming)
├── .env.example                  # template for the API key
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Pipeline / roadmap

| Phase | Step | Status |
|------:|------|--------|
| 1 | Problem framing & metric | ✅ Done |
| 2 | Data ingestion (FAERS zip → repo) | ✅ Done |
| 3 | Parse & flatten nested JSON → tabular | ⬜ Next |
| 4 | Feature engineering | ⬜ |
| 5 | Model training (baseline → XGBoost) | ⬜ |
| 6 | Evaluation + SHAP explainability | ⬜ |
| 7 | MLOps: MLflow tracking + serving API | ⬜ |
| 8 | Pharmacovigilance dashboard | ⬜ |

---

## Setup

```bash
# 1. Clone and enter the repo
git clone <your-repo-url>
cd drug-adverse-event-predictor

# 2. Create a virtual env and install deps
python -m venv venv
# Windows:  venv\Scripts\activate
# macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
```

The FAERS zip is already committed under `data/raw/faers/`. To verify you can
read it:

```bash
python src/read_faers.py
# -> prints record counts
```

> Run all scripts from the **repo root** so relative `data/` paths resolve.

---

## Re-fetching data (GitHub Actions)

1. Push the repo to GitHub.
2. Go to the **Actions** tab → **Ingest FAERS data** → **Run workflow**.
3. The workflow downloads the smallest FAERS partition and commits the zip.
4. `git pull` to get it locally — no API key or SSL setup needed.

Alternatively, download a small `.json.zip` manually from
[open.fda.gov/data/downloads](https://open.fda.gov/data/downloads/) and drop it
into `data/raw/faers/`.

---

## Tech stack

Python · openFDA/FAERS · pandas / PySpark · scikit-learn / XGBoost · SHAP ·
MLflow · FastAPI · GitHub Actions (CI/CD) · (Azure / Databricks for the cloud
version)

---

## Notes

- Secrets live in `.env` (git-ignored). Never commit your API key.
- Full extracted data (`bronze/silver/gold`) is git-ignored; only the small raw
  zip is versioned.