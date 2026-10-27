"""Turn my cleaned rows into the table I'll train models on.

Run it from the project folder after the audit:  python -m src.features

Every attempt column in the data is signed: a negative number means a missed lift,
and the size of the number is the weight chosen. I split that into the weight and
whether the lift was made.
"""
import pandas as pd

from .clean import clean
from .paths import INTERIM

# The 11 columns my models are allowed to use. Everything here is known before the
# third deadlift happens.
FEATURES = ['Sex', 'Age', 'BodyweightKg',
            'deadlift1_kg', 'deadlift2_kg', 'deadlift3_kg',
            'deadlift1_made', 'deadlift2_made',
            'jump_kg', 'jump_pct', 'load_per_bodyweight']

# These are only known after the lift (or are the answer itself), so they'd give the
# result away. They must never be inputs.
FORBIDDEN = {'Deadlift3Kg', 'Deadlift4Kg', 'Best3DeadliftKg', 'TotalKg', 'Place',
             'Dots', 'Wilks', 'Glossbrenner', 'Goodlift', 'made'}


def build_features(cleaned):
    """Build my modelling table from the cleaned rows."""
    attempts = {i: pd.to_numeric(cleaned[f'Deadlift{i}Kg']) for i in (1, 2, 3)}
    table = pd.DataFrame({
        'Sex': cleaned.Sex,
        'Age': pd.to_numeric(cleaned.Age, errors='coerce'),  # blank age becomes missing
        'BodyweightKg': pd.to_numeric(cleaned.BodyweightKg),
        # minus sign = missed lift; here I only want the weight
        'deadlift1_kg': attempts[1].abs(),
        'deadlift2_kg': attempts[2].abs(),
        'deadlift3_kg': attempts[3].abs(),
        'deadlift1_made': attempts[1].gt(0).astype(int),
        'deadlift2_made': attempts[2].gt(0).astype(int),
    })
    table['jump_kg'] = table.deadlift3_kg - table.deadlift2_kg
    table['jump_pct'] = 100 * table.jump_kg / table.deadlift2_kg
    table['load_per_bodyweight'] = table.deadlift3_kg / table.BodyweightKg
    # What I'm predicting: was the third deadlift made?
    table['made'] = attempts[3].gt(0).astype(int)
    # I only keep Name to keep each lifter on one side of the train/test split, and
    # Date for a later check over time. Neither is ever an input.
    table['Name'] = cleaned.Name
    table['Date'] = cleaned.Date
    return table


def check_no_leakage(X):
    """Stop if any column that would give the answer away (or Name or Date) is in X."""
    bad = sorted(set(X.columns) & (FORBIDDEN | {'Name', 'Date'}))
    if bad:
        raise ValueError(f'These columns must not be model inputs: {bad}')


if __name__ == '__main__':
    cohort = pd.read_csv(INTERIM / 'audit_cohort.csv.gz', dtype=str, keep_default_na=False)
    cleaned, _ = clean(cohort)
    table = build_features(cleaned)
    check_no_leakage(table[FEATURES])
    print('shape:', table.shape)
    print('\nmissing values per column:')
    print(table.isna().sum().to_string())
    print(f'\nsuccess rate: {100 * table.made.mean():.2f}%')
