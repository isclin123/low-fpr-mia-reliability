from __future__ import annotations

import argparse
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "analysis" / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from mia_eval.attacks import SCORE_NAMES
from mia_eval.audit_tool import AuditToolConfig, run_audit
from mia_eval.data import DEFAULT_RANDOM_STATE
from mia_eval.experiments import FPR_LEVELS
from mia_eval.subsampling import DEFAULT_SAMPLE_SIZES


def parse_float_tuple(values: list[str]) -> tuple[float, ...]:
    return tuple(float(value) for value in values)


def parse_int_tuple(values: list[str]) -> tuple[int, ...]:
    return tuple(int(value) for value in values)


def resolve_path(path: Path, project_root: Path) -> Path:
    if path.is_absolute():
        return path
    return project_root / path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run reusable MIA score-array audit outputs.")
    parser.add_argument("--project-root", type=Path, default=PROJECT_ROOT)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--input-format", choices=["npz", "csv"], required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--score-names", nargs="+", default=list(SCORE_NAMES))
    parser.add_argument("--dataset", default="")
    parser.add_argument("--model", default="")
    parser.add_argument("--fpr-levels", nargs="+", default=[str(value) for value in FPR_LEVELS])
    parser.add_argument("--n-bootstrap", type=int, default=1000)
    parser.add_argument("--confidence", type=float, default=0.95)
    parser.add_argument("--n-repeats", type=int, default=200)
    parser.add_argument("--sample-sizes", nargs="+", default=[str(value) for value in DEFAULT_SAMPLE_SIZES])
    parser.add_argument("--random-state", type=int, default=DEFAULT_RANDOM_STATE)
    parser.add_argument("--membership-column", default="membership")
    parser.add_argument("--sample-id-column", default="sample_id")
    parser.add_argument("--skip-figures", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    project_root = args.project_root.resolve()
    config = AuditToolConfig(
        input_path=resolve_path(args.input, project_root),
        input_format=args.input_format,
        output_dir=resolve_path(args.output_dir, project_root),
        score_names=tuple(args.score_names),
        dataset=args.dataset,
        model=args.model,
        fpr_levels=parse_float_tuple(args.fpr_levels),
        n_bootstrap=args.n_bootstrap,
        confidence=args.confidence,
        n_repeats=args.n_repeats,
        sample_sizes=parse_int_tuple(args.sample_sizes),
        random_state=args.random_state,
        membership_column=args.membership_column,
        sample_id_column=args.sample_id_column,
        make_figures=not args.skip_figures,
    )
    payload = run_audit(config)
    print(f"wrote {payload['outputs']['run_summary']}")
    print(f"main_metrics={payload['outputs']['main_metrics']}")
    print(f"fixed_threshold_intervals={payload['outputs']['fixed_threshold_intervals']}")


if __name__ == "__main__":
    main()
