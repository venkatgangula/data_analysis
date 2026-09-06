from __future__ import annotations

import io
from typing import Any

import pandas as pd


SUPPORTED_EXTENSIONS = {".csv", ".xlsx", ".xls"}


def load_dataframe(file_bytes: bytes, filename: str) -> pd.DataFrame:
    name = filename.lower()
    buffer = io.BytesIO(file_bytes)

    if name.endswith(".csv"):
        return pd.read_csv(buffer)
    if name.endswith(".xlsx") or name.endswith(".xls"):
        return pd.read_excel(buffer)

    raise ValueError(
        "Unsupported file type. Upload a CSV or Excel file (.csv, .xlsx, .xls)."
    )


def _json_safe(value: Any) -> Any:
    if pd.isna(value):
        return None
    if hasattr(value, "item"):
        return value.item()
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    return value


def _records(df: pd.DataFrame) -> list[dict[str, Any]]:
    return [
        {str(col): _json_safe(row[col]) for col in df.columns}
        for row in df.to_dict(orient="records")
    ]


def _duplicate_analysis(df: pd.DataFrame, preview_rows: int = 10) -> dict[str, Any]:
    extra_copies = df.duplicated()
    involved = df.duplicated(keep=False)
    involved_df = df.loc[involved]
    unique_groups = int(involved_df.drop_duplicates().shape[0]) if not involved_df.empty else 0

    by_column: dict[str, int] = {}
    for col in df.columns:
        series = df[col]
        extra = int(series.duplicated().sum())
        by_column[str(col)] = extra

    return {
        "duplicate_row_count": int(extra_copies.sum()),
        "rows_involved_in_duplicates": int(involved.sum()),
        "unique_duplicate_groups": unique_groups,
        "duplicate_percent": round(float(extra_copies.sum()) / len(df) * 100, 2) if len(df) else 0.0,
        "by_column": by_column,
        "preview": _records(involved_df.head(preview_rows)),
    }


def _numeric_statistics(series: pd.Series) -> dict[str, Any]:
    clean = series.dropna()
    if clean.empty:
        return {
            "count": 0,
            "mean": None,
            "median": None,
            "mode": None,
            "std": None,
            "variance": None,
            "min": None,
            "max": None,
            "range": None,
            "q1": None,
            "q3": None,
            "iqr": None,
            "skewness": None,
            "kurtosis": None,
        }

    q1 = clean.quantile(0.25)
    q3 = clean.quantile(0.75)
    modes = clean.mode()
    return {
        "count": int(clean.count()),
        "mean": _json_safe(round(clean.mean(), 4)),
        "median": _json_safe(round(clean.median(), 4)),
        "mode": _json_safe(modes.iloc[0]) if not modes.empty else None,
        "std": _json_safe(round(clean.std(ddof=1), 4)) if len(clean) > 1 else None,
        "variance": _json_safe(round(clean.var(ddof=1), 4)) if len(clean) > 1 else None,
        "min": _json_safe(round(clean.min(), 4)),
        "max": _json_safe(round(clean.max(), 4)),
        "range": _json_safe(round(clean.max() - clean.min(), 4)),
        "q1": _json_safe(round(q1, 4)),
        "q3": _json_safe(round(q3, 4)),
        "iqr": _json_safe(round(q3 - q1, 4)),
        "skewness": _json_safe(round(clean.skew(), 4)) if len(clean) > 2 else None,
        "kurtosis": _json_safe(round(clean.kurtosis(), 4)) if len(clean) > 3 else None,
    }


def _categorical_statistics(series: pd.Series, top_n: int = 5) -> dict[str, Any]:
    clean = series.dropna()
    value_counts = clean.value_counts()
    modes = clean.mode()
    top_values = [
        {"value": _json_safe(idx), "count": int(count)}
        for idx, count in value_counts.head(top_n).items()
    ]
    return {
        "count": int(clean.count()),
        "unique": int(clean.nunique()),
        "mode": _json_safe(modes.iloc[0]) if not modes.empty else None,
        "mode_count": int(value_counts.iloc[0]) if not value_counts.empty else 0,
        "top_values": top_values,
    }


def profile_dataframe(df: pd.DataFrame, preview_rows: int = 10) -> dict[str, Any]:
    numeric_df = df.select_dtypes(include="number")
    categorical_cols = [str(col) for col in df.select_dtypes(exclude="number").columns]
    missing = df.isna().sum()

    summary = {}
    if not numeric_df.empty:
        describe = numeric_df.describe().round(4)
        summary = {
            col: {stat: _json_safe(val) for stat, val in stats.items()}
            for col, stats in describe.to_dict().items()
        }

    correlation = {}
    if numeric_df.shape[1] >= 2:
        correlation = {
            col: {other: _json_safe(val) for other, val in row.items()}
            for col, row in numeric_df.corr().round(4).to_dict().items()
        }

    numeric_statistics = {
        str(col): _numeric_statistics(numeric_df[col]) for col in numeric_df.columns
    }
    categorical_statistics = {
        col: _categorical_statistics(df[col]) for col in categorical_cols
    }

    return {
        "rows": int(len(df)),
        "column_count": int(df.shape[1]),
        "columns": [str(col) for col in df.columns],
        "dtypes": {str(col): str(dtype) for col, dtype in df.dtypes.items()},
        "missing": {str(col): int(count) for col, count in missing.items()},
        "unique_counts": {str(col): int(count) for col, count in df.nunique().items()},
        "numeric_columns": [str(col) for col in numeric_df.columns],
        "categorical_columns": categorical_cols,
        "numeric_summary": summary,
        "numeric_statistics": numeric_statistics,
        "categorical_statistics": categorical_statistics,
        "duplicates": _duplicate_analysis(df, preview_rows=preview_rows),
        "correlation": correlation,
        "preview": _records(df.head(preview_rows)),
    }
