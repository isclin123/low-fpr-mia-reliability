from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = PROJECT_ROOT / "05_analysis" / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from mia_eval.attacks import SCORE_NAMES
from mia_eval.data import DEFAULT_RANDOM_STATE


DEFAULT_SOURCE = PROJECT_ROOT / "05_analysis/results/core/attack_scores/credit_default/random_forest/attack_scores.npz"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "05_analysis/examples"


def make_examples(
    *,
    source: Path,
    output_dir: Path,
    sample_size: int,
    random_state: int,
) -> dict[str, Path]:
    arrays = np.load(source)
    rng = np.random.default_rng(random_state)

    member_pool_size = len(arrays[f"member_{SCORE_NAMES[0]}"])
    nonmember_pool_size = len(arrays[f"nonmember_{SCORE_NAMES[0]}"])
    n = min(sample_size, member_pool_size, nonmember_pool_size)
    member_idx = rng.choice(member_pool_size, size=n, replace=False)
    nonmember_idx = rng.choice(nonmember_pool_size, size=n, replace=False)

    output_dir.mkdir(parents=True, exist_ok=True)
    npz_path = output_dir / "example_scores.npz"
    csv_path = output_dir / "example_scores.csv"

    payload: dict[str, np.ndarray] = {}
    for score_name in SCORE_NAMES:
        payload[f"member_{score_name}"] = arrays[f"member_{score_name}"][member_idx]
        payload[f"nonmember_{score_name}"] = arrays[f"nonmember_{score_name}"][nonmember_idx]
    np.savez_compressed(npz_path, **payload)

    rows: list[dict[str, object]] = []
    for local_idx, source_idx in enumerate(member_idx):
        row: dict[str, object] = {
            "sample_id": f"member_{int(source_idx)}",
            "membership": 1,
            "dataset": "credit_default",
            "model": "random_forest",
        }
        for score_name in SCORE_NAMES:
            row[score_name] = float(arrays[f"member_{score_name}"][source_idx])
        rows.append(row)
    for local_idx, source_idx in enumerate(nonmember_idx):
        row = {
            "sample_id": f"nonmember_{int(source_idx)}",
            "membership": 0,
            "dataset": "credit_default",
            "model": "random_forest",
        }
        for score_name in SCORE_NAMES:
            row[score_name] = float(arrays[f"nonmember_{score_name}"][source_idx])
        rows.append(row)
    pd.DataFrame(rows).to_csv(csv_path, index=False)

    return {"npz": npz_path, "csv": csv_path}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create small reusable audit-tool example score files.")
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--sample-size", type=int, default=1000)
    parser.add_argument("--random-state", type=int, default=DEFAULT_RANDOM_STATE)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    paths = make_examples(
        source=args.source.resolve(),
        output_dir=args.output_dir.resolve(),
        sample_size=args.sample_size,
        random_state=args.random_state,
    )
    for label, path in paths.items():
        print(f"{label}: {path}")


if __name__ == "__main__":
    main()
