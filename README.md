# CT4101-Powerlifting
CT4101 machine learning project investigating whether a powerlifter’s third deadlift attempt will succeed, using athlete information and earlier attempts from the OpenPowerlifting IPF-affiliate dataset.

Repository: https://github.com/Jake23461/CT4101-Powerlifting

## Running it from a fresh clone

Everything below is run from the repository root. I used Python 3.13 (see `requirements.txt`).

### 1. Set up the environment

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

On Windows, if PowerShell says running scripts is disabled, run
`Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` first and then activate again.

### 2. Get the data

Download `openipf-latest.zip` from the link in [data/README.md](data/README.md) and put it in `data/raw/` without unzipping it. [data/README.md](data/README.md)
explains where it comes from and which exact snapshot I used.

### 3. Run the data audit

```bash
python -m src.audit
```

It checks the data file is the right one, applies the filters, removes duplicates and
writes the results to `reports/`. The row-level files it writes go in `data/interim/`,
which the notebooks need. It takes around a minute.

### 4. Run the notebooks

Open the notebooks in VS Code or Jupyter, pick the `.venv` kernel, and run each one top
to bottom in this order:

| Notebook | What it does | Roughly how long |
|---|---|---|
| `notebooks/01_data.ipynb` | Checks the data, runs the audit again, cleans the data and builds the model inputs | a couple of minutes (it reruns the audit) |
| `notebooks/02_evaluation_design.ipynb` | Splits the data by lifter and sets up the 5 folds | under a minute |
| `notebooks/03_baselines.ipynb` | Scores the two baselines and saves `reports/baseline_results.csv` | about a minute |

The very first time scikit-learn is imported after installing it can take a few extra
minutes on Windows. After that the times above apply.

## Layout

```text
data/README.md      where the data comes from and where to put it
src/                reusable code (file paths, audit, cleaning, features, evaluation, baselines)
notebooks/          the notebooks, run in order 01, 02, 03
reports/            aggregate results only, with no names or row-level data
ASSISTANCE.md       how I used AI tools and other help
```
