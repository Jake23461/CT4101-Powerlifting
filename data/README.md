# Data

This project uses one frozen snapshot of the OpenPowerlifting IPF-affiliate bulk CSV.
The data files are not in this repository: the ZIP is 68 MB, and the CSV contains
lifters' names. To be confirmed how to send the Zipped data, since downloading newest version may contain updated data

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
