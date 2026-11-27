# Changelog

Decisions that changed the project, and why.

## Oct 2026: new data snapshot

I lost the original ZIP from 26 September, and the download link only ever gives the
latest build, so I couldn't get it back. I froze the 3 October build and added a SHA-256
check to the audit so this can't quietly happen again. The final count moved from 461,268
(my Milestone 1 audit) to 462,489. That's a small shift (1,221 rows), but enough that the
numbers wouldn't have matched without a frozen snapshot.

## Oct 2026: split by lifter

Lots of lifters compete at several meets, so a random split would have tested the model
on people it had already seen. I used an 80/20 GroupShuffleSplit by lifter, and grouped
folds inside the training set, so every score is on lifters the model has never met.

## Oct 2026: cleaning rules

I looked at the flagged rows before deciding anything, instead of just dropping
everything odd. I removed the 659 duplicate-person rows and the 2 attempts over 450 kg,
but kept the 344 under-10s and the 113 extreme bodyweights because they turned out to be
real lifters.

## Nov 2026: added ensembles

After Milestone 3 the tree (0.617) and logistic regression (0.611) were close, so I
tried a random forest and gradient boosting to see if combining many trees helped. They
did, but only by about 0.003 to 0.004, which told me the inputs matter more than the model.

## Nov 2026: threshold kept at 0.50

I searched thresholds from 0.30 to 0.70 on out-of-fold training probabilities, and 0.50
was already the best (0.6216). Looking back that makes sense, because the class weighting
had already balanced the classes.

## Nov 2026: gradient boosting over random forest

I fixed my rule (highest CV mean) before tuning, and boosting won 0.6216 to 0.6206, which
is really a tie within the std. On the test set the forest came out 0.0002 ahead, but I
didn't switch, because changing my pick after seeing the test set would have made that
score meaningless.

## Nov 2026: dropped groups under 30 rows

Mx had only 1 test row, so any score for it meant nothing. I left out groups under 30 rows
rather than report numbers that would look more certain than they are.

## Nov 2026: calibration check

The Week 12 slides list calibration, and I hadn't checked it. The probabilities came out
about 0.1 too low (Brier 0.227 against 0.239 for a constant guess), so the recommendation
now says they need recalibrating before a coach sees them.
