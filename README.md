# Internship Project Workspace

This repository contains two related e-commerce search/query projects developed during the internship:

1. mini-parser (query parsing + cleaned-data filtering, Streamlit app)
2. search_engine (advanced Kintsugi-inspired retrieval engine)

It also includes report/document artifacts used for submission and documentation.

## Repository Overview

- `mini-parser/`
  - Lightweight query processor for a product dataset
  - Supports queries like:
    - `key:value` (partial text match)
    - `key:"exact value"` (exact text match)
    - `key>value`, `key<value`, `key>=value`, `key<=value` (numeric comparisons)
  - Includes:
    - `query_processor.py` (CLI processor over JSON)
    - `preprocessed.py` (data exploration + cleaning to CSV)
    - `app.py` (Streamlit UI over cleaned CSV)
    - `data-set.json`, `cleaned_data.csv`, `index.html`

- `search_engine/`
  - Full-featured e-commerce search engine using a “Kintsugi” concept:
    - imperfect/misspelled/partial queries are repaired rather than discarded
  - Core capabilities include:
    - parsing and preprocessing
    - inverted indexing
    - fuzzy matching
    - vector search support
    - ranking/scoring (including PageRank-inspired components)
    - recommendation logic
    - web UI templates + Flask app
    - test scripts and system validation files
  - Key files:
    - `main.py`, `search_engine.py`, `web_app.py`
    - `parser.py`, `preprocessor.py`, `indexer.py`, `fuzzy_matcher.py`
    - `vector_search.py`, `pagerank_ranker.py`, `recommendation_engine.py`
    - `requirements.txt`
    - docs: `README.md`, `USAGE.md`, `KINTSUGI_README.md`, `SYSTEM_DESIGN_REPORT.md`

- Root-level artifacts
  - `search-engine.pdf`
  - `search-engine.docx`
  - `search_engine.zip`

## Folder Structure (current)

```text
internship/
├── README.md
├── .gitignore
├── search-engine.docx
├── search-engine.pdf
├── search_engine.zip
├── mini-parser/
│   ├── app.py
│   ├── cleaned_data.csv
│   ├── data-set.json
│   ├── index.html
│   ├── preprocessed.py
│   └── query_processor.py
└── search_engine/
    ├── README.md
    ├── requirements.txt
    ├── main.py
    ├── search_engine.py
    ├── web_app.py
    ├── parser.py
    ├── preprocessor.py
    ├── indexer.py
    ├── fuzzy_matcher.py
    ├── vector_search.py
    ├── unified_scoring_system.py
    ├── recommendation_engine.py
    ├── pagerank_ranker.py
    ├── granovetter_cascade.py
    ├── polya_urn_model.py
    ├── formatter.py
    ├── templates/
    ├── tests + demo/validation scripts
    ├── docs (*.md)
    ├── search_index.json
    └── __pycache__/
```

## Quick Start

### 1) mini-parser (Streamlit app)

From `mini-parser/`:

```bash
python preprocessed.py
streamlit run app.py
```

Then open the local Streamlit URL shown in terminal.

### 2) search_engine (advanced engine)

From `search_engine/`:

```bash
pip install -r requirements.txt
python main.py --data data-set.json --interactive
```

Optional web app:

```bash
python web_app.py
```

## Suggested Python Environment

Recommended:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -U pip
```

Then install project dependencies as needed (especially in `search_engine/requirements.txt`).

## Notes for GitHub

- This repo currently contains generated/cache files in some folders (for example `__pycache__/` and `*.pyc`).
- The provided `.gitignore` is configured to prevent these from being tracked going forward.
- If such files are already staged/tracked, remove them from Git index before pushing:

```bash
git rm -r --cached __pycache__ search_engine/__pycache__
git rm --cached '*.pyc'
```

(If files are not tracked yet, these commands may not be necessary.)

## Future Improvements

- Split `mini-parser` and `search_engine` into separate repos or clearly versioned modules
- Add a unified root `requirements.txt` or `pyproject.toml`
- Add reproducible test commands and CI workflow
- Add dataset/schema documentation and sample queries

---

If you want, I can next generate:
1) a cleaner, portfolio-style README for GitHub visitors, and
2) exact Git commands to initialize, commit, and push this repo.