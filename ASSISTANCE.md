# Assistance declaration

## Generative AI and coding assistants

- **Claude (claude.ai):** I used it to set up a plan for the project, to help keep on top of things week by week. explain concepts I was unsure about (leakage, grouped splits, pipelines, the metrics), check my results against an independent rerun, and review my working notes for mistakes.  It also suggested the cleaning rules after looking at the flagged rows, and I reviewed and accepted them.

## Claude Code (in VS Code)

I used Claude Code as a coding assistant throughout the project and to help draft explainitory texts. I defined the project myself: the question (predicting third deadlift success), the data cohort and filters, the evaluation design, which models to compare and how to judge them. I used Claude Code mainly to implement code to my specifications, catch errors, and run checks.

**Milestones 1 to 3.** I wrote and ran notebooks 01 to 04 and made the design decisions in
them: the filtering and cleaning rules (after reviewing the flagged rows), the 11 input
features and the leakage check, the 80/20 split by lifter with 5 stratified group folds,
balanced accuracy as the main metric, the two baselines, and tuning logistic regression and a
decision tree with class_weight='balanced'. Claude Code helped me write and debug the code in
src/, spot errors, and rewrite some of my code comments and reports/data_audit.md in plainer
English.

**Final portfolio.** I planned the final stage and set the design before any results came in:
- adding a random forest and gradient boosting, with small grids chosen to keep the cost of
  5-fold tuning on about 370,000 training rows manageable
- choosing the final model by highest mean CV balanced accuracy, and checking whether the gap
  to the next model was bigger than the fold standard deviation
- choosing the threshold from out-of-fold probabilities on the training set only
- using the test set once, at the end, with the final choice written down beforehand
- the follow-up analyses: permutation importance, performance by sex and age band, and
  performance by meet year

Claude Code implemented the two ensemble pipelines in src/models.py to these specifications, I wrote up the notebook, and used claude code to correct any mistakes made and run the notebook to catch any errors. I reviewed the results and revised where I disagreed or something was missing. For example, I had it frame separate
thresholds for women and men as a fairness question rather than a simple fix, propose
testing a model without Sex as an input, and drop groups under 30 rows from the subgroup
table. It also helped to verify its reproducibility by doing clean rerun from a fresh clone, which gave
identical numbers in reports/. I then reran the audit and all five notebooks myself, checked the numbers against the outputs.

## External code

No code was copied from other sources. The project uses these open-source libraries, listed in `requirements.txt`: pandas, NumPy, scikit-learn and Jupyter.

## Collaboration

None. I did not work with other students on this project.
