"""My baselines: the simplest predictions I can make, so I know what a real model has to beat.

There are two. One always guesses that the lift is made. The other is the rule a coach
would use: if they missed the second attempt, they'll miss the third.
"""
import numpy as np
from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.metrics import f1_score, make_scorer, precision_score, recall_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from .features import FEATURES

# Every input except Sex is a number.
NUMERIC = [f for f in FEATURES if f != 'Sex']

# The scores I report for every model. Balanced accuracy is my main one, because 61% of
# lifts are made, so a model can get a decent plain accuracy just by guessing "made".
# I work out precision, recall and F1 for made (1) and missed (0) separately, so I can
# see how well a model spots the misses. If a model never predicts one of the classes,
# zero_division=0 just gives it a score of 0 instead of a warning.
SCORING = {'balanced_accuracy': 'balanced_accuracy', 'accuracy': 'accuracy',
           'roc_auc': 'roc_auc'}
for name, label in [('made', 1), ('missed', 0)]:
    SCORING[f'precision_{name}'] = make_scorer(precision_score, pos_label=label, zero_division=0)
    SCORING[f'recall_{name}'] = make_scorer(recall_score, pos_label=label, zero_division=0)
    SCORING[f'f1_{name}'] = make_scorer(f1_score, pos_label=label, zero_division=0)


def make_preprocessor():
    """Get the inputs ready for a model. For the numbers I fill a missing value with the
    median (only Age has any) and then scale them. Sex gets one-hot encoded."""
    numeric = Pipeline([('impute', SimpleImputer(strategy='median')),
                        ('scale', StandardScaler())])
    return ColumnTransformer([('numeric', numeric, NUMERIC),
                              ('sex', OneHotEncoder(handle_unknown='ignore'), ['Sex'])])


class SecondAttemptRule(ClassifierMixin, BaseEstimator):
    """The coach's rule: if they missed the second attempt, they'll miss the third.

    It doesn't learn anything. It just copies deadlift2_made, so it needs the raw inputs,
    not the preprocessed ones.
    """

    def fit(self, X, y=None):
        # There's nothing to learn, but scikit-learn needs every model to know its classes.
        self.classes_ = np.array([0, 1])
        return self

    def predict(self, X):
        return X['deadlift2_made'].astype(int).to_numpy()

    def predict_proba(self, X):
        # The rule never has any doubt, so every probability is either 0 or 1. The columns
        # go [missed, made], the same order as classes_.
        made = self.predict(X)
        return np.column_stack([1 - made, made])
