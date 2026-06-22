from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
from pathlib import Path
from typing import Any

import joblib
import numpy as np

from mia_eval.data import DEFAULT_RANDOM_STATE, default_project_root
from mia_eval.models import ALL_DATASETS, ALL_MODELS, CORE_DATASETS, CORE_MODELS, load_clean_split, predict_proba_for_labels


SCORE_NAMES = ("neg_loss", "confidence", "neg_entropy", "modified_entropy")
EPS = 1e-12


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def label_positions(labels: np.ndarray) -> dict[int, int]:
    return {int(label): position for position, label in enumerate(labels)}


def true_class_probabilities(probabilities: np.ndarray, y: np.ndarray, labels: np.ndarray) -> np.ndarray:
    positions = label_positions(labels)
    cols = np.asarray([positions[int(label)] for label in y], dtype=np.int64)
    return probabilities[np.arange(len(y)), cols]


def modified_prediction_entropy(probabilities: np.ndarray, y: np.ndarray, labels: np.ndarray) -> np.ndarray:
    """Compute label-aware modified prediction entropy from MIA literature."""
    clipped = np.clip(np.asarray(probabilities, dtype=np.float64), EPS, 1.0 - EPS)
    positions = label_positions(labels)
    target_cols = np.asarray([positions[int(label)] for label in y], dtype=np.int64)

    target_probs = clipped[np.arange(len(y)), target_cols]
    entropy = -(1.0 - target_probs) * np.log(target_probs)

    all_terms = clipped * np.log(1.0 - clipped)
    all_terms[np.arange(len(y)), target_cols] = 0.0
    entropy -= np.sum(all_terms, axis=1)
    return entropy


def compute_attack_scores(probabilities: np.ndarray, y: np.ndarray, labels: np.ndarray) -> dict[str, np.ndarray]:
    probabilities = np.asarray(probabilities, dtype=np.float64)
    clipped = np.clip(probabilities, EPS, 1.0)
    true_probs = np.clip(true_class_probabilities(clipped, y, labels), EPS, 1.0)

    per_sample_loss = -np.log(true_probs)
    entropy = -np.sum(clipped * np.log(clipped), axis=1)
    modified_entropy = modified_prediction_entropy(probabilities, y, labels)

    return {
        "neg_loss": -per_sample_loss,
        "confidence": np.max(probabilities, axis=1),
        "neg_entropy": -entropy,
        # Larger is more member-like; this is negative modified prediction entropy.
        "modified_entropy": -modified_entropy,
    }


def predict_scores_batched(
    model: Any,
    X: np.ndarray,
    y: np.ndarray,
    labels: np.ndarray,
    *,
    batch_size: int = 50000,
) -> dict[str, np.ndarray]:
    chunks: dict[str, list[np.ndarray]] = {name: [] for name in SCORE_NAMES}

    for start in range(0, len(y), batch_size):
        stop = min(start + batch_size, len(y))
        probabilities = predict_proba_for_labels(model, X[start:stop], labels)
        batch_scores = compute_attack_scores(probabilities, y[start:stop], labels)
        for name in SCORE_NAMES:
            if not np.all(np.isfinite(batch_scores[name])):
                raise ValueError(f"Non-finite values produced for attack score {name}")
            chunks[name].append(batch_scores[name].astype(np.float32, copy=False))

    return {name: np.concatenate(parts) for name, parts in chunks.items()}


def score_summary_rows(scores: dict[str, np.ndarray], group: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for name, values in scores.items():
        rows.append(
            {
                "group": group,
                "score": name,
                "n": int(len(values)),
                "mean": float(np.mean(values)),
                "std": float(np.std(values, ddof=1)) if len(values) > 1 else 0.0,
                "min": float(np.min(values)),
                "p25": float(np.quantile(values, 0.25)),
                "median": float(np.quantile(values, 0.5)),
                "p75": float(np.quantile(values, 0.75)),
                "max": float(np.max(values)),
            }
        )
    return rows


def write_score_summary(path: Path, rows: list[dict[str, Any]]) -> None:
    fieldnames = ["group", "score", "n", "mean", "std", "min", "p25", "median", "p75", "max"]
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def extract_attack_scores(
    project_root: Path,
    *,
    dataset_name: str,
    model_name: str,
    model_subdir: str = "models",
    output_subdir: str = "attack_scores",
    batch_size: int = 50000,
) -> dict[str, Any]:
    split = load_clean_split(project_root, dataset_name)
    model_dir = project_root / "05_analysis" / "results" / model_subdir / dataset_name / model_name
    model_path = model_dir / "model.joblib"
    indices_path = model_dir / "training_indices.npz"
    model_metadata_path = model_dir / "metadata.json"

    if not model_path.exists():
        raise FileNotFoundError(f"Missing model artifact: {model_path}")
    if not indices_path.exists():
        raise FileNotFoundError(f"Missing training indices: {indices_path}")
    if not model_metadata_path.exists():
        raise FileNotFoundError(f"Missing model metadata: {model_metadata_path}")

    model = joblib.load(model_path)
    model_metadata = read_json(model_metadata_path)
    indices = np.load(indices_path)
    member_idx = indices["train_idx"]
    nonmember_idx = indices["nonmember_idx"]
    labels = np.asarray(model_metadata["labels"], dtype=np.int64)

    member_scores = predict_scores_batched(
        model,
        split.X[member_idx],
        split.y[member_idx],
        labels,
        batch_size=batch_size,
    )
    nonmember_scores = predict_scores_batched(
        model,
        split.X[nonmember_idx],
        split.y[nonmember_idx],
        labels,
        batch_size=batch_size,
    )

    output_dir = project_root / "05_analysis" / "results" / output_subdir / dataset_name / model_name
    output_dir.mkdir(parents=True, exist_ok=True)

    score_path = output_dir / "attack_scores.npz"
    metadata_path = output_dir / "metadata.json"
    summary_path = output_dir / "score_summary.csv"

    payload: dict[str, np.ndarray] = {
        "member_idx": member_idx.astype(np.int64, copy=False),
        "nonmember_idx": nonmember_idx.astype(np.int64, copy=False),
    }
    for name in SCORE_NAMES:
        payload[f"member_{name}"] = member_scores[name]
        payload[f"nonmember_{name}"] = nonmember_scores[name]
    np.savez_compressed(score_path, **payload)

    summary_rows = score_summary_rows(member_scores, "member") + score_summary_rows(nonmember_scores, "nonmember")
    write_score_summary(summary_path, summary_rows)

    generated_at = dt.datetime.now().astimezone().isoformat(timespec="seconds")
    metadata = {
        "dataset": dataset_name,
        "model": model_name,
        "model_subdir": model_subdir,
        "model_metadata_path": str(model_metadata_path.relative_to(project_root)),
        "score_path": str(score_path.relative_to(project_root)),
        "summary_path": str(summary_path.relative_to(project_root)),
        "member_count": int(len(member_idx)),
        "nonmember_count": int(len(nonmember_idx)),
        "scores": {
            "neg_loss": "Negative per-sample cross-entropy loss; larger means more member-like.",
            "confidence": "Maximum predicted class probability; larger means more member-like.",
            "neg_entropy": "Negative prediction entropy; larger means sharper and more member-like.",
            "modified_entropy": "Negative label-aware modified prediction entropy; larger means more member-like.",
        },
        "batch_size": batch_size,
        "random_state": DEFAULT_RANDOM_STATE,
        "generated_at": generated_at,
    }
    write_json(metadata_path, metadata)
    return metadata


def extract_many(
    project_root: Path,
    *,
    datasets: list[str],
    models: list[str],
    model_subdir: str = "models",
    output_subdir: str = "attack_scores",
    batch_size: int = 50000,
) -> list[dict[str, Any]]:
    summaries: list[dict[str, Any]] = []
    for dataset_name in datasets:
        for model_name in models:
            summaries.append(
                extract_attack_scores(
                    project_root,
                    dataset_name=dataset_name,
                    model_name=model_name,
                    model_subdir=model_subdir,
                    output_subdir=output_subdir,
                    batch_size=batch_size,
                )
            )
    return summaries


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Extract member/non-member attack scores from target models.")
    parser.add_argument("--project-root", type=Path, default=default_project_root())
    parser.add_argument("--datasets", nargs="+", default=list(CORE_DATASETS), choices=list(ALL_DATASETS))
    parser.add_argument("--models", nargs="+", default=list(CORE_MODELS), choices=list(ALL_MODELS))
    parser.add_argument("--model-subdir", default="models")
    parser.add_argument("--output-subdir", default="attack_scores")
    parser.add_argument("--batch-size", type=int, default=50000)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    summaries = extract_many(
        args.project_root.resolve(),
        datasets=args.datasets,
        models=args.models,
        model_subdir=args.model_subdir,
        output_subdir=args.output_subdir,
        batch_size=args.batch_size,
    )
    for item in summaries:
        print(
            f"{item['dataset']} / {item['model']}: "
            f"{item['member_count']} member scores, "
            f"{item['nonmember_count']} non-member scores -> {item['score_path']}"
        )


if __name__ == "__main__":
    main()
