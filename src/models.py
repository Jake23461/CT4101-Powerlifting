"""My real models and the code I use to tune them. Logistic regression and the decision
tree are from Milestone 3. The random forest and gradient boosting are for the final
portfolio.

They all start with the same preprocessor as my baselines, so the only thing that
changes between them is the model at the end.
"""
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GridSearchCV
from sklearn.pipeline import Pipeline
from sklearn.tree import DecisionTreeClassifier

from .baselines import SCORING, make_preprocessor
from .evaluation import SEED, make_cv

# Why class_weight='balanced': 61% of lifts are made, and balanced accuracy is my main
# score. Without it, the model leans towards always guessing "made", because that's
# right most of the time. 'balanced' makes each missed lift count for more during
# training, so missing a miss costs the model as much as missing a make.


def make_logistic_regression(C=1.0):
    """Logistic regression after my usual preprocessing. A smaller C means the model is
    held back more and keeps its weights smaller."""
    return Pipeline([('prep', make_preprocessor()),
                     ('model', LogisticRegression(C=C, class_weight='balanced',
                                                  max_iter=1000))])


def make_decision_tree(max_depth=None, min_samples_leaf=1):
    """A decision tree after my usual preprocessing. A tree doesn't need scaling, but I
    keep the same preprocessor so both models get exactly the same inputs."""
    return Pipeline([('prep', make_preprocessor()),
                     ('model', DecisionTreeClassifier(class_weight='balanced',
                                                      random_state=SEED,
                                                      max_depth=max_depth,
                                                      min_samples_leaf=min_samples_leaf))])


def make_random_forest(max_depth=None, min_samples_leaf=1):
    """A random forest after my usual preprocessing. It averages many trees, each grown
    on a different random sample of rows and inputs, so its answers vary less than a
    single tree's do."""
    return Pipeline([('prep', make_preprocessor()),
                     ('model', RandomForestClassifier(n_estimators=100,
                                                      class_weight='balanced',
                                                      random_state=SEED, n_jobs=-1,
                                                      max_depth=max_depth,
                                                      min_samples_leaf=min_samples_leaf))])


def make_gradient_boosting(learning_rate=0.1, max_leaf_nodes=31, min_samples_leaf=20):
    """Gradient boosting after my usual preprocessing. It builds trees one after another,
    and each new tree tries to fix the mistakes of the ones before it. A smaller
    learning_rate means each tree changes the answer less."""
    return Pipeline([('prep', make_preprocessor()),
                     ('model', HistGradientBoostingClassifier(class_weight='balanced',
                                                              random_state=SEED,
                                                              learning_rate=learning_rate,
                                                              max_leaf_nodes=max_leaf_nodes,
                                                              min_samples_leaf=min_samples_leaf))])


# The settings I try for each model. For the tree, a shallower depth or a bigger
# minimum leaf size stops it from just memorising the training rows.
LR_GRID = {'model__C': [0.01, 0.1, 1, 10]}
TREE_GRID = {'model__max_depth': [3, 5, 8, 12],
             'model__min_samples_leaf': [1, 50, 200]}
# I keep the two ensemble grids small on purpose. Each setting gets fitted 5 times, once
# for each fold of my roughly 370,000 training rows.
RF_GRID = {'model__max_depth': [10, 15], 'model__min_samples_leaf': [50, 200]}
GB_GRID = {'model__learning_rate': [0.05, 0.1], 'model__max_leaf_nodes': [31, 63],
           'model__min_samples_leaf': [50, 200]}


def tune(pipeline, grid, X, y, groups):
    """Try every setting in the grid on my 5 folds and keep the one with the best
    balanced accuracy. I pass the lifter names as groups so a lifter never ends up on
    both sides of a fold. It returns the fitted search."""
    search = GridSearchCV(pipeline, grid, cv=make_cv(), scoring=SCORING,
                          refit='balanced_accuracy', n_jobs=-1)
    search.fit(X, y, groups=groups)
    return search
