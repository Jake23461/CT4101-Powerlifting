"""My first pass over the dataset: I filter it down to the lifts I can use, remove
duplicates, and work out some summary numbers.

Run it from the project folder:  python -m src.audit

It first checks I've got the right data file, then reads it straight from the ZIP
without changing anything. I read every column as text so a blank cell stays blank,
and I only treat a blank as "missing". I don't filter on age, sex, date, federation,
placing or TotalKg yet.

The summary numbers go in reports/. The row-level files have lifters' names in them,
so they go in data/interim/, which git ignores.
"""
import datetime
import hashlib
import json
import platform
import zipfile

import numpy as np
import pandas as pd

from .paths import INTERIM, RAW_ZIP, REPORTS

# The download link always gives you the newest version of the data, so I use this
# fingerprint to make sure it's the exact file I worked with (see data/README.md).
# If it's a different file, the audit stops.
ZIP_SHA256 = 'f4b65d165f3677cd6f063469a2ab64458caea3b19161a2c87fcf0574aedbadc7'

ATTEMPTS = ['Deadlift1Kg', 'Deadlift2Kg', 'Deadlift3Kg']

# If two rows match on everything except these columns, it's the same lift listed
# under more than one division (e.g. Open and Junior), so I only keep one of them.
DIVISION_DEPENDENT = ['Division', 'Place', 'AgeClass', 'BirthYearClass', 'WeightClassKg',
                      'Dots', 'Wilks', 'Glossbrenner', 'Goodlift']
# Rows that match on all of these look like the same person at the same meet.
IDENTITY_MEET_KEY = ['Name', 'Sex', 'Federation', 'Date', 'MeetCountry', 'MeetState',
                     'MeetTown', 'MeetName', 'Event', 'Equipment']


def check_snapshot(zip_path):
    """Stop if this isn't the data file I used. Otherwise, give back the name of the CSV inside it."""
    if not zip_path.exists():
        raise FileNotFoundError(f'{zip_path} not found. See data/README.md.')
    digest = hashlib.sha256(zip_path.read_bytes()).hexdigest()
    if digest != ZIP_SHA256:
        raise ValueError(f'{zip_path.name} is not the frozen snapshot (SHA-256 {digest}).')
    with zipfile.ZipFile(zip_path) as archive:
        (member,) = [n for n in archive.namelist() if n.endswith('.csv')]
    return member


def load(zip_path, member):
    """Read the whole CSV out of the ZIP in one go."""
    with zipfile.ZipFile(zip_path) as archive, archive.open(member) as handle:
        data = pd.read_csv(handle, dtype=str, keep_default_na=False)
    columns = list(data.columns)
    # I note each row's line number in the original CSV (the header is line 1),
    # so I can find any row again later.
    data.insert(0, 'source_csv_row', np.arange(2, len(data) + 2))
    return data, columns


def apply_filters(data, counts):
    """Apply my filters one after another and count how many rows are left after each."""
    nums = data[ATTEMPTS + ['BodyweightKg']].apply(pd.to_numeric, errors='coerce')
    steps = [('SBD', data.Event.eq('SBD')),
             ('SBD_Raw', data.Equipment.eq('Raw')),
             ('three_attempts_present', data[ATTEMPTS].ne('').all(axis=1)),
             ('valid_bodyweight', np.isfinite(nums.BodyweightKg) & nums.BodyweightKg.gt(0)),
             ('valid_nonzero_attempts', np.isfinite(nums[ATTEMPTS]).all(axis=1)
                                        & nums[ATTEMPTS].ne(0).all(axis=1))]
    keep = pd.Series(True, index=data.index)
    for label, step in steps:
        keep &= step
        counts[label] = int(keep.sum())
    return data.loc[keep]


def deduplicate(eligible, columns, counts):
    """Remove exact copies first, then lifts listed under more than one division
    (I keep the first one)."""
    exact = eligible.duplicated(subset=columns)
    no_exact = eligible.loc[~exact]
    cross = no_exact.duplicated(subset=[c for c in columns if c not in DIVISION_DEPENDENT])
    final = no_exact.loc[~cross]
    counts['exact_duplicates_removed'] = int(exact.sum())
    counts['cross_division_duplicates_removed'] = int(cross.sum())
    counts['final_unique_recorded_performances'] = len(final)
    return final, eligible.loc[exact], no_exact.loc[cross]


def review_flags(final, counts):
    """Count the rows that look odd and need a closer look. I don't remove anything here.
    I'll decide what to do with them in a later stage"""
    age = pd.to_numeric(final.Age, errors='coerce')
    bodyweight = pd.to_numeric(final.BodyweightKg)
    # minus sign = missed lift; I only want the weight here
    second, third = (pd.to_numeric(final[c]).abs() for c in ['Deadlift2Kg', 'Deadlift3Kg'])
    young, heavy = age.lt(10), third.gt(450)
    odd_bodyweight = bodyweight.lt(30) | bodyweight.gt(250)
    repeated = final.duplicated(subset=IDENTITY_MEET_KEY, keep=False)
    counts.update({
        'age_below_10': int(young.sum()),
        'third_attempt_above_450kg': int(heavy.sum()),
        'bodyweight_below_30_or_above_250': int(odd_bodyweight.sum()),
        'repeated_identity_meet_rows': int(repeated.sum()),
        'repeated_identity_meet_groups': final.loc[repeated].groupby(IDENTITY_MEET_KEY).ngroups,
        'third_attempt_same_load_as_second': int(third.eq(second).sum()),
    })
    return final.loc[repeated], final.loc[young | heavy | odd_bodyweight]


def run(zip_path=RAW_ZIP):
    member = check_snapshot(zip_path)
    data, columns = load(zip_path, member)
    counts = {'raw_rows': len(data)}
    eligible = apply_filters(data, counts)
    final, exact_rows, cross_rows = deduplicate(eligible, columns, counts)
    repeated_rows, flagged_rows = review_flags(final, counts)

    INTERIM.mkdir(parents=True, exist_ok=True)
    final.to_csv(INTERIM / 'audit_cohort.csv.gz', index=False)
    exact_rows.to_csv(INTERIM / 'exact_duplicate_rows.csv.gz', index=False)
    cross_rows.to_csv(INTERIM / 'cross_division_duplicate_rows.csv.gz', index=False)
    repeated_rows.to_csv(INTERIM / 'repeated_identity_meet_rows.csv.gz', index=False)
    flagged_rows.to_csv(INTERIM / 'review_flag_rows.csv.gz', index=False)

    # Success means the third deadlift is positive (a miss is stored as a negative number).
    success = pd.to_numeric(final.Deadlift3Kg).gt(0)
    REPORTS.mkdir(exist_ok=True)
    (final.groupby('Federation')
          .agg(rows=('Name', 'size'), unique_lifters=('Name', 'nunique'),
               date_min=('Date', 'min'), date_max=('Date', 'max'))
          .sort_values('rows', ascending=False)
          .to_csv(REPORTS / 'federations.csv'))
    yearly = success.groupby(final.Date.str[:4].rename('year')).agg(rows='size', successes='sum')
    yearly['success_pct'] = 100 * yearly.successes / yearly.rows
    yearly.to_csv(REPORTS / 'yearly.csv')

    age_missing = int(final.Age.eq('').sum())
    results = {'run_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
               'python': platform.python_version(), 'pandas': pd.__version__, 'numpy': np.__version__,
               'zip_sha256': ZIP_SHA256, 'csv_member': member,
               'counts': counts,
               'final': {'success': int(success.sum()), 'failure': int((~success).sum()),
                         'success_pct': 100 * success.mean(),
                         'unique_lifters': final.Name.nunique(),
                         'federations': final.Federation.nunique(),
                         'date_min': final.Date.min(), 'date_max': final.Date.max(),
                         'age_missing': age_missing, 'age_missing_pct': 100 * age_missing / len(final)}}
    (REPORTS / 'audit_results.json').write_text(json.dumps(results, indent=2), encoding='utf-8')
    return results


if __name__ == '__main__':
    out = run()
    print(json.dumps({k: out[k] for k in ['counts', 'final']}, indent=2))
