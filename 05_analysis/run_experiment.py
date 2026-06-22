from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
import time
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "05_analysis" / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from mia_eval.attacks import extract_many
from mia_eval.data import DEFAULT_RANDOM_STATE, prepare_datasets
from mia_eval.experiments import run_metric_tables
from mia_eval.models import ALL_DATASETS, ALL_MODELS, CORE_DATASETS, CORE_MODELS, train_many
from mia_eval.subsampling import DEFAULT_SAMPLE_SIZES, run_subsampling


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def parse_sample_sizes(values: list[str]) -> tuple[int, ...]:
    return tuple(int(value) for value in values)


def result_paths(project_root: Path, run_name: str) -> dict[str, Any]:
    run_root = project_root / "05_analysis" / "results" / run_name
    return {
        "run_root": run_root,
        "model_subdir": f"{run_name}/models",
        "attack_score_subdir": f"{run_name}/attack_scores",
        "metrics_dir": run_root / "metrics",
        "subsampling_dir": run_root / "subsampling",
        "run_config": run_root / "run_config.json",
        "run_summary": run_root / "run_summary.md",
    }


def run_summary_text(config: dict[str, Any], timings: dict[str, float]) -> str:
    lines = [
        "# Experiment Run Summary",
        "",
        f"Generated: {config['generated_at']}",
        "",
        "## Run",
        "",
        f"- Run name: `{config['run_name']}`",
        f"- Datasets: `{config['datasets']}`",
        f"- Models: `{config['models']}`",
        f"- Prepare data: `{config['prepare_data']}`",
        f"- Model subdir: `{config['model_subdir']}`",
        f"- Attack-score subdir: `{config['attack_score_subdir']}`",
        f"- Metrics dir: `{config['metrics_dir']}`",
        f"- Subsampling dir: `{config['subsampling_dir']}`",
        "",
        "## Key Settings",
        "",
        f"- Random state: `{config['random_state']}`",
        f"- Max train samples: `{config['max_train_samples']}`",
        f"- Random forest estimators: `{config['n_estimators']}`",
        f"- Bootstrap repeats: `{config['n_bootstrap']}`",
        f"- Subsampling repeats: `{config['n_repeats']}`",
        f"- Sample sizes: `{config['sample_sizes']}`",
        "",
        "## Stage Timings",
        "",
        "| Stage | Seconds |",
        "| --- | ---: |",
    ]
    for stage, seconds in timings.items():
        lines.append(f"| {stage} | {seconds:.2f} |")
    lines.extend(
        [
            "",
            "## Outputs",
            "",
            f"- Metric table: `{config['metrics_dir']}/main_metrics.csv`",
            f"- Confidence intervals: `{config['metrics_dir']}/confidence_intervals.csv`",
            f"- Sample-size sensitivity: `{config['subsampling_dir']}/sample_size_sensitivity.csv`",
            f"- Per-repeat subsampling records: `{config['subsampling_dir']}/sample_size_repeats.csv`",
            "",
            "## Notes",
            "",
            "- This runner orchestrates existing modules; it does not change raw data.",
            "- Low-FPR metrics use tie-aware randomized threshold handling.",
            "- Subsampling reuses the same sampled rows across attack scores within each dataset/model/sample-size/repeat.",
        ]
    )
    return "\n".join(lines) + "\n"


def timed(stage: str, timings: dict[str, float], fn: Any) -> Any:
    start = time.perf_counter()
    result = fn()
    timings[stage] = time.perf_counter() - start
    return result


def run_pipeline(args: argparse.Namespace) -> dict[str, Any]:
    project_root = args.project_root.resolve()
    paths = result_paths(project_root, args.run_name)
    paths["run_root"].mkdir(parents=True, exist_ok=True)

    datasets = list(args.datasets)
    models = list(args.models)
    sample_sizes = parse_sample_sizes(args.sample_sizes)
    timings: dict[str, float] = {}

    if args.prepare_data:
        timed(
            "prepare_data",
            timings,
            lambda: prepare_datasets(
                project_root,
                dataset_names=tuple(datasets),
                random_state=args.random_state,
            ),
        )

    if not args.skip_train:
        timed(
            "train_models",
            timings,
            lambda: train_many(
                project_root,
                datasets=datasets,
                models=models,
                output_subdir=paths["model_subdir"],
                random_state=args.random_state,
                n_estimators=args.n_estimators,
                n_jobs=args.n_jobs,
                max_iter=args.max_iter,
                max_train_samples=args.max_train_samples,
            ),
        )

    if not args.skip_scores:
        timed(
            "extract_attack_scores",
            timings,
            lambda: extract_many(
                project_root,
                datasets=datasets,
                models=models,
                model_subdir=paths["model_subdir"],
                output_subdir=paths["attack_score_subdir"],
                batch_size=args.batch_size,
            ),
        )

    if not args.skip_metrics:
        timed(
            "metric_tables",
            timings,
            lambda: run_metric_tables(
                project_root,
                datasets=datasets,
                models=models,
                attack_score_subdir=paths["attack_score_subdir"],
                output_dir=paths["metrics_dir"],
                n_bootstrap=args.n_bootstrap,
                confidence=args.confidence,
                random_state=args.random_state,
            ),
        )

    if not args.skip_subsampling:
        timed(
            "subsampling",
            timings,
            lambda: run_subsampling(
                project_root,
                datasets=datasets,
                models=models,
                attack_score_subdir=paths["attack_score_subdir"],
                output_dir=paths["subsampling_dir"],
                sample_sizes=sample_sizes,
                n_repeats=args.n_repeats,
                random_state=args.random_state,
            ),
        )

    generated_at = dt.datetime.now().astimezone().isoformat(timespec="seconds")
    config = {
        "generated_at": generated_at,
        "run_name": args.run_name,
        "project_root": str(project_root),
        "datasets": datasets,
        "models": models,
        "prepare_data": args.prepare_data,
        "skip_train": args.skip_train,
        "skip_scores": args.skip_scores,
        "skip_metrics": args.skip_metrics,
        "skip_subsampling": args.skip_subsampling,
        "model_subdir": paths["model_subdir"],
        "attack_score_subdir": paths["attack_score_subdir"],
        "metrics_dir": str(paths["metrics_dir"].relative_to(project_root)),
        "subsampling_dir": str(paths["subsampling_dir"].relative_to(project_root)),
        "random_state": args.random_state,
        "max_train_samples": args.max_train_samples,
        "n_estimators": args.n_estimators,
        "n_jobs": args.n_jobs,
        "max_iter": args.max_iter,
        "batch_size": args.batch_size,
        "n_bootstrap": args.n_bootstrap,
        "confidence": args.confidence,
        "n_repeats": args.n_repeats,
        "sample_sizes": list(sample_sizes),
        "timings_seconds": timings,
    }

    write_json(paths["run_config"], config)
    paths["run_summary"].write_text(run_summary_text(config, timings), encoding="utf-8")
    return config


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the MIA evaluation pipeline end to end.")
    parser.add_argument("--project-root", type=Path, default=PROJECT_ROOT)
    parser.add_argument("--run-name", default="core")
    parser.add_argument("--datasets", nargs="+", default=list(CORE_DATASETS), choices=list(ALL_DATASETS))
    parser.add_argument("--models", nargs="+", default=list(CORE_MODELS), choices=list(ALL_MODELS))
    parser.add_argument("--prepare-data", action="store_true")
    parser.add_argument("--skip-train", action="store_true")
    parser.add_argument("--skip-scores", action="store_true")
    parser.add_argument("--skip-metrics", action="store_true")
    parser.add_argument("--skip-subsampling", action="store_true")
    parser.add_argument("--random-state", type=int, default=DEFAULT_RANDOM_STATE)
    parser.add_argument("--max-train-samples", type=int)
    parser.add_argument("--n-estimators", type=int, default=200)
    parser.add_argument("--n-jobs", type=int, default=-1)
    parser.add_argument("--max-iter", type=int, default=1000)
    parser.add_argument("--batch-size", type=int, default=50000)
    parser.add_argument("--n-bootstrap", type=int, default=1000)
    parser.add_argument("--confidence", type=float, default=0.95)
    parser.add_argument("--n-repeats", type=int, default=200)
    parser.add_argument("--sample-sizes", nargs="+", default=[str(value) for value in DEFAULT_SAMPLE_SIZES])
    return parser.parse_args()


def main() -> None:
    config = run_pipeline(parse_args())
    print(f"run_name={config['run_name']}")
    print(f"metrics={config['metrics_dir']}/main_metrics.csv")
    print(f"subsampling={config['subsampling_dir']}/sample_size_sensitivity.csv")


if __name__ == "__main__":
    main()
