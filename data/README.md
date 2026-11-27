# Data

This project uses one frozen snapshot of the OpenPowerlifting IPF-affiliate bulk CSV.
The data files are not in this repository: the ZIP is 68 MB, and the CSV contains
lifters' names. The download link now gives a newer build, so it won't match this snapshot. The exact ZIP I used can be downloaded here: https://nuigalwayie-my.sharepoint.com/:u:/g/personal/j_hanrahan7_universityofgalway_ie/IQAdJl654gp4T4vHqMiGUVp9Abp4D0mbNmF04CCdPcFTUxs?e=nUg0B5


## Source

| | |
|---|---|
| Publisher | OpenPowerlifting, https://www.openpowerlifting.org |
| Download URL | https://openpowerlifting.gitlab.io/opl-csv/files/openipf-latest.zip |
| Documentation | https://openpowerlifting.gitlab.io/opl-csv/bulk-csv-docs.html |
| Licence | Public domain (see `LICENSE.txt` inside the ZIP) |
| Snapshot | `openipf-2026-10-03`, revision `199bb416` (ZIP build date 3 October 2026) |
| Downloaded | 4 October 2026 |
| ZIP file | `openipf-latest.zip`, 68,045,630 bytes |
| ZIP SHA-256 | `f4b65d165f3677cd6f063469a2ab64458caea3b19161a2c87fcf0574aedbadc7` |
| CSV member | `openipf-2026-10-03/openipf-2026-10-03-199bb416.csv` (329,304,523 bytes) |

The download URL always serves the latest build, so downloading it again later
will give a different file. The audit checks the ZIP's SHA-256 first and stops if it
doesn't match.

## Setup

Put the ZIP at `data/raw/openipf-latest.zip`. Don't unzip it, because the code reads it directly.

## Folders (all ignored by git)

- `data/raw/`: the untouched ZIP.
- `data/interim/`: row-level files the audit writes, such as the cohort and the duplicate and review lists. They contain names, so they stay local.

Aggregate results (counts and percentages only) go in `reports/` and are committed.

## Attribution

This project uses data from the OpenPowerlifting project, https://www.openpowerlifting.org.

## Data statement

### Source and licence

The data comes from OpenPowerlifting's IPF-affiliate bulk CSV, which is public domain
(see `LICENSE.txt` inside the ZIP). I use one frozen snapshot, `openipf-2026-10-03`
(revision `199bb416`). Before doing anything else, `python -m src.audit` checks that the
ZIP's SHA-256 is
`f4b65d165f3677cd6f063469a2ab64458caea3b19161a2c87fcf0574aedbadc7` and stops if it
isn't, so every count below comes from exactly that file.

### Filters

Each filter applies on top of the ones before it. The counts are from
`reports/audit_results.json`.

| Step | Rows left |
|---|---:|
| Everything in the file | 1,529,372 |
| Full meets only (squat, bench and deadlift) | 1,135,955 |
| Raw lifting only (no supportive equipment) | 624,937 |
| All three deadlift attempts recorded | 481,386 |
| Bodyweight recorded | 481,248 |
| Attempts are proper numbers (not zero or blank) | 481,248 |
| Removed exact duplicate rows (196) | 481,052 |
| Removed lifts listed twice under different divisions (18,563) | 462,489 |

That leaves 462,489 lifts from 182,281 lifters across 104 federations, with meet dates
from 9 November 1973 to 27 September 2026.

### Cleaning rules

After the audit I applied these rules in order with `python -m src.clean`. The counts are
from `reports/cleaning_summary.json`, and my reasons are in
`reports/cleaning_decisions.md`.

| Rule | Rows | What I did |
|---|---:|---|
| Same person at the same meet more than once (329 cases) | 659 | Removed |
| Third attempt over 450 kg | 2 | Removed |
| Age under 10 | 344 | Kept |
| Bodyweight under 30 kg or over 250 kg | 113 | Kept |

That leaves 461,828 lifts, and 60.96% of third attempts are made. I also checked the
38,058 lifts where the third attempt was the same weight as the second. Every one of
those lifters had missed their second attempt and was retrying it, so I kept them.

### Input variables

The models use these 11 inputs (`FEATURES` in `src/features.py`). All of them are known
before the third deadlift happens.

| Input | What it is |
|---|---|
| `Sex` | the sex category the lifter competed in (M, F or Mx) |
| `Age` | age at the meet, in years |
| `BodyweightKg` | weigh-in bodyweight |
| `deadlift1_kg` | weight of the first deadlift attempt |
| `deadlift2_kg` | weight of the second deadlift attempt |
| `deadlift3_kg` | weight of the third deadlift attempt |
| `deadlift1_made` | 1 if the first attempt was made, 0 if missed |
| `deadlift2_made` | 1 if the second attempt was made, 0 if missed |
| `jump_kg` | third attempt weight minus second attempt weight |
| `jump_pct` | that jump as a percentage of the second attempt |
| `load_per_bodyweight` | third attempt weight divided by bodyweight |

What I'm predicting is whether the third deadlift was made (`Deadlift3Kg > 0`). Columns
that are only known after the lift, like `Deadlift4Kg`, `Best3DeadliftKg`, `TotalKg`,
`Place`, `Dots`, `Wilks`, `Glossbrenner` and `Goodlift`, are never inputs, and
`check_no_leakage` in `src/features.py` stops if any of them get in.

### Known gaps

- It only covers IPF-affiliate federations, raw lifting and full squat, bench and
  deadlift meets. Equipped lifting and other federations aren't in it.
- Age is missing for 73,444 lifts (15.9%).
- Lifters' names are public in the data, but I only use `Name` to keep each lifter on
  one side of the train/test split. It's never a model input, and the row-level files
  that contain names stay in `data/interim/`, which git ignores.
- There's no lifter history. Each row is one lift at one meet, and the inputs don't say
  anything about the lifter's earlier meets.
- Mx is very rare. The audit found only 5 Mx rows.
