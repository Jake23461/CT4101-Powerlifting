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

## Columns I'm using

I only want to use things that are known before the third deadlift happens.

| Column | Type | Units / values | What it means | Known before the 3rd deadlift? |
|---|---|---|---|---|
| Sex | category | M, F, Mx (only 5 Mx rows) | The sex category the lifter competed in | Yes |
| Age | number | years, often x.5 (approximate) | Age at the meet, missing for 15.9% | Yes |
| BodyweightKg | number | kg | Weigh-in bodyweight | Yes |
| Deadlift1Kg | signed number | kg, negative = missed | First attempt: the size is the weight, the sign is whether they made it | Yes |
| Deadlift2Kg | signed number | kg, negative = missed | Second attempt, stored the same way | Yes |
| Deadlift3Kg | signed number | kg, negative = missed | The weight is announced before the lift, but the sign is the result, so this is what I'm predicting and I never use it as an input | Weight yes, result no |
| Name | text | | I only use this to keep each lifter on one side of the train/test split, never as an input | Not an input |

I never use Deadlift4Kg, Best3DeadliftKg, TotalKg, Place, Dots, Wilks, Glossbrenner or
Goodlift as inputs, because they're only known after the lift, so they'd give the answer away.

Next week I'll build the actual model inputs from these columns: the three attempt weights,
whether attempts 1 and 2 were made, the jump from attempt 2 to 3 (in kg and %), and the
third attempt's weight divided by bodyweight.

## Things that look odd

I haven't removed these yet. I'll decide what to do with them next week.

- 344 rows where the lifter is listed as younger than 10
- 2 third attempts heavier than 450 kg
- 113 bodyweights under 30 kg or over 250 kg
- 329 cases where the same person seems to appear more than once at the same meet (659 rows)

I also noticed 38,058 lifters attempted the same weight on their third attempt as their
second. Every one of them had missed their second attempt, so they were just retrying the same
weight. That's normal, so I kept them.
