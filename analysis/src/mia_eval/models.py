from __future__ import annotations

import argparse
import datetime as dt
import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import joblib
import numpy as np
from sklearn.ensemble import ExtraTreesClassifier, HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, log_loss
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from mia_eval.data import DEFAULT_RANDOM_STATE, EXPANDED_DATASETS, default_project_root


CORE_DATASETS = ("credit_default", "covertype")
ALL_DATASETS = EXPANDED_DATASETS
CORE_MODELS = ("logistic_regression", "random_forest")
ALL_MODELS = (*CORE_MODELS, "hist_gradient_boosting", "extra_trees", "small_mlp")


@dataclass(frozen=True)
class CleanSplit:
    dataset_name: str
    X: np.ndarray
    y: np.ndarray
    member_idx: np.ndarray
    nonmember_idx: np.ndarray
    metadata: dict[str, Any]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_clean_split(project_root: Path, dataset_name: str) -> CleanSplit:
    dataset_dir = project_root / "data_processed" / dataset_name
    data_path = dataset_dir / "cleaned_dataset.npz"
    split_path = dataset_dir / "member_nonmember_split.npz"
    metadata_path = dataset_dir / "metadata.json"

    if not data_path.exists():
        raise FileNotFoundError(f"Missing cleaned dataset: {data_path}")
    if not split_path.exists():
        raise FileNotFoundError(f"Missing member/non-member split: {split_path}")
    if not metadata_path.exists():
        raise FileNotFoundError(f"Missing dataset metadata: {metadata_path}")

    data = np.load(data_path)
    split = np.load(split_path)
    return CleanSplit(
        dataset_name=dataset_name,
        X=data["X"],
        y=data["y"],
        member_idx=split["member_idx"],
        nonmember_idx=split["nonmember_idx"],
        metadata=read_json(metadata_path),
    )


def build_model(
    model_name: str,
    *,
    random_state: int = DEFAULT_RANDOM_STATE,
    n_estimators: int = 200,
    n_jobs: int = -1,
    max_iter: int = 1000,
) -> Any:
    if model_name == "logistic_regression":
        return Pipeline(
            steps=[
                ("scaler", StandardScaler()),
                (
                    "classifier",
                    LogisticRegression(
                        max_iter=max_iter,
                        random_state=random_state,
                    ),
                ),
            ]
        )

    if model_name == "random_forest":
        return RandomForestClassifier(
            n_estimators=n_estimators,
            random_state=random_state,
            n_jobs=n_jobs,
        )

    if model_name == "hist_gradient_boosting":
        return HistGradientBoostingClassifier(
            max_iter=min(max_iter, 200),
            random_state=random_state,
        )

    if model_name == "extra_trees":
        return ExtraTreesClassifier(
            n_estimators=n_estimators,
            random_state=random_state,
            n_jobs=n_jobs,
        )

    if model_name == "small_mlp":
        return Pipeline(
            steps=[
                ("scaler", StandardScaler()),
                (
                    "classifier",
                    MLPClassifier(
                        hidden_layer_sizes=(64,),
                        alpha=1e-4,
                        learning_rate_init=1e-3,
                        max_iter=min(max_iter, 200),
                        early_stopping=True,
                        n_iter_no_change=10,
                        random_state=random_state,
                    ),
                ),
            ]
        )

    known = ", ".join(ALL_MODELS)
    raise ValueError(f"Unknown model {model_name!r}. Known models: {known}")


def model_config(
    model_name: str,
    *,
    random_state: int,
    n_estimators: int,
    n_jobs: int,
    max_iter: int,
) -> dict[str, Any]:
    if model_name == "logistic_regression":
        return {
            "pipeline": "StandardScaler -> LogisticRegression",
            "max_iter": max_iter,
            "random_state": random_state,
        }
    if model_name == "random_forest":
        return {
            "estimator": "RandomForestClassifier",
            "n_estimators": n_estimators,
            "n_jobs": n_jobs,
            "random_state": random_state,
        }
    if model_name == "hist_gradient_boosting":
        return {
            "estimator": "HistGradientBoostingClassifier",
            "max_iter": min(max_iter, 200),
            "random_state": random_state,
        }
    if model_name == "extra_trees":
        return {
            "estimator": "ExtraTreesClassifier",
            "n_estimators": n_estimators,
            "n_jobs": n_jobs,
            "random_state": random_state,
        }
    if model_name == "small_mlp":
        return {
            "pipeline": "StandardScaler -> MLPClassifier",
            "hidden_layer_sizes": [64],
            "alpha": 1e-4,
            "learning_rate_init": 1e-3,
            "max_iter": min(max_iter, 200),
            "early_stopping": True,
            "n_iter_no_change": 10,
            "random_state": random_state,
        }
    raise ValueError(f"Unknown model {model_name!r}")


def limit_training_indices(
    indices: np.ndarray,
    y: np.ndarray,
    *,
    max_train_samples: int | None,
    random_state: int,
) -> np.ndarray:
    if max_train_samples is None or max_train_samples >= len(indices):
        return indices
    if max_train_samples <= 0:
        raise ValueError("max_train_samples must be positive")

    limited, _ = train_test_split(
        indices,
        train_size=max_train_samples,
        random_state=random_state,
        stratify=y[indices],
    )
    return np.asarray(limited, dtype=np.int64)


def predict_proba_for_labels(model: Any, X: np.ndarray, labels: np.ndarray) -> np.ndarray:
    probabilities = model.predict_proba(X)
    model_classes = np.asarray(model.classes_)
    if np.array_equal(model_classes, labels):
        return probabilities

    aligned = np.zeros((len(X), len(labels)), dtype=float)
    label_positions = {label: pos for pos, label in enumerate(labels)}
    for source_pos, label in enumerate(model_classes):
        aligned[:, label_positions[label]] = probabilities[:, source_pos]
    return aligned


def evaluate_classifier(
    model: Any,
    X: np.ndarray,
    y: np.ndarray,
    *,
    labels: np.ndarray,
) -> dict[str, float]:
    probabilities = predict_proba_for_labels(model, X, labels)
    predictions = labels[np.argmax(probabilities, axis=1)]
    return {
        "accuracy": float(accuracy_score(y, predictions)),
        "log_loss": float(log_loss(y, probabilities, labels=labels)),
    }


def train_target_model(
    split: CleanSplit,
    model_name: str,
    project_root: Path,
    *,
    output_subdir: str = "models",
    random_state: int = DEFAULT_RANDOM_STATE,
    n_estimators: int = 200,
    n_jobs: int = -1,
    max_iter: int = 1000,
    max_train_samples: int | None = None,
) -> dict[str, Any]:
    train_idx = limit_training_indices(
        split.member_idx,
        split.y,
        max_train_samples=max_train_samples,
        random_state=random_state,
    )
    nonmember_idx = split.nonmember_idx
    labels = np.unique(split.y)

    model = build_model(
        model_name,
        random_state=random_state,
        n_estimators=n_estimators,
        n_jobs=n_jobs,
        max_iter=max_iter,
    )

    started = time.perf_counter()
    model.fit(split.X[train_idx], split.y[train_idx])
    fit_seconds = time.perf_counter() - started

    train_eval = evaluate_classifier(model, split.X[train_idx], split.y[train_idx], labels=labels)
    nonmember_eval = evaluate_classifier(model, split.X[nonmember_idx], split.y[nonmember_idx], labels=labels)

    output_dir = project_root / "analysis" / "results" / output_subdir / split.dataset_name / model_name
    output_dir.mkdir(parents=True, exist_ok=True)

    model_path = output_dir / "model.joblib"
    indices_path = output_dir / "training_indices.npz"
    metadata_path = output_dir / "metadata.json"

    joblib.dump(model, model_path)
    np.savez_compressed(indices_path, train_idx=train_idx, nonmember_idx=nonmember_idx)

    generated_at = dt.datetime.now().astimezone().isoformat(timespec="seconds")
    metadata = {
        "dataset": split.dataset_name,
        "model": model_name,
        "model_config": model_config(
            model_name,
            random_state=random_state,
            n_estimators=n_estimators,
            n_jobs=n_jobs,
            max_iter=max_iter,
        ),
        "dataset_metadata_path": str(
            (project_root / "data_processed" / split.dataset_name / "metadata.json").relative_to(project_root)
        ),
        "model_path": str(model_path.relative_to(project_root)),
        "indices_path": str(indices_path.relative_to(project_root)),
        "n_rows": int(split.X.shape[0]),
        "n_features": int(split.X.shape[1]),
        "member_pool_size": int(len(split.member_idx)),
        "nonmember_pool_size": int(len(nonmember_idx)),
        "train_size": int(len(train_idx)),
        "max_train_samples": max_train_samples,
        "labels": [int(label) for label in labels],
        "fit_seconds": float(fit_seconds),
        "train_accuracy": train_eval["accuracy"],
        "train_log_loss": train_eval["log_loss"],
        "nonmember_accuracy": nonmember_eval["accuracy"],
        "nonmember_log_loss": nonmember_eval["log_loss"],
        "random_state": random_state,
        "generated_at": generated_at,
    }
    write_json(metadata_path, metadata)
    return metadata


def train_many(
    project_root: Path,
    *,
    datasets: list[str],
    models: list[str],
    output_subdir: str = "models",
    random_state: int = DEFAULT_RANDOM_STATE,
    n_estimators: int = 200,
    n_jobs: int = -1,
    max_iter: int = 1000,
    max_train_samples: int | None = None,
) -> list[dict[str, Any]]:
    summaries: list[dict[str, Any]] = []
    for dataset_name in datasets:
        split = load_clean_split(project_root, dataset_name)
        for model_name in models:
            summaries.append(
                train_target_model(
                    split,
                    model_name,
                    project_root,
                    output_subdir=output_subdir,
                    random_state=random_state,
                    n_estimators=n_estimators,
                    n_jobs=n_jobs,
                    max_iter=max_iter,
                    max_train_samples=max_train_samples,
                )
            )
    return summaries


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train target models for MIA experiments.")
    parser.add_argument("--project-root", type=Path, default=default_project_root())
    parser.add_argument("--datasets", nargs="+", default=list(CORE_DATASETS), choices=list(ALL_DATASETS))
    parser.add_argument("--models", nargs="+", default=list(CORE_MODELS), choices=list(ALL_MODELS))
    parser.add_argument("--output-subdir", default="models")
    parser.add_argument("--random-state", type=int, default=DEFAULT_RANDOM_STATE)
    parser.add_argument("--n-estimators", type=int, default=200)
    parser.add_argument("--n-jobs", type=int, default=-1)
    parser.add_argument("--max-iter", type=int, default=1000)
    parser.add_argument("--max-train-samples", type=int)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    summaries = train_many(
        args.project_root.resolve(),
        datasets=args.datasets,
        models=args.models,
        output_subdir=args.output_subdir,
        random_state=args.random_state,
        n_estimators=args.n_estimators,
        n_jobs=args.n_jobs,
        max_iter=args.max_iter,
        max_train_samples=args.max_train_samples,
    )
    for item in summaries:
        print(
            f"{item['dataset']} / {item['model']}: "
            f"train_acc={item['train_accuracy']:.4f}, "
            f"nonmember_acc={item['nonmember_accuracy']:.4f}, "
            f"fit_seconds={item['fit_seconds']:.2f}, "
            f"train_size={item['train_size']}"
        )


if __name__ == "__main__":
    main()
