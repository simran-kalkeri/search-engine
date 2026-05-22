# Internship Project Workspace

This repository contains two Python projects built during an internship around
e-commerce product search, query parsing, and information retrieval.

- `mini-parser`: a lightweight query parser and Streamlit data-filtering app.
- `search_engine`: a larger Kintsugi-inspired e-commerce search engine that
  supports fuzzy matching, ranking, recommendations, and a Flask web UI.

The workspace also includes final report artifacts used for submission.

## Project Highlights

| Area | Description |
| --- | --- |
| Query parsing | Supports structured filters such as `key:value`, exact quoted matches, and numeric comparisons. |
| Data preparation | Cleans and transforms the product dataset for easier searching and filtering. |
| Search indexing | Builds an inverted index for faster product lookup. |
| Fuzzy search | Repairs misspelled, incomplete, and partial user queries instead of discarding them. |
| Ranking | Combines scoring techniques, including TF-IDF-style relevance and PageRank-inspired logic. |
| Recommendations | Includes recommendation and behavior-inspired ranking modules. |
| User interfaces | Provides both a Streamlit app and a Flask web application. |

## Repository Structure

```text
internship/
|-- README.md
|-- .gitignore
|-- search-engine.docx
|-- search-engine.pdf
|-- search_engine.zip
|-- mini-parser/
|   |-- app.py
|   |-- cleaned_data.csv
|   |-- data-set.json
|   |-- index.html
|   |-- preprocessed.py
|   `-- query_processor.py
`-- search_engine/
    |-- README.md
    |-- USAGE.md
    |-- KINTSUGI_README.md
    |-- SYSTEM_DESIGN_REPORT.md
    |-- requirements.txt
    |-- main.py
    |-- search_engine.py
    |-- web_app.py
    |-- start_web.py
    |-- parser.py
    |-- preprocessor.py
    |-- indexer.py
    |-- fuzzy_matcher.py
    |-- vector_search.py
    |-- unified_scoring_system.py
    |-- recommendation_engine.py
    |-- pagerank_ranker.py
    |-- granovetter_cascade.py
    |-- polya_urn_model.py
    |-- formatter.py
    |-- templates/
    `-- test and validation scripts
```

## Getting Started

### 1. Create a Python environment

From the repository root:

```bash
python -m venv .venv
```

Activate it:

```bash
# Windows PowerShell
.\.venv\Scripts\Activate.ps1

# macOS/Linux
source .venv/bin/activate
```

Upgrade `pip`:

```bash
python -m pip install --upgrade pip
```

## Mini Parser

The `mini-parser` project is a compact product-data query processor. It can run
as a command-line processor or as a Streamlit app over cleaned CSV data.

### Features

- Partial text search: `brand:samsung`
- Exact text search: `brand:"Samsung"`
- Numeric comparisons: `price>1000`, `rating>=4.5`
- Dataset preprocessing from JSON to CSV
- Simple Streamlit interface for interactive filtering

### Run the Streamlit app

```bash
cd mini-parser
pip install streamlit pandas
python preprocessed.py
streamlit run app.py
```

### Run the query processor

```bash
cd mini-parser
python query_processor.py
```

## Kintsugi Search Engine

The `search_engine` project is the advanced retrieval system in this workspace.
It is inspired by the Kintsugi idea of repairing imperfections: misspelled,
partial, or incomplete queries are still treated as useful signals.

### Core Capabilities

- JSON data parsing and validation
- Text normalization and preprocessing
- Inverted index construction
- Exact, fuzzy, and combined search modes
- Vector-search support
- PageRank-inspired ranking
- Unified scoring logic
- Recommendation engine
- Flask web interface
- Test, demo, and validation scripts

### Install dependencies

```bash
cd search_engine
pip install -r requirements.txt
```

### Run interactive search

```bash
python main.py --data data-set.json --interactive
```

If the dataset is stored in another folder, pass the correct path:

```bash
python main.py --data ../mini-parser/data-set.json --interactive
```

### Run a single query

```bash
python main.py --data data-set.json --query "wireless headphones"
```

### Run fuzzy search

```bash
python main.py --data data-set.json --query "samsng galaxy" --fuzzy
```

### Run the Flask web app

```bash
python web_app.py
```

Or use the helper script:

```bash
python start_web.py
```

Then open the local URL shown in the terminal, usually:

```text
http://localhost:5000
```

## Example Queries

```text
iphone 14
samsng galaxy
wireless headphones
gaming mouse
laptop i7
noise cancling headphones
brand:"Sony"
price<5000
rating>=4.5
```

## Testing and Validation

The `search_engine` folder includes several standalone test and validation
scripts. After installing dependencies, run the scripts from inside
`search_engine/`.

```bash
python simple_test.py
python test_system.py
python final_validation.py
python test_web_app.py
```

If `pytest` tests are added or collected in the future, use:

```bash
python -m pytest
```

## Documentation

Additional project documentation is available in `search_engine/`:

- `README.md`: detailed search engine overview
- `USAGE.md`: CLI, web UI, and example search usage
- `KINTSUGI_README.md`: Kintsugi search concept and implementation notes
- `KINTSUGI_ENGINE_WORKFLOW.md`: workflow-level explanation
- `SYSTEM_DESIGN_REPORT.md`: architecture and design report
- `TEST_RESULTS.md`: recorded validation results

Root-level submission artifacts:

- `search-engine.pdf`
- `search-engine.docx`
- `search_engine.zip`

## Git Notes

The `.gitignore` excludes generated data, archives, documents, Python cache
files, and environment files:

- `*.csv`
- `*.json`
- `*.zip`
- `*.pdf`
- `*.docx`
- `__pycache__/`
- `*.pyc`
- `venv/`
- `.env`

If any generated files were already tracked before the ignore rules were added,
remove them from Git tracking without deleting the local copies:

```bash
git rm --cached path/to/file
```

## Suggested Improvements

- Add a root-level `requirements.txt` or `pyproject.toml`.
- Move large report/archive files to release assets or external storage.
- Add sample datasets or a documented dataset download step.
- Standardize test execution through `pytest`.
- Add screenshots of the Streamlit and Flask interfaces.
- Add GitHub Actions for automated validation.
