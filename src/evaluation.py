"""How I split my data for training and testing.

The same lifter often appears at lots of meets, so I always split by lifter. That way
the model is never tested on someone it has already seen during training.
"""
from sklearn.model_selection import GroupShuffleSplit, StratifiedGroupKFold

# I use the same seed everywhere so my splits come out the same every time I run them.
SEED = 4101


def split_by_lifter(table):
    """Put 80% of lifters in train and 20% in test. Every row for a lifter goes to the
    same side."""
    splitter = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=SEED)
    train_rows, test_rows = next(splitter.split(table, groups=table.Name))
    return (table.iloc[train_rows].reset_index(drop=True),
            table.iloc[test_rows].reset_index(drop=True))


def make_cv():
    """5 folds for comparing methods on the training set. Each fold keeps lifters together
    and has roughly the same success rate."""
    return StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=SEED)
