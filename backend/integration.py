# from __future__ import annotations

# from itertools import combinations
# from pathlib import Path
# from typing import Any

# import pandas as pd
# from difflib import SequenceMatcher

# from analysis import _json_safe, _records, profile_dataframe

# MAX_DATASETS = 5
# PREVIEW_ROWS = 10
# MIN_JOIN_JACCARD = 0.05
# STRONG_CORR = 0.5


# def _safe_label(filename: str, index: int, used: set[str]) -> str:
#     stem = Path(filename).stem
#     label = "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in stem) or f"dataset_{index + 1}"
#     candidate = label
#     suffix = 2
#     while candidate in used:
#         candidate = f"{label}_{suffix}"
#         suffix += 1
#     used.add(candidate)
#     return candidate


# def _unique_strings(series: pd.Series) -> set[str]:
#     return {str(value) for value in series.dropna().tolist()}


# def _looks_like_key(column: str, series: pd.Series, row_count: int) -> bool:
#     name = str(column).lower()
#     if any(token in name for token in ("id", "key", "code", "uuid", "email", "name")):
#         return True
#     unique_count = int(series.nunique(dropna=True))
#     return bool(row_count and unique_count / row_count >= 0.8)


# def _name_similarity(left: str, right: str) -> float:
#     a = str(left).strip().lower().replace(" ", "_").replace("-", "_")
#     b = str(right).strip().lower().replace(" ", "_").replace("-", "_")
#     if a == b:
#         return 1.0
#     return round(SequenceMatcher(None, a, b).ratio(), 4)


# def _join_candidates(left: pd.DataFrame, right: pd.DataFrame) -> list[dict[str, Any]]:
#     candidates: list[dict[str, Any]] = []
#     for left_col in left.columns:
#         left_values = _unique_strings(left[left_col])
#         left_is_key = _looks_like_key(left_col, left[left_col], len(left))
#         for right_col in right.columns:
#             name_score = _name_similarity(str(left_col), str(right_col))
#             right_is_key = _looks_like_key(right_col, right[right_col], len(right))
#             if name_score < 0.72 and not (left_is_key and right_is_key):
#                 continue

#             right_values = _unique_strings(right[right_col])
#             if not left_values or not right_values:
#                 continue
#             shared = left_values & right_values
#             union = left_values | right_values
#             jaccard = len(shared) / len(union) if union else 0.0
#             if name_score < 1.0 and jaccard < 0.2:
#                 continue
#             if jaccard < MIN_JOIN_JACCARD:
#                 continue

#             score = round(0.45 * name_score + 0.55 * jaccard, 4)
#             candidates.append(
#                 {
#                     "left_column": str(left_col),
#                     "right_column": str(right_col),
#                     "name_similarity": name_score,
#                     "shared_values": len(shared),
#                     "left_unique": len(left_values),
#                     "right_unique": len(right_values),
#                     "jaccard": round(jaccard, 4),
#                     "left_match_rate": round(len(shared) / len(left_values), 4),
#                     "right_match_rate": round(len(shared) / len(right_values), 4),
#                     "score": score,
#                 }
#             )

#     candidates.sort(key=lambda item: item["score"], reverse=True)
#     return candidates[:12]


# def _merge_pair(
#     left: pd.DataFrame,
#     right: pd.DataFrame,
#     left_name: str,
#     right_name: str,
#     candidate: dict[str, Any],
# ) -> tuple[pd.DataFrame, dict[str, Any]]:
#     left_on = candidate["left_column"]
#     right_on = candidate["right_column"]
#     left_renamed = left.rename(
#         columns={col: f"{left_name}__{col}" for col in left.columns if col != left_on}
#     )
#     right_renamed = right.rename(
#         columns={col: f"{right_name}__{col}" for col in right.columns if col != right_on}
#     )
#     if left_on == right_on:
#         merged = left_renamed.merge(right_renamed, on=left_on, how="outer", indicator=True)
#         join_column = left_on
#     else:
#         merged = left_renamed.merge(
#             right_renamed,
#             left_on=left_on,
#             right_on=right_on,
#             how="outer",
#             indicator=True,
#         )
#         join_column = f"{left_on} / {right_on}"

#     counts = merged["_merge"].value_counts().to_dict()
#     both = int(counts.get("both", 0))
#     left_only = int(counts.get("left_only", 0))
#     right_only = int(counts.get("right_only", 0))
#     summary = {
#         "method": "outer_join",
#         "join_column": join_column,
#         "left_on": left_on,
#         "right_on": right_on,
#         "matched_rows": both,
#         "left_only_rows": left_only,
#         "right_only_rows": right_only,
#         "integrated_rows": int(len(merged)),
#         "integrated_columns": int(merged.shape[1] - 1),
#         "left_coverage_pct": round(both / len(left) * 100, 2) if len(left) else 0.0,
#         "right_coverage_pct": round(both / len(right) * 100, 2) if len(right) else 0.0,
#     }
#     return merged.drop(columns=["_merge"]), summary


# def _cross_correlations(
#     merged: pd.DataFrame,
#     left: pd.DataFrame,
#     right: pd.DataFrame,
#     left_name: str,
#     right_name: str,
#     join_left: str,
#     join_right: str,
# ) -> list[dict[str, Any]]:
#     left_numeric = [
#         col
#         for col in left.select_dtypes(include="number").columns
#         if col != join_left
#     ]
#     right_numeric = [
#         col
#         for col in right.select_dtypes(include="number").columns
#         if col != join_right
#     ]
#     relations: list[dict[str, Any]] = []
#     if merged.empty:
#         return relations

#     for left_col in left_numeric:
#         left_merged = left_col if left_col in merged.columns else f"{left_name}__{left_col}"
#         if left_merged not in merged.columns:
#             continue
#         for right_col in right_numeric:
#             right_merged = right_col if right_col in merged.columns else f"{right_name}__{right_col}"
#             if right_merged not in merged.columns:
#                 continue
#             pair = merged[[left_merged, right_merged]].dropna()
#             if len(pair) < 4:
#                 continue
#             corr = pair[left_merged].corr(pair[right_merged])
#             if pd.isna(corr):
#                 continue
#             relations.append(
#                 {
#                     "left_column": f"{left_name}.{left_col}",
#                     "right_column": f"{right_name}.{right_col}",
#                     "correlation": _json_safe(round(float(corr), 4)),
#                     "sample_size": int(len(pair)),
#                     "strength": _corr_strength(float(corr)),
#                 }
#             )
#     relations.sort(key=lambda item: abs(item["correlation"] or 0), reverse=True)
#     return relations[:20]


# def _corr_strength(value: float) -> str:
#     magnitude = abs(value)
#     if magnitude >= 0.7:
#         return "strong"
#     if magnitude >= STRONG_CORR:
#         return "moderate"
#     if magnitude >= 0.3:
#         return "weak"
#     return "very weak"


# def _concat_if_compatible(left: pd.DataFrame, right: pd.DataFrame) -> dict[str, Any] | None:
#     left_cols = [str(col) for col in left.columns]
#     right_cols = [str(col) for col in right.columns]
#     shared = set(left_cols) & set(right_cols)
#     if not shared:
#         return None
#     compatible = left_cols == right_cols
#     stacked = pd.concat([left, right], ignore_index=True, sort=False) if compatible else None
#     return {
#         "compatible_for_stack": compatible,
#         "shared_columns": sorted(shared),
#         "left_only_columns": sorted(set(left_cols) - set(right_cols)),
#         "right_only_columns": sorted(set(right_cols) - set(left_cols)),
#         "stacked_rows": int(len(stacked)) if stacked is not None else None,
#     }


# def _suggestions(
#     left_name: str,
#     right_name: str,
#     left: pd.DataFrame,
#     right: pd.DataFrame,
#     candidates: list[dict[str, Any]],
#     merge_summary: dict[str, Any] | None,
#     relations: list[dict[str, Any]],
#     concat_info: dict[str, Any] | None,
# ) -> list[dict[str, str]]:
#     suggestions: list[dict[str, str]] = []

#     if concat_info and concat_info["compatible_for_stack"]:
#         suggestions.append(
#             {
#                 "priority": "high",
#                 "title": "Stack the datasets vertically",
#                 "detail": (
#                     f"{left_name} and {right_name} share the same columns. "
#                     "Concatenate them to build one longer table, then drop duplicate rows."
#                 ),
#             }
#         )

#     if candidates:
#         best = candidates[0]
#         suggestions.append(
#             {
#                 "priority": "high" if best["score"] >= 0.6 else "medium",
#                 "title": f"Join on {best['left_column']} = {best['right_column']}",
#                 "detail": (
#                     f"This key pair scores {best['score']}. "
#                     f"{best['left_match_rate'] * 100:.1f}% of {left_name} keys and "
#                     f"{best['right_match_rate'] * 100:.1f}% of {right_name} keys overlap."
#                 ),
#             }
#         )
#     else:
#         suggestions.append(
#             {
#                 "priority": "high",
#                 "title": "No reliable join key was found",
#                 "detail": (
#                     "Add a shared identifier (id, code, or name) to both files, "
#                     "or rename matching columns so they can be merged."
#                 ),
#             }
#         )

#     if merge_summary:
#         unmatched = merge_summary["left_only_rows"] + merge_summary["right_only_rows"]
#         if unmatched:
#             suggestions.append(
#                 {
#                     "priority": "medium",
#                     "title": "Investigate unmatched rows after the join",
#                     "detail": (
#                         f"{merge_summary['left_only_rows']} rows stay only in {left_name} and "
#                         f"{merge_summary['right_only_rows']} stay only in {right_name}. "
#                         "Check missing IDs, extra whitespace, or type mismatches."
#                     ),
#                 }
#             )

#     strong = [item for item in relations if abs(item.get("correlation") or 0) >= STRONG_CORR]
#     if strong:
#         top = strong[0]
#         suggestions.append(
#             {
#                 "priority": "high",
#                 "title": f"{top['left_column']} is related to {top['right_column']}",
#                 "detail": (
#                     f"Pearson correlation is {top['correlation']} ({top['strength']}). "
#                     "Use this pair for scatter plots, regression, or a combined KPI."
#                 ),
#             }
#         )
#     elif relations:
#         suggestions.append(
#             {
#                 "priority": "low",
#                 "title": "Cross-dataset numeric links are weak",
#                 "detail": (
#                     "After joining, no strong linear relationship appeared. "
#                     "Try grouping by a category, or check non-linear patterns in charts."
#                 ),
#             }
#         )

#     left_missing = int(left.isna().sum().sum())
#     right_missing = int(right.isna().sum().sum())
#     if left_missing or right_missing:
#         suggestions.append(
#             {
#                 "priority": "medium",
#                 "title": "Clean missing values before modeling",
#                 "detail": (
#                     f"{left_name} has {left_missing} missing cells and "
#                     f"{right_name} has {right_missing}. "
#                     "Impute or drop them so joined statistics stay reliable."
#                 ),
#             }
#         )

#     if int(left.duplicated().sum()) or int(right.duplicated().sum()):
#         suggestions.append(
#             {
#                 "priority": "medium",
#                 "title": "Remove duplicate rows before joining",
#                 "detail": "Duplicate keys can inflate a merge into a many-to-many join.",
#             }
#         )

#     return suggestions


# def analyze_pair(
#     left_name: str,
#     left: pd.DataFrame,
#     right_name: str,
#     right: pd.DataFrame,
# ) -> dict[str, Any]:
#     common_columns = sorted(set(map(str, left.columns)) & set(map(str, right.columns)))
#     candidates = _join_candidates(left, right)
#     concat_info = _concat_if_compatible(left, right)

#     merged = None
#     merge_summary = None
#     relations: list[dict[str, Any]] = []
#     if candidates:
#         merged, merge_summary = _merge_pair(left, right, left_name, right_name, candidates[0])
#         relations = _cross_correlations(
#             merged,
#             left,
#             right,
#             left_name,
#             right_name,
#             candidates[0]["left_column"],
#             candidates[0]["right_column"],
#         )

#     return {
#         "left": left_name,
#         "right": right_name,
#         "common_columns": common_columns,
#         "join_candidates": candidates,
#         "concat": concat_info,
#         "integration": merge_summary,
#         "cross_relations": relations,
#         "integrated_preview": _records(merged.head(PREVIEW_ROWS)) if merged is not None else [],
#         "suggestions": _suggestions(
#             left_name,
#             right_name,
#             left,
#             right,
#             candidates,
#             merge_summary,
#             relations,
#             concat_info,
#         ),
#     }


# def integrate_datasets(datasets: list[tuple[str, pd.DataFrame]]) -> dict[str, Any]:
#     if len(datasets) < 2:
#         raise ValueError("Upload at least two datasets to integrate.")
#     if len(datasets) > MAX_DATASETS:
#         raise ValueError(f"Upload at most {MAX_DATASETS} datasets at a time.")

#     used_labels: set[str] = set()
#     named: list[tuple[str, str, pd.DataFrame]] = []
#     for index, (filename, frame) in enumerate(datasets):
#         if frame.empty:
#             raise ValueError(f"{filename} has no rows.")
#         label = _safe_label(filename, index, used_labels)
#         named.append((filename, label, frame))

#     profiles = []
#     for filename, label, frame in named:
#         profile = profile_dataframe(frame)
#         profile["filename"] = filename
#         profile["label"] = label
#         profiles.append(profile)

#     pairs = [
#         analyze_pair(left_label, left_df, right_label, right_df)
#         for (_, left_label, left_df), (_, right_label, right_df) in combinations(named, 2)
#     ]

#     all_suggestions: list[dict[str, str]] = []
#     seen: set[str] = set()
#     for pair in pairs:
#         for item in pair["suggestions"]:
#             key = f"{item['title']}|{item['detail']}"
#             if key in seen:
#                 continue
#             seen.add(key)
#             all_suggestions.append(item)

#     priority_rank = {"high": 0, "medium": 1, "low": 2}
#     all_suggestions.sort(key=lambda item: priority_rank.get(item["priority"], 9))

#     return {
#         "dataset_count": len(named),
#         "datasets": profiles,
#         "pairs": pairs,
#         "suggestions": all_suggestions,
#     }


from __future__ import annotations

from itertools import combinations
from pathlib import Path
from typing import Any
from difflib import SequenceMatcher

import pandas as pd

from analysis import _json_safe, _records, profile_dataframe


MAX_DATASETS = 5
PREVIEW_ROWS = 10

# Minimum overlap required before considering two columns a relationship
MIN_OVERLAP = 0.05

# Correlation thresholds
STRONG_CORRELATION = 0.70
MODERATE_CORRELATION = 0.50


# ---------------------------------------------------------
# DATASET LABEL
# ---------------------------------------------------------

def _safe_label(filename: str, index: int, used: set[str]) -> str:

    stem = Path(filename).stem

    label = "".join(
        ch if ch.isalnum() or ch in "-_"
        else "_"
        for ch in stem
    )

    if not label:
        label = f"dataset_{index + 1}"

    candidate = label
    counter = 2

    while candidate in used:
        candidate = f"{label}_{counter}"
        counter += 1

    used.add(candidate)

    return candidate


# ---------------------------------------------------------
# NORMALIZE VALUES
# ---------------------------------------------------------

def _normalize_value(value: Any) -> str | None:

    if pd.isna(value):
        return None

    value = str(value).strip().lower()

    # Remove unnecessary .0 from numeric IDs
    if value.endswith(".0"):
        try:
            value = str(int(float(value)))
        except ValueError:
            pass

    return value


def _unique_values(series: pd.Series) -> set[str]:

    values = set()

    for value in series:

        normalized = _normalize_value(value)

        if normalized is not None and normalized != "":
            values.add(normalized)

    return values


# ---------------------------------------------------------
# COLUMN NAME NORMALIZATION
# ---------------------------------------------------------

def _normalize_column_name(name: str) -> str:

    return (
        str(name)
        .strip()
        .lower()
        .replace("-", "_")
        .replace(" ", "_")
    )


# ---------------------------------------------------------
# COLUMN NAME SIMILARITY
# ---------------------------------------------------------

def _name_similarity(left: str, right: str) -> float:

    left = _normalize_column_name(left)
    right = _normalize_column_name(right)

    if left == right:
        return 1.0

    return round(
        SequenceMatcher(None, left, right).ratio(),
        4
    )


# ---------------------------------------------------------
# DETECT ID / KEY COLUMNS
# ---------------------------------------------------------

def _looks_like_key(
    column: str,
    series: pd.Series,
    row_count: int
) -> bool:

    name = _normalize_column_name(column)

    key_words = [
        "id",
        "key",
        "code",
        "uuid",
        "email",
        "roll",
        "registration",
        "customer",
        "employee",
        "student",
        "account",
        "product"
    ]

    if any(word in name for word in key_words):

        return True

    unique_count = series.nunique(dropna=True)

    if row_count == 0:
        return False

    uniqueness_ratio = unique_count / row_count

    return uniqueness_ratio >= 0.80


# ---------------------------------------------------------
# FIND RELATIONSHIP BETWEEN TWO COLUMNS
# ---------------------------------------------------------

def _calculate_column_relationship(
    left_column: str,
    left_series: pd.Series,
    right_column: str,
    right_series: pd.Series,
) -> dict[str, Any] | None:

    left_values = _unique_values(left_series)
    right_values = _unique_values(right_series)

    if not left_values or not right_values:
        return None

    shared_values = left_values.intersection(right_values)

    union_values = left_values.union(right_values)

    if not union_values:
        return None

    jaccard = len(shared_values) / len(union_values)

    left_match_rate = (
        len(shared_values) / len(left_values)
        if left_values
        else 0
    )

    right_match_rate = (
        len(shared_values) / len(right_values)
        if right_values
        else 0
    )

    name_score = _name_similarity(
        left_column,
        right_column
    )

    left_is_key = _looks_like_key(
        left_column,
        left_series,
        len(left_series)
    )

    right_is_key = _looks_like_key(
        right_column,
        right_series,
        len(right_series)
    )

    # -----------------------------------------------------
    # SCORE
    # -----------------------------------------------------

    score = (
        0.30 * name_score
        + 0.50 * jaccard
        + 0.20 * min(left_match_rate, right_match_rate)
    )

    # Stronger score when both columns look like IDs
    if left_is_key and right_is_key:
        score += 0.10

    score = min(score, 1.0)

    # Ignore completely unrelated columns
    if jaccard < MIN_OVERLAP:
        return None

    # If names are unrelated, require stronger value overlap
    if name_score < 0.40 and jaccard < 0.30:
        return None

    # -----------------------------------------------------
    # CLASSIFICATION
    # -----------------------------------------------------

    if score >= 0.75:
        relationship = "Very Strong"

    elif score >= 0.60:
        relationship = "Strong"

    elif score >= 0.45:
        relationship = "Moderate"

    else:
        relationship = "Weak"

    return {
        "left_column": str(left_column),
        "right_column": str(right_column),

        "relationship_type": relationship,

        "score": round(score, 4),

        "name_similarity": round(name_score, 4),

        "shared_values": len(shared_values),

        "left_unique_values": len(left_values),

        "right_unique_values": len(right_values),

        "jaccard_similarity": round(jaccard, 4),

        "left_match_rate": round(left_match_rate, 4),

        "right_match_rate": round(right_match_rate, 4),

        "left_is_key": left_is_key,

        "right_is_key": right_is_key,
    }


# ---------------------------------------------------------
# FIND ALL POSSIBLE JOIN COLUMNS
# ---------------------------------------------------------

def _find_join_candidates(
    left: pd.DataFrame,
    right: pd.DataFrame
) -> list[dict[str, Any]]:

    candidates = []

    for left_column in left.columns:

        for right_column in right.columns:

            result = _calculate_column_relationship(
                left_column,
                left[left_column],
                right_column,
                right[right_column],
            )

            if result is not None:

                candidates.append(result)

    # Highest score first
    candidates.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    return candidates[:15]


# ---------------------------------------------------------
# MERGE DATASETS
# ---------------------------------------------------------

def _merge_pair(
    left: pd.DataFrame,
    right: pd.DataFrame,
    left_name: str,
    right_name: str,
    candidate: dict[str, Any],
) -> tuple[pd.DataFrame, dict[str, Any]]:

    left_on = candidate["left_column"]
    right_on = candidate["right_column"]

    left_copy = left.copy()
    right_copy = right.copy()

    # Normalize join columns
    left_copy[left_on] = left_copy[left_on].map(
        _normalize_value
    )

    right_copy[right_on] = right_copy[right_on].map(
        _normalize_value
    )

    # Rename non-key columns
    left_copy = left_copy.rename(
        columns={
            col: f"{left_name}__{col}"
            for col in left_copy.columns
            if col != left_on
        }
    )

    right_copy = right_copy.rename(
        columns={
            col: f"{right_name}__{col}"
            for col in right_copy.columns
            if col != right_on
        }
    )

    # -----------------------------------------------------
    # MERGE
    # -----------------------------------------------------

    if left_on == right_on:

        merged = pd.merge(
            left_copy,
            right_copy,
            on=left_on,
            how="outer",
            indicator=True,
            validate="many_to_many",
        )

        join_column = left_on

    else:

        merged = pd.merge(
            left_copy,
            right_copy,
            left_on=left_on,
            right_on=right_on,
            how="outer",
            indicator=True,
            validate="many_to_many",
        )

        join_column = f"{left_on} ↔ {right_on}"

    # -----------------------------------------------------
    # MERGE STATISTICS
    # -----------------------------------------------------

    counts = merged["_merge"].value_counts()

    matched = int(counts.get("both", 0))
    left_only = int(counts.get("left_only", 0))
    right_only = int(counts.get("right_only", 0))

    summary = {

        "method": "outer_join",

        "join_column": join_column,

        "left_on": left_on,

        "right_on": right_on,

        "matched_rows": matched,

        "left_only_rows": left_only,

        "right_only_rows": right_only,

        "integrated_rows": int(len(merged)),

        "integrated_columns": int(
            merged.shape[1] - 1
        ),

        "left_coverage_pct": round(
            matched / len(left) * 100,
            2
        ) if len(left) else 0,

        "right_coverage_pct": round(
            matched / len(right) * 100,
            2
        ) if len(right) else 0,
    }

    merged = merged.drop(
        columns=["_merge"]
    )

    return merged, summary


# ---------------------------------------------------------
# NUMERIC RELATIONSHIPS
# ---------------------------------------------------------

def _cross_correlations(
    merged: pd.DataFrame,
    left: pd.DataFrame,
    right: pd.DataFrame,
    left_name: str,
    right_name: str,
    join_left: str,
    join_right: str,
) -> list[dict[str, Any]]:

    relations = []

    left_numeric = list(
        left.select_dtypes(
            include="number"
        ).columns
    )

    right_numeric = list(
        right.select_dtypes(
            include="number"
        ).columns
    )

    # Remove join keys if numeric
    left_numeric = [
        col
        for col in left_numeric
        if col != join_left
    ]

    right_numeric = [
        col
        for col in right_numeric
        if col != join_right
    ]

    for left_column in left_numeric:

        left_merged_column = (
            left_column
            if left_column in merged.columns
            else f"{left_name}__{left_column}"
        )

        if left_merged_column not in merged.columns:
            continue

        for right_column in right_numeric:

            right_merged_column = (
                right_column
                if right_column in merged.columns
                else f"{right_name}__{right_column}"
            )

            if right_merged_column not in merged.columns:
                continue

            pair = merged[
                [
                    left_merged_column,
                    right_merged_column
                ]
            ].dropna()

            if len(pair) < 4:
                continue

            correlation = pair[
                left_merged_column
            ].corr(
                pair[right_merged_column]
            )

            if pd.isna(correlation):
                continue

            correlation = float(correlation)

            absolute_corr = abs(correlation)

            if absolute_corr >= STRONG_CORRELATION:
                strength = "Strong"

            elif absolute_corr >= MODERATE_CORRELATION:
                strength = "Moderate"

            elif absolute_corr >= 0.30:
                strength = "Weak"

            else:
                strength = "Very Weak"

            if correlation > 0:
                direction = "Positive"

            else:
                direction = "Negative"

            relations.append({

                "left_column":
                    f"{left_name}.{left_column}",

                "right_column":
                    f"{right_name}.{right_column}",

                "correlation":
                    round(correlation, 4),

                "absolute_correlation":
                    round(absolute_corr, 4),

                "direction":
                    direction,

                "strength":
                    strength,

                "sample_size":
                    int(len(pair)),
            })

    relations.sort(
        key=lambda x: x["absolute_correlation"],
        reverse=True
    )

    return relations[:20]


# ---------------------------------------------------------
# STACK COMPATIBLE DATASETS
# ---------------------------------------------------------

def _concat_if_compatible(
    left: pd.DataFrame,
    right: pd.DataFrame
) -> dict[str, Any] | None:

    left_columns = [
        str(col)
        for col in left.columns
    ]

    right_columns = [
        str(col)
        for col in right.columns
    ]

    shared = set(left_columns).intersection(
        right_columns
    )

    if not shared:
        return None

    compatible = (
        left_columns == right_columns
    )

    return {

        "compatible_for_stack":
            compatible,

        "shared_columns":
            sorted(shared),

        "left_only_columns":
            sorted(
                set(left_columns)
                - set(right_columns)
            ),

        "right_only_columns":
            sorted(
                set(right_columns)
                - set(left_columns)
            ),

        "stacked_rows":
            int(len(left) + len(right))
            if compatible
            else None,
    }


# ---------------------------------------------------------
# SUGGESTIONS
# ---------------------------------------------------------

def _suggestions(
    left_name: str,
    right_name: str,
    left: pd.DataFrame,
    right: pd.DataFrame,
    candidates: list[dict[str, Any]],
    merge_summary: dict[str, Any] | None,
    relations: list[dict[str, Any]],
    concat_info: dict[str, Any] | None,
) -> list[dict[str, str]]:

    suggestions = []

    # -----------------------------------------------------
    # STACK
    # -----------------------------------------------------

    if concat_info and concat_info[
        "compatible_for_stack"
    ]:

        suggestions.append({

            "priority": "high",

            "title":
                "Datasets can be stacked",

            "detail":
                f"{left_name} and {right_name} "
                "have the same columns. "
                "They can be concatenated vertically.",
        })

    # -----------------------------------------------------
    # JOIN
    # -----------------------------------------------------

    if candidates:

        best = candidates[0]

        suggestions.append({

            "priority":
                "high"
                if best["score"] >= 0.60
                else "medium",

            "title":
                f"Join using "
                f"{best['left_column']} ↔ "
                f"{best['right_column']}",

            "detail":
                f"Relationship score: "
                f"{best['score']}. "
                f"{best['left_match_rate'] * 100:.1f}% "
                f"of {left_name} values match and "
                f"{best['right_match_rate'] * 100:.1f}% "
                f"of {right_name} values match.",
        })

    else:

        suggestions.append({

            "priority": "high",

            "title":
                "No reliable join key found",

            "detail":
                "The datasets do not have enough "
                "overlapping values to confidently "
                "join them.",
        })

    # -----------------------------------------------------
    # UNMATCHED ROWS
    # -----------------------------------------------------

    if merge_summary:

        unmatched = (
            merge_summary["left_only_rows"]
            + merge_summary["right_only_rows"]
        )

        if unmatched > 0:

            suggestions.append({

                "priority": "medium",

                "title":
                    "Some rows could not be matched",

                "detail":
                    f"{merge_summary['left_only_rows']} "
                    f"rows exist only in {left_name}, "
                    f"while "
                    f"{merge_summary['right_only_rows']} "
                    f"exist only in {right_name}. "
                    "Check missing IDs, spelling, "
                    "spaces and data types.",
            })

    # -----------------------------------------------------
    # NUMERIC RELATIONSHIP
    # -----------------------------------------------------

    strong_relations = [
        item
        for item in relations
        if abs(
            item["correlation"]
        ) >= MODERATE_CORRELATION
    ]

    if strong_relations:

        top = strong_relations[0]

        suggestions.append({

            "priority": "high",

            "title":
                f"Numeric relationship detected",

            "detail":
                f"{top['left_column']} and "
                f"{top['right_column']} have "
                f"a {top['strength'].lower()} "
                f"{top['direction'].lower()} "
                f"relationship "
                f"(correlation = "
                f"{top['correlation']}).",
        })

    # -----------------------------------------------------
    # MISSING VALUES
    # -----------------------------------------------------

    left_missing = int(
        left.isna().sum().sum()
    )

    right_missing = int(
        right.isna().sum().sum()
    )

    if left_missing or right_missing:

        suggestions.append({

            "priority": "medium",

            "title":
                "Missing values detected",

            "detail":
                f"{left_name} contains "
                f"{left_missing} missing cells "
                f"and {right_name} contains "
                f"{right_missing}.",
        })

    # -----------------------------------------------------
    # DUPLICATES
    # -----------------------------------------------------

    left_duplicates = int(
        left.duplicated().sum()
    )

    right_duplicates = int(
        right.duplicated().sum()
    )

    if left_duplicates or right_duplicates:

        suggestions.append({

            "priority": "medium",

            "title":
                "Duplicate rows detected",

            "detail":
                "Duplicates may create "
                "many-to-many joins and "
                "increase the number of "
                "rows after merging.",
        })

    return suggestions


# ---------------------------------------------------------
# ANALYZE TWO DATASETS
# ---------------------------------------------------------

def analyze_pair(
    left_name: str,
    left: pd.DataFrame,
    right_name: str,
    right: pd.DataFrame,
) -> dict[str, Any]:

    common_columns = sorted(
        set(map(str, left.columns))
        &
        set(map(str, right.columns))
    )

    candidates = _find_join_candidates(
        left,
        right
    )

    concat_info = _concat_if_compatible(
        left,
        right
    )

    merged = None
    merge_summary = None
    numeric_relationships = []

    # -----------------------------------------------------
    # USE BEST RELATIONSHIP
    # -----------------------------------------------------

    if candidates:

        best_candidate = candidates[0]

        merged, merge_summary = _merge_pair(
            left,
            right,
            left_name,
            right_name,
            best_candidate
        )

        numeric_relationships = _cross_correlations(
            merged,
            left,
            right,
            left_name,
            right_name,
            best_candidate["left_column"],
            best_candidate["right_column"],
        )

    suggestions = _suggestions(
        left_name,
        right_name,
        left,
        right,
        candidates,
        merge_summary,
        numeric_relationships,
        concat_info,
    )

    return {

        "left": left_name,

        "right": right_name,

        "common_columns":
            common_columns,

        "join_candidates":
            candidates,

        "best_join":
            candidates[0]
            if candidates
            else None,

        "concat":
            concat_info,

        "integration":
            merge_summary,

        "cross_relations":
            numeric_relationships,

        "integrated_preview":
            _records(
                merged.head(PREVIEW_ROWS)
            )
            if merged is not None
            else [],

        "suggestions":
            suggestions,
    }


# ---------------------------------------------------------
# ANALYZE ALL DATASETS
# ---------------------------------------------------------

def integrate_datasets(
    datasets: list[
        tuple[str, pd.DataFrame]
    ]
) -> dict[str, Any]:

    if len(datasets) < 2:

        raise ValueError(
            "Upload at least two datasets."
        )

    if len(datasets) > MAX_DATASETS:

        raise ValueError(
            f"Upload at most "
            f"{MAX_DATASETS} datasets."
        )

    # -----------------------------------------------------
    # CREATE UNIQUE LABELS
    # -----------------------------------------------------

    used_labels = set()

    named = []

    for index, (filename, dataframe) in enumerate(
        datasets
    ):

        if dataframe.empty:

            raise ValueError(
                f"{filename} has no rows."
            )

        dataframe = dataframe.copy()

        # Clean column names
        dataframe.columns = [
            str(column).strip()
            for column in dataframe.columns
        ]

        label = _safe_label(
            filename,
            index,
            used_labels
        )

        named.append(
            (
                filename,
                label,
                dataframe
            )
        )

    # -----------------------------------------------------
    # DATASET PROFILES
    # -----------------------------------------------------

    profiles = []

    for filename, label, dataframe in named:

        profile = profile_dataframe(
            dataframe
        )

        profile["filename"] = filename
        profile["label"] = label

        profiles.append(profile)

    # -----------------------------------------------------
    # COMPARE EVERY DATASET PAIR
    # -----------------------------------------------------

    pairs = []

    for (
        left_file,
        left_label,
        left_dataframe
    ), (
        right_file,
        right_label,
        right_dataframe
    ) in combinations(named, 2):

        pair_result = analyze_pair(
            left_label,
            left_dataframe,
            right_label,
            right_dataframe,
        )

        # Add original filenames
        pair_result["left_filename"] = left_file
        pair_result["right_filename"] = right_file

        pairs.append(pair_result)

    # -----------------------------------------------------
    # COMBINE SUGGESTIONS
    # -----------------------------------------------------

    all_suggestions = []

    seen = set()

    for pair in pairs:

        for suggestion in pair[
            "suggestions"
        ]:

            key = (
                suggestion["title"],
                suggestion["detail"]
            )

            if key in seen:
                continue

            seen.add(key)

            all_suggestions.append(
                suggestion
            )

    priority = {
        "high": 0,
        "medium": 1,
        "low": 2
    }

    all_suggestions.sort(
        key=lambda x:
        priority.get(
            x["priority"],
            99
        )
    )

    # -----------------------------------------------------
    # RETURN RESULT
    # -----------------------------------------------------

    return {

        "dataset_count":
            len(named),

        "datasets":
            profiles,

        "pairs":
            pairs,

        "suggestions":
            all_suggestions,
    }