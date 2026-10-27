"""My cleaning rules for the audit cohort, applied in order.

Run it from the project folder after the audit:  python -m src.clean

It reads the cohort the audit wrote to data/interim/, applies my rules, and prints how
many rows each rule affected. Only those counts are saved, to reports/cleaning_summary.json,
never any names or rows.
"""
import json

import pandas as pd

from .audit import IDENTITY_MEET_KEY
from .paths import INTERIM, REPORTS


def clean(cohort):
    """Apply my cleaning rules in order. Give back the cleaned rows and how many rows
    each rule affected."""
    counts = {'start_rows': len(cohort)}

    # Rule 1: if the same person appears more than once at the same meet, I can't tell
    # which entry is right, so I remove all of them.
    repeated = cohort.duplicated(subset=IDENTITY_MEET_KEY, keep=False)
    counts['removed_repeated_identity_meet'] = int(repeated.sum())
    cohort = cohort.loc[~repeated]

    # Rule 2: a third attempt over 450 kg is far beyond any raw record, so it probably is a
    # data-entry error. (minus sign = missed lift; I only want the weight here)
    heavy = pd.to_numeric(cohort.Deadlift3Kg).abs().gt(450)
    counts['removed_third_attempt_above_450kg'] = int(heavy.sum())
    cohort = cohort.loc[~heavy]

    # Rule 3: lifters under 10 are nearly all real youth lifters, so I keep them.
    # I still count them so my summary shows I checked.
    age = pd.to_numeric(cohort.Age, errors='coerce')
    counts['kept_age_below_10'] = int(age.lt(10).sum())

    # Rule 4: very light lifters are children, and the one very heavy lifter is
    # plausible, so I keep them too. Again I only count them.
    bodyweight = pd.to_numeric(cohort.BodyweightKg)
    counts['kept_bodyweight_below_30_or_above_250'] = int((bodyweight.lt(30) | bodyweight.gt(250)).sum())

    counts['final_rows'] = len(cohort)
    return cohort, counts


if __name__ == '__main__':
    cohort = pd.read_csv(INTERIM / 'audit_cohort.csv.gz', dtype=str, keep_default_na=False)
    cleaned, counts = clean(cohort)
    # Success means the third deadlift is positive (a miss is stored as a negative number).
    success = pd.to_numeric(cleaned.Deadlift3Kg).gt(0)
    counts['success'] = int(success.sum())
    counts['success_pct'] = 100 * success.mean()
    (REPORTS / 'cleaning_summary.json').write_text(json.dumps(counts, indent=2), encoding='utf-8')
    print(json.dumps(counts, indent=2))
