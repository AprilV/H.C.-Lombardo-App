#!/usr/bin/env python3
"""TA-019 s19_3: compute spread MAE evidence on validation and test splits."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List

import joblib
import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from ml.train_xgb_spread import load_data, prepare_features, split_data

DEFAULT_OUT_DIR = ROOT_DIR / "docs" / "sprints" / "ta019_spread_retrain"
DEFAULT_MODEL_PATH = ROOT_DIR / "ml" / "models" / "xgb_spread.pkl"
DEFAULT_FEATURES_PATH = ROOT_DIR / "ml" / "models" / "xgb_spread_features.txt"


@dataclass
class SplitMetrics:
    mae_points: float
    rmse_points: float
    r2: float
    winner_accuracy_pct: float
    row_count: int


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compute validation/test MAE evidence for TA-019 s19_3"
    )
    parser.add_argument("--schema", default="hcl", help="Database schema")
    parser.add_argument(
        "--model-path",
        default=str(DEFAULT_MODEL_PATH),
        help="Path to trained spread model artifact",
    )
    parser.add_argument(
        "--features-path",
        default=str(DEFAULT_FEATURES_PATH),
        help="Path to spread model feature list artifact",
    )
    parser.add_argument(
        "--out-dir",
        default=str(DEFAULT_OUT_DIR),
        help="Output directory for summary/report artifacts",
    )
    return parser.parse_args()


def load_feature_file(features_path: Path) -> List[str]:
    lines: List[str] = []
    for raw_line in features_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if line:
            lines.append(line)
    return lines


def evaluate_split(model, X: np.ndarray, y: np.ndarray) -> SplitMetrics:
    y_pred = model.predict(X)

    mae = float(mean_absolute_error(y, y_pred))
    rmse = float(np.sqrt(mean_squared_error(y, y_pred)))
    r2 = float(r2_score(y, y_pred))

    actual_winners = (y > 0).astype(int)
    pred_winners = (y_pred > 0).astype(int)
    winner_accuracy_pct = float(np.mean(actual_winners == pred_winners) * 100.0)

    return SplitMetrics(
        mae_points=mae,
        rmse_points=rmse,
        r2=r2,
        winner_accuracy_pct=winner_accuracy_pct,
        row_count=int(len(y)),
    )


def compute_metrics(schema: str, model_path: Path, features_path: Path) -> Dict[str, object]:
    df = load_data(schema=schema)
    X, y, feature_cols = prepare_features(df)
    X_train, y_train, X_val, y_val, X_test, y_test, _df_train, _df_val, _df_test = split_data(
        df, X, y
    )

    model = joblib.load(model_path)

    features_from_file = load_feature_file(features_path)
    missing_in_file = [f for f in feature_cols if f not in features_from_file]
    extra_in_file = [f for f in features_from_file if f not in feature_cols]
    ordered_match = features_from_file == feature_cols

    val_metrics = evaluate_split(model, X_val, y_val)
    test_metrics = evaluate_split(model, X_test, y_test)

    return {
        "schema": schema,
        "split_counts": {
            "train_rows": int(len(y_train)),
            "validation_rows": int(len(y_val)),
            "test_rows": int(len(y_test)),
        },
        "feature_alignment": {
            "feature_count_training": int(len(feature_cols)),
            "feature_count_file": int(len(features_from_file)),
            "ordered_match": ordered_match,
            "missing_in_feature_file": missing_in_file,
            "extra_in_feature_file": extra_in_file,
        },
        "validation": {
            "mae_points": round(val_metrics.mae_points, 4),
            "rmse_points": round(val_metrics.rmse_points, 4),
            "r2": round(val_metrics.r2, 6),
            "winner_accuracy_pct": round(val_metrics.winner_accuracy_pct, 4),
            "row_count": val_metrics.row_count,
        },
        "test": {
            "mae_points": round(test_metrics.mae_points, 4),
            "rmse_points": round(test_metrics.rmse_points, 4),
            "r2": round(test_metrics.r2, 6),
            "winner_accuracy_pct": round(test_metrics.winner_accuracy_pct, 4),
            "row_count": test_metrics.row_count,
        },
        "delta_test_minus_validation": {
            "mae_points": round(test_metrics.mae_points - val_metrics.mae_points, 4),
            "rmse_points": round(test_metrics.rmse_points - val_metrics.rmse_points, 4),
            "r2": round(test_metrics.r2 - val_metrics.r2, 6),
            "winner_accuracy_pct": round(
                test_metrics.winner_accuracy_pct - val_metrics.winner_accuracy_pct, 4
            ),
        },
    }


def write_artifacts(
    out_dir: Path,
    payload: Dict[str, object],
    model_path: Path,
    features_path: Path,
) -> tuple[Path, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    stem = f"ta019_s19_3_{ts}"
    summary_path = out_dir / f"{stem}_summary.json"
    report_path = out_dir / f"{stem}_report.md"

    envelope = {
        "subtask": "s19_3",
        "ticket": "TA-019",
        "objective": "Compute MAE on validation/test split and capture metric evidence",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "schema": payload["schema"],
        "artifacts": {
            "model_path": model_path.as_posix(),
            "feature_list_path": features_path.as_posix(),
        },
        "metrics": payload,
    }

    summary_path.write_text(json.dumps(envelope, indent=2), encoding="utf-8")

    split_counts = payload["split_counts"]
    feature_alignment = payload["feature_alignment"]
    validation = payload["validation"]
    test = payload["test"]
    delta = payload["delta_test_minus_validation"]

    report_lines = [
        "# TA-019 s19_3 Spread MAE Evidence",
        "",
        f"- Generated: {envelope['generated_at']}",
        f"- Schema: {envelope['schema']}",
        f"- Model artifact: {model_path.as_posix()}",
        f"- Feature artifact: {features_path.as_posix()}",
        "",
        "## Split Counts",
        f"- Train rows (<=2023): {split_counts['train_rows']}",
        f"- Validation rows (2024): {split_counts['validation_rows']}",
        f"- Test rows (2025): {split_counts['test_rows']}",
        "",
        "## Feature Alignment",
        f"- Training feature count: {feature_alignment['feature_count_training']}",
        f"- Feature-file count: {feature_alignment['feature_count_file']}",
        f"- Ordered match: {feature_alignment['ordered_match']}",
        f"- Missing in feature file: {feature_alignment['missing_in_feature_file']}",
        f"- Extra in feature file: {feature_alignment['extra_in_feature_file']}",
        "",
        "## Validation Metrics (2024)",
        f"- MAE: {validation['mae_points']} points",
        f"- RMSE: {validation['rmse_points']} points",
        f"- R2: {validation['r2']}",
        f"- Winner accuracy: {validation['winner_accuracy_pct']}%",
        "",
        "## Test Metrics (2025)",
        f"- MAE: {test['mae_points']} points",
        f"- RMSE: {test['rmse_points']} points",
        f"- R2: {test['r2']}",
        f"- Winner accuracy: {test['winner_accuracy_pct']}%",
        "",
        "## Delta (Test - Validation)",
        f"- MAE delta: {delta['mae_points']} points",
        f"- RMSE delta: {delta['rmse_points']} points",
        f"- R2 delta: {delta['r2']}",
        f"- Winner accuracy delta: {delta['winner_accuracy_pct']}%",
        "",
        "## Artifacts",
        f"- Summary JSON: {summary_path.as_posix()}",
        f"- Report MD: {report_path.as_posix()}",
    ]
    report_path.write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    return summary_path, report_path


def main() -> int:
    args = parse_args()

    model_path = Path(args.model_path)
    features_path = Path(args.features_path)
    out_dir = Path(args.out_dir)

    if not model_path.exists():
        print(f"error=model_artifact_missing path={model_path.as_posix()}")
        return 1
    if not features_path.exists():
        print(f"error=feature_artifact_missing path={features_path.as_posix()}")
        return 1

    metrics = compute_metrics(args.schema, model_path, features_path)
    summary_path, report_path = write_artifacts(out_dir, metrics, model_path, features_path)

    print("TA-019 s19_3 metric computation complete")
    print(f"schema={metrics['schema']}")
    print(
        "split_counts="
        f"train:{metrics['split_counts']['train_rows']},"
        f"validation:{metrics['split_counts']['validation_rows']},"
        f"test:{metrics['split_counts']['test_rows']}"
    )
    print(
        f"validation_mae_points={metrics['validation']['mae_points']}"
    )
    print(
        f"test_mae_points={metrics['test']['mae_points']}"
    )
    print(
        "feature_alignment_ordered_match="
        f"{metrics['feature_alignment']['ordered_match']}"
    )
    print(f"summary={summary_path.as_posix()}")
    print(f"report={report_path.as_posix()}")

    validation_rows_ok = metrics["split_counts"]["validation_rows"] > 0
    test_rows_ok = metrics["split_counts"]["test_rows"] > 0
    return 0 if validation_rows_ok and test_rows_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
