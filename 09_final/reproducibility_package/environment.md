# Environment

Date: 2026-06-03

## Python

Observed local runtime:

```text
Python 3.13.5
```

## Requirements File

Install the project analysis dependencies with:

```bash
python3 -m pip install -r 05_analysis/requirements.txt
```

For public-release smoke reproduction, use the pinned lock file:

```bash
python3 -m pip install -r 05_analysis/requirements-lock.txt
```

Current `05_analysis/requirements.txt`:

```text
numpy
pandas
scipy
scikit-learn
matplotlib
seaborn
tqdm
joblib
xlrd
```

## Observed Package Versions

The current workspace was validated with:

| Package | Observed version |
|---|---|
| numpy | 2.1.3 |
| pandas | 2.2.3 |
| scikit-learn | 1.6.1 |
| scipy | 1.15.3 |
| matplotlib | 3.10.0 |
| seaborn | 0.13.2 |
| joblib | 1.4.2 |
| xlrd | 2.0.2 |

## Import Path

Most commands insert `05_analysis/src` automatically. For interactive use, set:

```bash
export PYTHONPATH="$PWD/05_analysis/src:$PYTHONPATH"
```

## Pinned Release Lock

The fast audit-tool reporting path has been validated in a fresh virtual environment installed from `05_analysis/requirements-lock.txt`. See `09_final/reproducibility_package/locked_env_smoke.md`.

Remaining boundary: the pinned lock validates the audit-tool smoke path, not a full expanded-grid rerun on every platform. A container recipe remains optional for stronger cross-platform archival reproducibility.
