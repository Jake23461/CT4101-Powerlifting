# CT4101-Powerlifting
CT4101 machine learning project investigating whether a powerlifter’s third deadlift attempt will succeed, using athlete information and earlier attempts from the OpenPowerlifting IPF-affiliate dataset.

Repository: https://github.com/Jake23461/CT4101-Powerlifting

Report: reports/report.pdf

Video: ill add once ive the video finished

## Results

- My final model is gradient boosting (learning rate 0.05, 31 leaves per tree, minimum leaf size 200), with the threshold left at 0.50.
- On the test set it got 0.6220 balanced accuracy. The second-attempt rule got 0.5557.
- The test score was very close to the cross-validated score on the training set (0.6216), so I think the CV numbers I used to choose it were honest.
- A random forest scored about the same, so I can't say gradient boosting is clearly better than it.

## Running it from a fresh clone

Everything below is run from the repository root. I used Python 3.13 (see `requirements.txt`).

### 1. Set up the environment

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

This installs pandas, NumPy, scikit-learn, matplotlib (for the figures in notebooks 04 and 05) and Jupyter.

On Windows, if PowerShell says running scripts is disabled, run
`Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` first and then activate again.

Also on Windows, clone the repository into a short folder path (for example on your Desktop). In a very deep folder, `pip install` can fail with a "No such file or directory" error, because some of Jupyter's files end up past Windows' 260-character path limit.

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
| `notebooks/04_models.ipynb` | Tunes logistic regression and a decision tree, compares them with the baselines, and saves `reports/model_results.csv`, `reports/error_analysis.csv` and the figures in `reports/figures/` | about 3 minutes |
| `notebooks/05_final.ipynb` | Tunes a random forest and gradient boosting, picks the final model and threshold, then scores everything once on the test set and checks the final model by group and by year | about 8 minutes (tuning the random forest alone took about 4) |

The very first time scikit-learn is imported after installing it can take a few extra
minutes on Windows. After that the times above apply.

## Layout

```text
data/README.md      where the data comes from and where to put it
src/                reusable code (file paths, audit, cleaning, features, evaluation, baselines, models)
notebooks/          the notebooks, run in order 01, 02, 03, 04, 05
reports/            aggregate results only, with no names or row-level data
reports/figures/    the PNG figures saved by notebooks 04 and 05
ASSISTANCE.md       how I used AI tools and other help
```

The results files in `reports/` that come from the notebooks:

| File | What's in it | Made by |
|---|---|---|
| `baseline_results.csv` | CV scores for the two baselines | 03 |
| `model_results.csv` | CV scores for the baselines, logistic regression and the decision tree | 04 |
| `error_analysis.csv` | where the decision tree does badly, by group | 04 |
| `final_cv_results.csv` | CV scores for every model, including the random forest and gradient boosting | 05 |
| `test_results.csv` | test set scores for every model | 05 |
| `test_by_group.csv` | the final model's test scores by sex and age band | 05 |
| `test_by_year.csv` | the final model's test scores by meet year | 05 |

The figures in `reports/figures/`:

| Figure | Made by |
|---|---|
| `confusion_matrix.png`, `roc_curves.png`, `tree_feature_importance.png`, `lr_coefficients.png` | 04 |
| `threshold.png`, `test_confusion_matrix.png`, `test_roc_curves.png`, `permutation_importance.png` | 05 |
