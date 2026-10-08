# CT4101-Powerlifting
CT4101 machine learning project investigating whether a powerlifter’s third deadlift attempt will succeed, using athlete information and earlier attempts from the OpenPowerlifting IPF-affiliate dataset.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Then get the dataset by following [data/README.md](data/README.md).

## Reproduce the data audit

Run from the repository root:

```bash
python -m src.audit
```

It checks the data file is the right one, applies the filters, removes duplicates and
writes the results to `reports/`. It takes around a minute.

## Layout

```text
data/README.md      where the data comes from and where to put it
src/                reusable code (file paths and the audit)
reports/            aggregate results only, with no names or row-level data
```
