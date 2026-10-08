# Data audit

This is a summary of what I found when I first went through the dataset. I used the
OpenPowerlifting IPF snapshot from 3 October 2026 (`openipf-2026-10-03`). All the numbers
here come from running `python -m src.audit`, and the full output is in `audit_results.json`.
While building this I also double-checked the counts with a second, separate script, and
they matched.

## Cleaning the data

I started with every row in the file and kept only the rows I could use. Each step
below applies on top of the ones before it.

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

The second type of duplicate happens when someone enters two divisions at one meet,
for example Open and Junior. It's the same lift, so I only kept it once.

That leaves **462,489 lifts** from 182,281 different lifters across 104 federations,
from 1973 to 2026.

## What I'm predicting

I want to predict whether a lifter's third deadlift is successful. In this dataset a
failed lift is stored as a negative number (for example `-200` means they missed 200 kg),
so a success is simply `Deadlift3Kg > 0`.

| | Lifts | % |
|---|---:|---:|
| Success | 281,925 | 60.96 |
| Failure | 180,564 | 39.04 |

About 61% of third attempts succeed, so a model would need to do better than just
guessing "success" every time.

Age is missing for 73,444 lifts (15.9%), which I'll need to deal with before modelling.

## Things that look odd

I haven't removed these yet. I'll decide what to do with them next week.

- 344 lifters listed as younger than 10
- 2 third attempts heavier than 450 kg
- 113 bodyweights under 30 kg or over 250 kg
- 329 cases where the same person seems to appear more than once at the same meet (659 rows)

I also noticed 38,058 lifters attempted the same weight on their third attempt as their
second. Every one of them had missed their second attempt, so they were just retrying the same
weight. That's normal, so I kept them.
