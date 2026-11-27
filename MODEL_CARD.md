# Model card: third deadlift attempt predictor

This model predicts whether a powerlifter's third deadlift attempt will be made, using
things that are known before the lift happens. All the numbers here come from the files
in `reports/` and the outputs of `notebooks/05_final.ipynb`.

## Model details

| | |
|---|---|
| Model | `HistGradientBoostingClassifier` from scikit-learn |
| Settings | learning rate 0.05, 31 leaves per tree (`max_leaf_nodes=31`), minimum leaf size 200 |
| Class weights | `class_weight='balanced'` |
| Threshold | 0.50 (a lift is called made if its probability is at least 0.50) |
| Preprocessing | missing numbers filled with the training median (only Age has any), numbers scaled, Sex one-hot encoded |
| Inputs | the 11 columns in `FEATURES` in `src/features.py` (listed in [data/README.md](data/README.md#data-statement)) |
| Output | 1 = third deadlift made, 0 = missed |
| scikit-learn | 1.9.1 (from `requirements.txt`, with Python 3.13) |
| Seed | 4101 (`SEED` in `src/evaluation.py`), used for the split, the folds and the model |
| Code | `make_gradient_boosting` in `src/models.py`, final fit in section 5 of `notebooks/05_final.ipynb` |

I picked the settings with a grid search over 8 combinations (learning rate 0.05 or 0.1,
31 or 63 leaves, minimum leaf size 50 or 200) on 5 folds of the training set, keeping
the one with the highest mean balanced accuracy. All eight landed between 0.6209 and
0.6216, so the settings made very little difference. I set `class_weight='balanced'`
because 61% of lifts are made, and without it the model leans towards always guessing
"made". I kept the threshold at 0.50 because it had the best out-of-fold balanced
accuracy (0.6216) of the thresholds I tried.

## Intended use

- A second opinion for a coach or lifter choosing a third deadlift, in IPF raw full
  meets. The person still makes the call.
- A way to study patterns across many lifters, for example how the size of the jump
  relates to making the lift.
- It isn't for judging individual lifters, team selection or betting.

## Out-of-scope uses

- Lifts outside what I trained on: equipped lifting, meets that weren't full squat,
  bench and deadlift meets, and federations that aren't IPF affiliates. I never tested
  the model on any of these.
- Predicting future meets. My split is by lifter, not by time, so I haven't tested
  whether it holds up on meets newer than the ones it learned from.
- Reading the output as a real chance of making the lift. On the test set the
  probabilities are too low in every bin (see Calibration).
- Making decisions about a lifter on its own. It's wrong a lot (balanced accuracy
  0.6220), and it catches far fewer of women's misses than men's.
- Lifters in the Mx category. There were only 4 Mx rows in the training set and 1 in
  the test set, so I have no idea how it does for them.

## Training and evaluation data

The data is the OpenPowerlifting IPF-affiliate snapshot `openipf-2026-10-03`. The full
details, filters and cleaning rules are in the data statement in
[data/README.md](data/README.md#data-statement).

After cleaning there are 461,828 lifts. I split them 80/20 by lifter with
`GroupShuffleSplit`, so every row for a lifter goes to the same side and the model is
never tested on someone it has seen in training.

| | Rows | Lifters | Third attempts made |
|---|---:|---:|---:|
| Train | 369,880 | 145,781 | 61.02% |
| Test | 91,948 | 36,446 | 60.69% |

I made every choice (model, settings, threshold) using 5 folds of the training set
(`StratifiedGroupKFold`, also grouped by lifter). I only used the test set once, at the
end, after everything was chosen.

## Metrics

Balanced accuracy is my main score, because a model can get a decent plain accuracy just
by guessing "made" every time. CV numbers are the mean (std) over the 5 folds.

| Model | CV balanced accuracy | Test balanced accuracy | CV ROC-AUC | Test ROC-AUC | CV miss recall | Test miss recall |
|---|---:|---:|---:|---:|---:|---:|
| Gradient boosting (final) | 0.6216 (0.0011) | 0.6220 | 0.6701 (0.0020) | 0.6706 | 0.6068 (0.0024) | 0.6076 |
| Second-attempt rule | 0.5553 (0.0010) | 0.5557 | 0.5553 (0.0010) | 0.5557 | 0.1792 (0.0022) | 0.1791 |
| Always made | 0.5000 (0.0000) | 0.5000 | 0.5000 (0.0000) | 0.5000 | 0.0000 (0.0000) | 0.0000 |

The second-attempt rule says a lifter will miss their third if they missed their second.
It only ever gives a probability of 0 or 1, which is why its ROC-AUC is the same as its
balanced accuracy.

The test score is within 0.0004 of the CV score, which is smaller than the fold std, so
I think the CV numbers were honest. On the test set the model caught 21,960 of the 36,145
missed lifts, but it also wrongly called 20,285 of the 55,803 made lifts a miss. Its
plain accuracy (0.6251) is lower than the rule's (0.6362) for that reason. The random
forest was tied with it (0.6206 in CV, 0.6222 on test), and all the scores for every
model are in `reports/final_cv_results.csv` and `reports/test_results.csv`.

## Calibration

| | Brier score |
|---|---:|
| Gradient boosting | 0.227 |
| Always guessing the training make rate (61%) | 0.239 |

On the test set the average predicted probability is 0.509, but 0.607 of the lifts were
actually made. I split the test predictions into 10 equal-size bins
(`reports/test_calibration.csv`), and in every bin more lifts were made than predicted.
The gap (share made minus mean predicted) goes from 0.074 to 0.109. So the order of the
probabilities is fine, since the share made goes up with every bin, but the numbers
themselves are about 0.1 too low. My guess is this comes from
`class_weight='balanced'`, which makes misses count for more in training, but I haven't
tested that. The plot is `reports/figures/calibration.png`.

## Results by group

Test set, from `reports/test_by_group.csv`. I left out any group with fewer than 30 test
rows, which only affected Mx (1 row).

| Group | Rows | Made | Balanced accuracy | Miss recall | Make recall |
|---|---:|---:|---:|---:|---:|
| All rows | 91,948 | 60.69% | 0.6220 | 0.6076 | 0.6365 |
| Women | 31,136 | 65.75% | 0.5996 | 0.4074 | 0.7919 |
| Men | 60,811 | 58.10% | 0.6189 | 0.6913 | 0.5464 |
| Age under 18 | 9,262 | 62.88% | 0.6258 | 0.4997 | 0.7519 |
| Age 18-23 | 27,343 | 58.89% | 0.6176 | 0.6684 | 0.5669 |
| Age 24-39 | 29,159 | 59.17% | 0.6198 | 0.6505 | 0.5891 |
| Age 40+ | 11,733 | 63.10% | 0.6079 | 0.5313 | 0.6845 |
| Age missing | 14,451 | 63.80% | 0.6241 | 0.5129 | 0.7352 |

The biggest gap is between women and men. The model catches 40.7% of women's missed lifts
against 69.1% of men's. Women make more of their third attempts, so the model leans
towards calling their lifts made. Under-18s, over-40s and lifters with no age show the
same pattern. The decision tree's CV error analysis in notebook 04 had the same gap, so
it isn't just a quirk of this model or the test set.

## Limitations

- It's still wrong a lot. Balanced accuracy is 0.6220, and it wrongly called 20,285
  made lifts a miss on the test set.
- It works worse for women than for men, and the part it's worse at is catching the
  misses, which is the useful part of a warning.
- The probabilities are about 0.1 too low (see Calibration).
- The inputs don't include anything about a lifter's earlier meets, or how their squat
  and bench went on the day.
- The split is by lifter, not by time, so this isn't a test of predicting future meets.
  Balanced accuracy was steady across meet years (0.6184 to 0.6236 in
  `reports/test_by_year.csv`), but the model could have learned from meets in the same
  years it was tested on.
- Sex is the 3rd most important input by permutation importance, and I haven't tried a
  version without it.
- Gradient boosting is made of many trees, so it's harder to explain than the single
  decision tree, which was close behind (0.6183 on the test set).
- Age is missing for 15.9% of lifts (73,444 of 462,489 in the audit), and the model
  fills it with the training median.

## Monitoring if piloted

- Run it in shadow mode. The coach sees a recalibrated risk score but makes every call,
  and I log each prediction next to the result.
- Watch for changes in the inputs, like new federations, new weight classes or rule
  changes.
- Track performance as results come in, separately for women and men and by age band,
  not just overall.
- Look out for concept drift. If coaches start picking more conservative thirds, the
  link between jump size and success could change.
- Retraining is a reviewed decision, never automatic.

## Recommendation

- Don't deploy it as a decision tool. At most, run a supervised pilot like the one above.
- Why: about 1 in 3 safe attempts gets a false alarm (20,285 of 55,803 made lifts on the
  test set), a warning is right about half the time (precision on misses 0.5198), it
  catches 41% of women's misses against 69% of men's, and the raw scores are about 0.1
  too low.
- What would change my mind: adding lifter-history or same-day features that raise
  balanced accuracy clearly above 0.62 while closing the gap between women and men.
