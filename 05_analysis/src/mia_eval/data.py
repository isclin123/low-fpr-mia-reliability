from __future__ import annotations

import argparse
import datetime as dt
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.datasets import fetch_covtype
from sklearn.model_selection import train_test_split


DEFAULT_RANDOM_STATE = 20260602
DEFAULT_TEST_SIZE = 0.5
CORE_DATASETS = ("credit_default", "covertype")
EXPANDED_DATASETS = (*CORE_DATASETS, "adult_income", "bank_marketing", "diabetes_readmission")


ADULT_COLUMNS = [
    "age",
    "workclass",
    "fnlwgt",
    "education",
    "education_num",
    "marital_status",
    "occupation",
    "relationship",
    "race",
    "sex",
    "capital_gain",
    "capital_loss",
    "hours_per_week",
    "native_country",
    "income",
]


@dataclass(frozen=True)
class CleanDataset:
    name: str
    X: np.ndarray
    y: np.ndarray
    feature_names: list[str]
    target_name: str
    task_type: str
    raw_path: Path
    description: str


def default_project_root() -> Path:
    return Path(__file__).resolve().parents[3]


def normalize_categorical(series: pd.Series) -> pd.Series:
    normalized = series.astype(str).str.strip()
    return normalized.replace(
        {
            "?": "Unknown",
            "": "Unknown",
            "nan": "Unknown",
            "None": "Unknown",
        }
    )


def encode_mixed_tabular_frame(
    frame: pd.DataFrame,
    *,
    numeric_columns: list[str],
    categorical_columns: list[str],
    max_categories_by_column: dict[str, int] | None = None,
) -> tuple[np.ndarray, list[str]]:
    """Convert a mixed numeric/categorical table into a dense float32 matrix."""
    encoded_parts: list[pd.DataFrame] = []

    if numeric_columns:
        numeric_frame = frame[numeric_columns].apply(pd.to_numeric, errors="coerce")
        numeric_frame = numeric_frame.fillna(numeric_frame.median(numeric_only=True)).fillna(0.0)
        encoded_parts.append(numeric_frame.astype(np.float32))

    if categorical_columns:
        categorical_frame = pd.DataFrame(index=frame.index)
        max_categories_by_column = max_categories_by_column or {}
        for column in categorical_columns:
            values = normalize_categorical(frame[column])
            max_categories = max_categories_by_column.get(column)
            if max_categories is not None and values.nunique(dropna=False) > max_categories:
                top_values = set(values.value_counts(dropna=False).nlargest(max_categories).index)
                values = values.where(values.isin(top_values), "Other")
            categorical_frame[column] = values

        dummies = pd.get_dummies(
            categorical_frame,
            columns=categorical_columns,
            prefix=categorical_columns,
            dtype=np.float32,
        )
        encoded_parts.append(dummies)

    if not encoded_parts:
        raise ValueError("At least one numeric or categorical column is required")

    encoded = pd.concat(encoded_parts, axis=1)
    return encoded.to_numpy(dtype=np.float32, copy=False), [str(column) for column in encoded.columns]


def load_credit_default(project_root: Path) -> CleanDataset:
    """Load the UCI Default of Credit Card Clients raw XLS file."""
    raw_path = project_root / "03_data_raw" / "credit_default" / "default of credit card clients.xls"
    if not raw_path.exists():
        raise FileNotFoundError(f"Missing credit_default raw file: {raw_path}")

    frame = pd.read_excel(raw_path, header=1)
    target_name = "default payment next month"
    if target_name not in frame.columns:
        raise ValueError(f"Expected target column {target_name!r} in {raw_path}")

    feature_frame = frame.drop(columns=["ID", target_name])
    X = feature_frame.apply(pd.to_numeric, errors="raise").to_numpy(dtype=np.float32)
    y = pd.to_numeric(frame[target_name], errors="raise").to_numpy(dtype=np.int64)

    return CleanDataset(
        name="credit_default",
        X=X,
        y=y,
        feature_names=[str(col) for col in feature_frame.columns],
        target_name=target_name,
        task_type="binary_classification",
        raw_path=raw_path,
        description="UCI Default of Credit Card Clients financial tabular dataset.",
    )


def load_covertype(project_root: Path) -> CleanDataset:
    """Load the Forest Covertype raw arrays saved from sklearn fetch_covtype."""
    raw_dir = project_root / "03_data_raw" / "covertype"
    raw_path = raw_dir / "covertype_raw_arrays.npz"

    if not raw_path.exists():
        bunch = fetch_covtype(data_home=raw_dir / "sklearn_cache", download_if_missing=True, as_frame=False)
        np.savez_compressed(raw_path, data=bunch.data, target=bunch.target)

    raw = np.load(raw_path)
    X = raw["data"].astype(np.float32, copy=False)
    y = raw["target"].astype(np.int64, copy=False)

    return CleanDataset(
        name="covertype",
        X=X,
        y=y,
        feature_names=[f"feature_{i:02d}" for i in range(X.shape[1])],
        target_name="cover_type",
        task_type="multiclass_classification",
        raw_path=raw_path,
        description="Forest Covertype large tabular benchmark loaded through sklearn fetch_covtype.",
    )


def load_adult_income(project_root: Path) -> CleanDataset:
    """Load the UCI Adult/Census Income train and test files as one benchmark."""
    raw_dir = project_root / "03_data_raw" / "adult_income"
    train_path = raw_dir / "adult.data"
    test_path = raw_dir / "adult.test"
    if not train_path.exists():
        raise FileNotFoundError(f"Missing Adult train file: {train_path}")
    if not test_path.exists():
        raise FileNotFoundError(f"Missing Adult test file: {test_path}")

    train_frame = pd.read_csv(
        train_path,
        header=None,
        names=ADULT_COLUMNS,
        skipinitialspace=True,
    )
    test_frame = pd.read_csv(
        test_path,
        header=None,
        names=ADULT_COLUMNS,
        skipinitialspace=True,
        comment="|",
    )
    frame = pd.concat([train_frame, test_frame], ignore_index=True)

    target_name = "income"
    target = frame[target_name].astype(str).str.strip().str.rstrip(".")
    y = (target == ">50K").astype(np.int64).to_numpy()

    numeric_columns = [
        "age",
        "fnlwgt",
        "education_num",
        "capital_gain",
        "capital_loss",
        "hours_per_week",
    ]
    categorical_columns = [column for column in ADULT_COLUMNS if column not in numeric_columns + [target_name]]
    X, feature_names = encode_mixed_tabular_frame(
        frame.drop(columns=[target_name]),
        numeric_columns=numeric_columns,
        categorical_columns=categorical_columns,
    )

    return CleanDataset(
        name="adult_income",
        X=X,
        y=y,
        feature_names=feature_names,
        target_name=target_name,
        task_type="binary_classification",
        raw_path=raw_dir / "adult.zip",
        description=(
            "UCI Adult/Census Income tabular dataset. Original train/test files are combined; "
            "categorical unknown markers are kept as an explicit Unknown level."
        ),
    )


def load_bank_marketing(project_root: Path) -> CleanDataset:
    """Load the UCI Bank Marketing additional full dataset."""
    raw_path = project_root / "03_data_raw" / "bank_marketing" / "bank-additional" / "bank-additional-full.csv"
    if not raw_path.exists():
        raise FileNotFoundError(f"Missing Bank Marketing raw file: {raw_path}")

    frame = pd.read_csv(raw_path, sep=";")
    target_name = "y"
    y = (frame[target_name].astype(str).str.strip() == "yes").astype(np.int64).to_numpy()

    # Duration is a post-call variable. Dropping it keeps the prediction task closer
    # to a realistic pre-outcome audit setting.
    feature_frame = frame.drop(columns=[target_name, "duration"])
    numeric_columns = [
        "age",
        "campaign",
        "pdays",
        "previous",
        "emp.var.rate",
        "cons.price.idx",
        "cons.conf.idx",
        "euribor3m",
        "nr.employed",
    ]
    categorical_columns = [column for column in feature_frame.columns if column not in numeric_columns]
    X, feature_names = encode_mixed_tabular_frame(
        feature_frame,
        numeric_columns=numeric_columns,
        categorical_columns=categorical_columns,
    )

    return CleanDataset(
        name="bank_marketing",
        X=X,
        y=y,
        feature_names=feature_names,
        target_name=target_name,
        task_type="binary_classification",
        raw_path=raw_path,
        description=(
            "UCI Bank Marketing additional-full tabular dataset. The post-call duration feature "
            "is excluded because it is not available before the outcome is known."
        ),
    )


def load_diabetes_readmission(project_root: Path) -> CleanDataset:
    """Load UCI Diabetes 130-US Hospitals as an early-readmission task."""
    raw_path = project_root / "03_data_raw" / "diabetes_readmission" / "diabetic_data.csv"
    if not raw_path.exists():
        raise FileNotFoundError(f"Missing Diabetes raw file: {raw_path}")

    frame = pd.read_csv(raw_path)
    target_name = "readmitted"
    y = (frame[target_name].astype(str).str.strip() == "<30").astype(np.int64).to_numpy()

    feature_frame = frame.drop(columns=[target_name, "encounter_id", "patient_nbr"])
    numeric_columns = [
        "time_in_hospital",
        "num_lab_procedures",
        "num_procedures",
        "num_medications",
        "number_outpatient",
        "number_emergency",
        "number_inpatient",
        "number_diagnoses",
    ]
    categorical_columns = [column for column in feature_frame.columns if column not in numeric_columns]
    X, feature_names = encode_mixed_tabular_frame(
        feature_frame,
        numeric_columns=numeric_columns,
        categorical_columns=categorical_columns,
        max_categories_by_column={
            "diag_1": 100,
            "diag_2": 100,
            "diag_3": 100,
        },
    )

    return CleanDataset(
        name="diabetes_readmission",
        X=X,
        y=y,
        feature_names=feature_names,
        target_name=target_name,
        task_type="binary_classification",
        raw_path=raw_path,
        description=(
            "UCI Diabetes 130-US Hospitals healthcare-style tabular dataset. The target is "
            "early readmission within 30 days (`<30`) versus all other outcomes. Encounter and "
            "patient identifiers are excluded; rare diagnosis codes are grouped into Other."
        ),
    )


def load_dataset(name: str, project_root: Path | None = None) -> CleanDataset:
    root = (project_root or default_project_root()).resolve()
    loaders = {
        "credit_default": load_credit_default,
        "covertype": load_covertype,
        "adult_income": load_adult_income,
        "bank_marketing": load_bank_marketing,
        "diabetes_readmission": load_diabetes_readmission,
    }
    try:
        return loaders[name](root)
    except KeyError as exc:
        known = ", ".join(sorted(loaders))
        raise ValueError(f"Unknown dataset {name!r}. Known datasets: {known}") from exc


def make_member_nonmember_split(
    y: np.ndarray,
    *,
    test_size: float = DEFAULT_TEST_SIZE,
    random_state: int = DEFAULT_RANDOM_STATE,
) -> tuple[np.ndarray, np.ndarray]:
    """Create target-train/member and target-test/non-member indices."""
    indices = np.arange(len(y), dtype=np.int64)
    member_idx, nonmember_idx = train_test_split(
        indices,
        test_size=test_size,
        random_state=random_state,
        stratify=y,
    )
    return member_idx.astype(np.int64), nonmember_idx.astype(np.int64)


def class_counts(y: np.ndarray) -> dict[str, int]:
    values, counts = np.unique(y, return_counts=True)
    return {str(int(value)): int(count) for value, count in zip(values, counts)}


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def data_dictionary_text(dataset: CleanDataset, metadata: dict[str, Any]) -> str:
    lines = [
        f"# Data Dictionary: {dataset.name}",
        "",
        f"Generated: {metadata['generated_at']}",
        "",
        "## Summary",
        "",
        f"- Description: {dataset.description}",
        f"- Task type: `{dataset.task_type}`",
        f"- Rows: {metadata['n_rows']}",
        f"- Features: {metadata['n_features']}",
        f"- Target: `{dataset.target_name}`",
        f"- Target classes/counts: `{metadata['class_counts']}`",
        "",
        "## Split",
        "",
        f"- Random state: `{metadata['random_state']}`",
        f"- Member/target-train rows: {metadata['member_count']}",
        f"- Non-member/target-test rows: {metadata['nonmember_count']}",
        "- Split rule: 50/50 stratified split; target-train rows are treated as members, held-out target-test rows as non-members.",
        "",
        "## Features",
        "",
        "| Index | Feature | Stored dtype |",
        "| --- | --- | --- |",
    ]

    dtype = str(dataset.X.dtype)
    for index, feature in enumerate(dataset.feature_names):
        lines.append(f"| {index} | `{feature}` | `{dtype}` |")
    lines.append("")
    return "\n".join(lines)


def save_clean_dataset(
    dataset: CleanDataset,
    project_root: Path,
    *,
    random_state: int = DEFAULT_RANDOM_STATE,
    test_size: float = DEFAULT_TEST_SIZE,
) -> dict[str, Any]:
    cleaned_dir = project_root / "04_data_cleaned" / dataset.name
    cleaned_dir.mkdir(parents=True, exist_ok=True)

    member_idx, nonmember_idx = make_member_nonmember_split(
        dataset.y,
        test_size=test_size,
        random_state=random_state,
    )

    dataset_file = cleaned_dir / "cleaned_dataset.npz"
    splits_file = cleaned_dir / "member_nonmember_split.npz"
    np.savez_compressed(dataset_file, X=dataset.X, y=dataset.y)
    np.savez_compressed(splits_file, member_idx=member_idx, nonmember_idx=nonmember_idx)

    generated_at = dt.datetime.now().astimezone().isoformat(timespec="seconds")
    metadata = {
        "name": dataset.name,
        "description": dataset.description,
        "task_type": dataset.task_type,
        "raw_path": str(dataset.raw_path.relative_to(project_root)),
        "cleaned_dataset_path": str(dataset_file.relative_to(project_root)),
        "split_path": str(splits_file.relative_to(project_root)),
        "feature_names": dataset.feature_names,
        "target_name": dataset.target_name,
        "n_rows": int(dataset.X.shape[0]),
        "n_features": int(dataset.X.shape[1]),
        "X_dtype": str(dataset.X.dtype),
        "y_dtype": str(dataset.y.dtype),
        "class_counts": class_counts(dataset.y),
        "member_count": int(len(member_idx)),
        "nonmember_count": int(len(nonmember_idx)),
        "member_class_counts": class_counts(dataset.y[member_idx]),
        "nonmember_class_counts": class_counts(dataset.y[nonmember_idx]),
        "split_rule": "50/50 stratified split; member_idx is target train, nonmember_idx is held-out target test.",
        "test_size": test_size,
        "random_state": random_state,
        "generated_at": generated_at,
    }

    write_json(cleaned_dir / "metadata.json", metadata)
    (cleaned_dir / "data_dictionary.md").write_text(
        data_dictionary_text(dataset, metadata),
        encoding="utf-8",
    )
    return metadata


def preprocessing_log_text(summaries: list[dict[str, Any]]) -> str:
    generated_at = dt.datetime.now().astimezone().isoformat(timespec="seconds")
    lines = [
        "# Preprocessing Log",
        "",
        f"Last updated: {generated_at}",
        "",
        "## Shared Split Policy",
        "",
        "- Each dataset is split into target-train/member and target-test/non-member pools.",
        "- Split ratio: 50/50.",
        "- Stratification: by target label.",
        f"- Random state: `{DEFAULT_RANDOM_STATE}`.",
        "- Raw files are not manually edited.",
        "",
    ]

    for item in summaries:
        lines.extend(
            [
                f"## {item['name']}",
                "",
                f"- Raw path: `{item['raw_path']}`",
                f"- Cleaned dataset: `{item['cleaned_dataset_path']}`",
                f"- Split file: `{item['split_path']}`",
                f"- Rows: {item['n_rows']}",
                f"- Features: {item['n_features']}",
                f"- Target: `{item['target_name']}`",
                f"- Class counts: `{item['class_counts']}`",
                f"- Member rows: {item['member_count']}",
                f"- Non-member rows: {item['nonmember_count']}",
                "",
            ]
        )
    return "\n".join(lines)


def prepare_datasets(
    project_root: Path | None = None,
    *,
    dataset_names: tuple[str, ...] = CORE_DATASETS,
    random_state: int = DEFAULT_RANDOM_STATE,
    test_size: float = DEFAULT_TEST_SIZE,
) -> list[dict[str, Any]]:
    root = (project_root or default_project_root()).resolve()
    summaries: list[dict[str, Any]] = []

    for name in dataset_names:
        dataset = load_dataset(name, root)
        summaries.append(
            save_clean_dataset(
                dataset,
                root,
                random_state=random_state,
                test_size=test_size,
            )
        )

    log_path = root / "04_data_cleaned" / "preprocessing_log.md"
    log_path.write_text(preprocessing_log_text(summaries), encoding="utf-8")
    return summaries


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prepare cleaned MIA benchmark datasets.")
    parser.add_argument("--project-root", type=Path, default=default_project_root())
    parser.add_argument(
        "--datasets",
        nargs="+",
        default=list(CORE_DATASETS),
        choices=list(EXPANDED_DATASETS),
    )
    parser.add_argument("--random-state", type=int, default=DEFAULT_RANDOM_STATE)
    parser.add_argument("--test-size", type=float, default=DEFAULT_TEST_SIZE)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    summaries = prepare_datasets(
        args.project_root,
        dataset_names=tuple(args.datasets),
        random_state=args.random_state,
        test_size=args.test_size,
    )
    for summary in summaries:
        print(
            f"{summary['name']}: {summary['n_rows']} rows, "
            f"{summary['n_features']} features, "
            f"{summary['member_count']} members, "
            f"{summary['nonmember_count']} non-members"
        )


if __name__ == "__main__":
    main()
