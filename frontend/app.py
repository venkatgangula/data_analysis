# import pandas as pd
# import plotly.express as px
# import requests
# import streamlit as st

# DEFAULT_API_URL = "http://127.0.0.1:8001"

# st.set_page_config(
#     page_title="Data Analysis Workbench",
#     page_icon="📊",
#     layout="wide",
# )

# st.title("Data Analysis Workbench")
# st.caption("Data Analysis and Data relation")


# def _error_detail(response: requests.Response) -> str:
#     if response.headers.get("content-type", "").startswith("application/json"):
#         return str(response.json().get("detail", response.text))
#     return response.text


# def render_single_analysis(data: dict) -> None:
#     duplicates = data.get("duplicates", {})
#     metric1, metric2, metric3, metric4, metric5 = st.columns(5)
#     metric1.metric("Rows", data["rows"])
#     metric2.metric("Columns", data["column_count"])
#     metric3.metric("Numeric columns", len(data["numeric_columns"]))
#     metric4.metric("Missing cells", sum(data["missing"].values()))
#     metric5.metric("Duplicate rows", duplicates.get("duplicate_row_count", 0))

#     overview_tab, missing_tab, duplicates_tab, stats_tab, charts_tab = st.tabs(
#         ["Overview", "Missing values", "Duplicates", "Statistics", "Charts"]
#     )

#     with overview_tab:
#         st.subheader(f"File: {data['filename']}")
#         schema = pd.DataFrame(
#             {
#                 "column": data["columns"],
#                 "dtype": [data["dtypes"][col] for col in data["columns"]],
#                 "unique_values": [data["unique_counts"][col] for col in data["columns"]],
#                 "missing": [data["missing"][col] for col in data["columns"]],
#             }
#         )
#         st.dataframe(schema, use_container_width=True, hide_index=True)
#         st.subheader("Preview")
#         st.dataframe(pd.DataFrame(data["preview"]), use_container_width=True, hide_index=True)

#     with missing_tab:
#         missing_df = pd.DataFrame(
#             {
#                 "column": list(data["missing"].keys()),
#                 "missing_count": list(data["missing"].values()),
#             }
#         )
#         missing_df["missing_percent"] = (missing_df["missing_count"] / data["rows"] * 100).round(2)
#         st.dataframe(missing_df, use_container_width=True, hide_index=True)
#         if missing_df["missing_count"].sum() > 0:
#             fig = px.bar(missing_df, x="column", y="missing_count", title="Missing values by column")
#             st.plotly_chart(fig, use_container_width=True)
#         else:
#             st.success("No missing values found.")

#     with duplicates_tab:
#         st.subheader("Duplicate rows")
#         dup1, dup2, dup3 = st.columns(3)
#         dup1.metric("Extra duplicate rows", duplicates.get("duplicate_row_count", 0))
#         dup2.metric("Rows involved in duplicates", duplicates.get("rows_involved_in_duplicates", 0))
#         dup3.metric("Duplicate groups", duplicates.get("unique_duplicate_groups", 0))
#         st.caption(
#             "Extra duplicate rows count copies after the first occurrence. "
#             "Rows involved includes every row that is part of a duplicated set."
#         )

#         by_column = duplicates.get("by_column", {})
#         if by_column:
#             dup_col_df = pd.DataFrame(
#                 {
#                     "column": list(by_column.keys()),
#                     "extra_duplicate_values": list(by_column.values()),
#                 }
#             )
#             dup_col_df["duplicate_percent"] = (
#                 dup_col_df["extra_duplicate_values"] / data["rows"] * 100
#             ).round(2)
#             st.subheader("Duplicate values by column")
#             st.dataframe(dup_col_df, use_container_width=True, hide_index=True)
#             fig = px.bar(
#                 dup_col_df,
#                 x="column",
#                 y="extra_duplicate_values",
#                 title="Extra duplicate values by column",
#             )
#             st.plotly_chart(fig, use_container_width=True)

#         preview_dups = duplicates.get("preview", [])
#         if preview_dups:
#             st.subheader("Duplicate row preview")
#             st.dataframe(pd.DataFrame(preview_dups), use_container_width=True, hide_index=True)
#         elif duplicates.get("duplicate_row_count", 0) == 0:
#             st.success("No fully duplicated rows found.")

#     with stats_tab:
#         numeric_statistics = data.get("numeric_statistics") or {}
#         if numeric_statistics:
#             st.subheader("Numeric statistical analysis")
#             stats_df = pd.DataFrame(numeric_statistics).T
#             st.dataframe(stats_df, use_container_width=True)
#         elif data.get("numeric_summary"):
#             st.subheader("Numeric summary")
#             st.dataframe(pd.DataFrame(data["numeric_summary"]).T, use_container_width=True)
#         else:
#             st.warning("No numeric columns available for statistical analysis.")

#         categorical_statistics = data.get("categorical_statistics") or {}
#         if categorical_statistics:
#             st.subheader("Categorical statistical analysis")
#             cat_rows = []
#             for col, stats in categorical_statistics.items():
#                 cat_rows.append(
#                     {
#                         "column": col,
#                         "count": stats.get("count"),
#                         "unique": stats.get("unique"),
#                         "mode": stats.get("mode"),
#                         "mode_count": stats.get("mode_count"),
#                     }
#                 )
#             st.dataframe(pd.DataFrame(cat_rows), use_container_width=True, hide_index=True)

#             selected_cat = st.selectbox(
#                 "Top values for column",
#                 list(categorical_statistics.keys()),
#                 key=f"cat-{data.get('filename', 'file')}",
#             )
#             top_values = pd.DataFrame(categorical_statistics[selected_cat].get("top_values", []))
#             if not top_values.empty:
#                 fig = px.bar(
#                     top_values,
#                     x="value",
#                     y="count",
#                     title=f"Top values in {selected_cat}",
#                 )
#                 st.plotly_chart(fig, use_container_width=True)

#         if data["correlation"]:
#             st.subheader("Correlation")
#             corr_df = pd.DataFrame(data["correlation"])
#             st.dataframe(corr_df, use_container_width=True)
#             fig = px.imshow(corr_df, text_auto=True, aspect="auto", title="Correlation heatmap")
#             st.plotly_chart(fig, use_container_width=True)

#     with charts_tab:
#         numeric_cols = data["numeric_columns"]
#         if not numeric_cols:
#             st.warning("No numeric columns to chart.")
#         else:
#             preview_df = pd.DataFrame(data["preview"])
#             x_col = st.selectbox("X axis", numeric_cols, key=f"x-{data.get('filename', 'file')}")
#             y_col = st.selectbox(
#                 "Y axis",
#                 numeric_cols,
#                 index=min(1, len(numeric_cols) - 1),
#                 key=f"y-{data.get('filename', 'file')}",
#             )
#             fig = px.scatter(preview_df, x=x_col, y=y_col, title="Preview scatter (first rows)")
#             st.plotly_chart(fig, use_container_width=True)
#             hist_col = st.selectbox(
#                 "Histogram column",
#                 numeric_cols,
#                 key=f"hist-{data.get('filename', 'file')}",
#             )
#             fig_hist = px.histogram(preview_df, x=hist_col, title=f"Distribution of {hist_col} (preview)")
#             st.plotly_chart(fig_hist, use_container_width=True)


# def render_integration(data: dict) -> None:
#     st.subheader("Multiple dataset integration")
#     metric1, metric2, metric3 = st.columns(3)
#     metric1.metric("Datasets", data["dataset_count"])
#     metric2.metric("Compared pairs", len(data.get("pairs", [])))
#     metric3.metric("Suggestions", len(data.get("suggestions", [])))

#     datasets_tab, relations_tab, integration_tab, suggestions_tab = st.tabs(
#         ["Datasets", "Relations", "Integrated data", "Suggestions"]
#     )

#     with datasets_tab:
#         for dataset in data.get("datasets", []):
#             st.markdown(f"**{dataset['filename']}** (`{dataset['label']}`)")
#             cols = st.columns(4)
#             cols[0].metric("Rows", dataset["rows"])
#             cols[1].metric("Columns", dataset["column_count"])
#             cols[2].metric("Missing cells", sum(dataset["missing"].values()))
#             cols[3].metric(
#                 "Duplicate rows",
#                 dataset.get("duplicates", {}).get("duplicate_row_count", 0),
#             )
#             st.dataframe(pd.DataFrame(dataset["preview"]), use_container_width=True, hide_index=True)

#     with relations_tab:
#         pairs = data.get("pairs", [])
#         if not pairs:
#             st.info("No dataset pairs to compare.")
#         else:
#             pair_labels = [f"{pair['left']} ↔ {pair['right']}" for pair in pairs]
#             selected = st.selectbox("Dataset pair", pair_labels)
#             pair = pairs[pair_labels.index(selected)]

#             st.write("Shared column names:", ", ".join(pair.get("common_columns") or ["none"]))

#             candidates = pair.get("join_candidates") or []
#             if candidates:
#                 st.subheader("Possible join keys")
#                 st.dataframe(pd.DataFrame(candidates), use_container_width=True, hide_index=True)
#             else:
#                 st.warning("No overlapping identifiers were found for a join.")

#             relations = pair.get("cross_relations") or []
#             if relations:
#                 st.subheader("Numeric relationships after join")
#                 rel_df = pd.DataFrame(relations)
#                 st.dataframe(rel_df, use_container_width=True, hide_index=True)
#                 fig = px.bar(
#                     rel_df,
#                     x="left_column",
#                     y="correlation",
#                     color="right_column",
#                     title="Cross-dataset correlations",
#                 )
#                 st.plotly_chart(fig, use_container_width=True)
#             else:
#                 st.info("Join the files on a key to estimate relationships between numeric columns.")

#     with integration_tab:
#         pairs = data.get("pairs", [])
#         if not pairs:
#             st.info("No dataset pairs to integrate.")
#         else:
#             pair_labels = [f"{pair['left']} ↔ {pair['right']}" for pair in pairs]
#             selected = st.selectbox("Integrated pair", pair_labels, key="integrated-pair")
#             pair = pairs[pair_labels.index(selected)]
#             summary = pair.get("integration")
#             concat_info = pair.get("concat")

#             if concat_info:
#                 if concat_info.get("compatible_for_stack"):
#                     st.success("These tables have the same columns and can be stacked.")
#                 else:
#                     st.caption(
#                         "Shared columns: "
#                         + (", ".join(concat_info.get("shared_columns") or ["none"]))
#                     )

#             if summary:
#                 c1, c2, c3, c4 = st.columns(4)
#                 c1.metric("Join", f"{summary['left_on']} = {summary['right_on']}")
#                 c2.metric("Matched rows", summary["matched_rows"])
#                 c3.metric(f"Only {pair['left']}", summary["left_only_rows"])
#                 c4.metric(f"Only {pair['right']}", summary["right_only_rows"])
#                 st.caption(
#                     f"Coverage: {summary['left_coverage_pct']}% of {pair['left']} and "
#                     f"{summary['right_coverage_pct']}% of {pair['right']} matched."
#                 )
#                 preview = pair.get("integrated_preview") or []
#                 if preview:
#                     st.subheader("Integrated preview")
#                     st.dataframe(pd.DataFrame(preview), use_container_width=True, hide_index=True)
#             else:
#                 st.warning("Could not build an integrated table for this pair.")

#     with suggestions_tab:
#         suggestions = data.get("suggestions") or []
#         if not suggestions:
#             st.info("No suggestions yet.")
#         for item in suggestions:
#             if item["priority"] == "high":
#                 st.success(f"**{item['title']}** — {item['detail']}")
#             elif item["priority"] == "medium":
#                 st.warning(f"**{item['title']}** — {item['detail']}")
#             else:
#                 st.info(f"**{item['title']}** — {item['detail']}")


# with st.sidebar:
#     st.header("Connection")
#     api_url = st.text_input("FastAPI URL", value=DEFAULT_API_URL).rstrip("/")

#     health_placeholder = st.empty()
#     try:
#         health = requests.get(f"{api_url}/health", timeout=3)
#         if health.ok:
#             health_placeholder.success("Backend connected")
#         else:
#             health_placeholder.error("Backend is not healthy")
#     except requests.RequestException:
#         health_placeholder.error("Cannot reach FastAPI. Start the backend first.")

#     st.header("Upload data")
#     uploaded_files = st.file_uploader(
#         "CSV or Excel file (one or more)",
#         type=["csv", "xlsx", "xls"],
#         accept_multiple_files=True,
#     )
#     st.caption(
#         "Upload one file for analysis, or two or more files to integrate them, "
#         "find relationships, and get suggestions. Try `sample_data.csv` with `sample_activity.csv`."
#     )

# if not uploaded_files:
#     st.info(
#         "Upload a dataset in the sidebar. For integration, select multiple files "
#         "such as `sample_data.csv` and `sample_activity.csv`."
#     )
#     st.stop()

# if len(uploaded_files) == 1:
#     uploaded_file = uploaded_files[0]
#     with st.spinner("Sending file to FastAPI for analysis..."):
#         try:
#             response = requests.post(
#                 f"{api_url}/analyze",
#                 files={"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)},
#                 timeout=60,
#             )
#         except requests.RequestException as exc:
#             st.error(f"Could not connect to the backend: {exc}")
#             st.stop()
#     if not response.ok:
#         st.error(f"Backend error ({response.status_code}): {_error_detail(response)}")
#         st.stop()
#     render_single_analysis(response.json())
# else:
#     with st.spinner("Integrating datasets and finding relationships..."):
#         try:
#             response = requests.post(
#                 f"{api_url}/integrate",
#                 files=[
#                     ("files", (item.name, item.getvalue(), item.type or "application/octet-stream"))
#                     for item in uploaded_files
#                 ],
#                 timeout=90,
#             )
#         except requests.RequestException as exc:
#             st.error(f"Could not connect to the backend: {exc}")
#             st.stop()
#     if not response.ok:
#         st.error(f"Backend error ({response.status_code}): {_error_detail(response)}")
#         st.stop()
#     render_integration(response.json())


import time

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import streamlit as st

DEFAULT_API_URL = "https://data-analysis-o2wf.onrender.com"

st.set_page_config(
    page_title="Data Analysis Workbench",
    page_icon="📊",
    layout="wide",
)

# ---------------------------------------------------------------------------
# Theme
# ---------------------------------------------------------------------------

THEME_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;650&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
    --bg: #0B0F14;
    --surface: #131A22;
    --surface-2: #1B2430;
    --border: #26313D;
    --text: #E8EEF4;
    --text-muted: #8DA0B3;
    --accent: #4FD1C5;
    --good: #34D399;
    --warn: #FBBF24;
    --bad: #F87171;
    --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    --font-mono: 'JetBrains Mono', 'SFMono-Regular', Consolas, monospace;
}

html, body, [class*="css"] { font-family: var(--font-sans); }
.stApp { background: var(--bg); }

/* Header */
.workbench-header {
    display: flex;
    align-items: baseline;
    gap: 0.65rem;
    border-bottom: 1px solid var(--border);
    padding-bottom: 0.9rem;
    margin-bottom: 1.5rem;
}
.workbench-header h1 {
    font-size: 1.55rem;
    font-weight: 650;
    margin: 0;
    color: var(--text);
    letter-spacing: -0.01em;
}
.workbench-header span.tagline {
    font-family: var(--font-mono);
    font-size: 0.8rem;
    color: var(--text-muted);
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: var(--surface);
    border-right: 1px solid var(--border);
}
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    font-weight: 600;
    font-size: 0.92rem;
    color: var(--text-muted);
    margin-bottom: 0.5rem;
}
[data-testid="stSidebar"] label p {
    font-size: 0.8rem;
    color: var(--text-muted);
}
[data-testid="stSidebar"] input {
    background: var(--bg) !important;
    border: 1px solid var(--border) !important;
    color: var(--text) !important;
    font-family: var(--font-mono) !important;
    font-size: 0.83rem !important;
    border-radius: 6px !important;
}
[data-testid="stSidebar"] input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 1px var(--accent) !important;
}
[data-testid="stSidebar"] .stCaption, [data-testid="stSidebar"] small {
    color: var(--text-muted) !important;
}

/* Connection status chip */
.status-chip {
    display: flex;
    align-items: center;
    gap: 0.55rem;
    padding: 0.55rem 0.75rem;
    border-radius: 7px;
    border: 1px solid var(--border);
    background: var(--surface-2);
    margin: 0.35rem 0 1rem 0;
}
.status-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    flex-shrink: 0;
}
.status-dot.on {
    background: var(--good);
    box-shadow: 0 0 0 3px rgba(52, 211, 153, 0.18);
}
.status-dot.off {
    background: var(--bad);
    box-shadow: 0 0 0 3px rgba(248, 113, 113, 0.18);
}
.status-text {
    font-family: var(--font-mono);
    font-size: 0.78rem;
    color: var(--text);
}
.status-text .muted { color: var(--text-muted); }

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    gap: 4px;
    border-bottom: 1px solid var(--border);
}
.stTabs [data-baseweb="tab"] {
    font-size: 0.85rem;
    color: var(--text-muted);
    padding: 0.5rem 0.9rem;
}
.stTabs [aria-selected="true"] {
    color: var(--accent) !important;
    border-bottom: 2px solid var(--accent) !important;
}

/* Metrics */
[data-testid="stMetric"] {
    background: var(--surface-2);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 0.7rem 0.9rem 0.55rem 0.9rem;
}
[data-testid="stMetricLabel"] { color: var(--text-muted); font-size: 0.72rem; }
[data-testid="stMetricValue"] { font-family: var(--font-mono); color: var(--text); }

/* Alerts */
[data-testid="stAlert"] {
    border-radius: 7px;
    border: 1px solid var(--border);
    background: var(--surface-2);
}

/* Dataframes */
[data-testid="stDataFrame"] {
    border: 1px solid var(--border);
    border-radius: 8px;
    overflow: hidden;
}

/* Section headers */
h2, h3 { color: var(--text); font-weight: 600; }
hr { border-color: var(--border); }
</style>
"""

st.markdown(THEME_CSS, unsafe_allow_html=True)

st.markdown(
    """
    <div class="workbench-header">
        <h1>Data Analysis Workbench</h1>
        <span class="tagline">schema · quality · relations</span>
    </div>
    """,
    unsafe_allow_html=True,
)


def render_connection_status(connected: bool, latency_ms: float | None, error: str | None = None) -> None:
    dot_class = "on" if connected else "off"
    if connected:
        label = "Backend connected"
        detail = f"{latency_ms:.0f} ms" if latency_ms is not None else ""
    else:
        label = "Backend unreachable"
        detail = error or "start the FastAPI server"
    st.markdown(
        f"""
        <div class="status-chip">
            <span class="status-dot {dot_class}"></span>
            <span class="status-text">{label}<span class="muted"> · {detail}</span></span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _error_detail(response: requests.Response) -> str:
    if response.headers.get("content-type", "").startswith("application/json"):
        return str(response.json().get("detail", response.text))
    return response.text


# ---------------------------------------------------------------------------
# Data quality scoring
# ---------------------------------------------------------------------------

QUALITY_COLORS = {"good": "#34D399", "warn": "#FBBF24", "bad": "#F87171"}


def _score_band(score: float) -> str:
    if score >= 90:
        return "good"
    if score >= 70:
        return "warn"
    return "bad"


def compute_quality_report(data: dict) -> dict:
    """Derive a data-quality score and per-column diagnostics from an
    /analyze-style response, using only fields already present in it."""

    rows = data["rows"]
    columns = data["columns"]
    missing = data["missing"]
    unique_counts = data["unique_counts"]
    duplicates = data.get("duplicates", {})
    total_cells = max(rows * len(columns), 1)
    total_missing = sum(missing.values())

    completeness = 100 * (1 - total_missing / total_cells)

    dup_rows = duplicates.get("duplicate_row_count", 0)
    uniqueness = 100 * (1 - (dup_rows / rows if rows else 0))

    flagged_columns = 0
    column_rows = []
    for col in columns:
        col_missing = missing.get(col, 0)
        col_unique = unique_counts.get(col, 0)
        non_null = rows - col_missing
        missing_pct = round(100 * col_missing / rows, 1) if rows else 0.0
        unique_pct = round(100 * col_unique / rows, 1) if rows else 0.0

        issues = []
        if non_null == 0:
            issues.append("Empty column")
        elif col_missing > 0 and missing_pct >= 50:
            issues.append(f"{missing_pct}% missing")
        if non_null > 0 and col_unique == 1:
            issues.append("Constant value")
        if rows > 20 and non_null > 0 and col_unique == non_null and missing_pct < 5:
            issues.append("All values unique (possible ID)")

        if issues:
            flagged_columns += 1

        col_score = 100.0
        col_score -= min(missing_pct, 100)
        if "Constant value" in issues:
            col_score -= 20
        if "Empty column" in issues:
            col_score = 0
        col_score = max(0, round(col_score, 1))

        column_rows.append(
            {
                "column": col,
                "missing_pct": missing_pct,
                "unique_pct": unique_pct,
                "quality_score": col_score,
                "issues": ", ".join(issues) if issues else "—",
            }
        )

    consistency = 100 * (1 - flagged_columns / len(columns)) if columns else 100
    overall = round(0.4 * completeness + 0.3 * uniqueness + 0.3 * consistency, 1)

    return {
        "overall": overall,
        "completeness": round(completeness, 1),
        "uniqueness": round(uniqueness, 1),
        "consistency": round(consistency, 1),
        "flagged_columns": flagged_columns,
        "total_columns": len(columns),
        "columns": pd.DataFrame(column_rows),
    }


def render_quality_gauge(score: float, title: str = "Overall data quality") -> go.Figure:
    color = QUALITY_COLORS[_score_band(score)]
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=score,
            title={"text": title, "font": {"family": "Inter", "size": 15, "color": "#8DA0B3"}},
            number={"font": {"family": "JetBrains Mono", "color": "#E8EEF4"}},
            gauge={
                "axis": {"range": [0, 100], "tickcolor": "#26313D"},
                "bar": {"color": color},
                "bgcolor": "#131A22",
                "borderwidth": 0,
                "steps": [
                    {"range": [0, 70], "color": "rgba(248,113,113,0.12)"},
                    {"range": [70, 90], "color": "rgba(251,191,36,0.12)"},
                    {"range": [90, 100], "color": "rgba(52,211,153,0.12)"},
                ],
            },
        )
    )
    fig.update_layout(
        height=260,
        margin=dict(l=20, r=20, t=50, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        font={"color": "#E8EEF4"},
    )
    return fig


def _style_plotly(fig: go.Figure) -> go.Figure:
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"family": "Inter", "color": "#E8EEF4"},
        title_font={"family": "Inter", "size": 15, "color": "#E8EEF4"},
        margin=dict(t=50, b=30, l=10, r=10),
    )
    fig.update_xaxes(gridcolor="#1B2430", zerolinecolor="#26313D")
    fig.update_yaxes(gridcolor="#1B2430", zerolinecolor="#26313D")
    return fig


def render_data_quality_tab(data: dict, key_prefix: str = "") -> dict:
    report = compute_quality_report(data)

    left, right = st.columns([1, 2])
    with left:
        st.plotly_chart(render_quality_gauge(report["overall"]), use_container_width=True)
    with right:
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Completeness", f"{report['completeness']}%")
        m2.metric("Uniqueness", f"{report['uniqueness']}%")
        m3.metric("Consistency", f"{report['consistency']}%")
        m4.metric("Flagged columns", f"{report['flagged_columns']} / {report['total_columns']}")
        band = _score_band(report["overall"])
        if band == "good":
            st.success("Overall data quality looks strong.")
        elif band == "warn":
            st.warning("Data quality is acceptable but has notable issues — review flagged columns.")
        else:
            st.error("Data quality is poor — several columns need attention before analysis.")

    st.subheader("Per-column quality")
    cols_df = report["columns"].sort_values("quality_score")

    def _row_color(val):
        band = _score_band(val)
        return f"background-color: {QUALITY_COLORS[band]}33"

    st.dataframe(
        cols_df.style.applymap(_row_color, subset=["quality_score"]),
        use_container_width=True,
        hide_index=True,
    )

    chart_col1, chart_col2 = st.columns(2)
    with chart_col1:
        fig = px.bar(
            cols_df,
            x="column",
            y="quality_score",
            color="quality_score",
            color_continuous_scale=["#F87171", "#FBBF24", "#34D399"],
            range_color=[0, 100],
            title="Quality score by column",
        )
        st.plotly_chart(_style_plotly(fig), use_container_width=True, key=f"{key_prefix}quality-bar")
    with chart_col2:
        fig2 = px.bar(cols_df, x="column", y="missing_pct", title="Missing % by column")
        fig2.update_traces(marker_color="#4FD1C5")
        st.plotly_chart(_style_plotly(fig2), use_container_width=True, key=f"{key_prefix}missing-bar")

    issues_df = cols_df[cols_df["issues"] != "—"]
    if not issues_df.empty:
        st.subheader("Flagged issues")
        st.dataframe(issues_df[["column", "issues"]], use_container_width=True, hide_index=True)

    return report


def render_single_analysis(data: dict) -> None:
    duplicates = data.get("duplicates", {})
    metric1, metric2, metric3, metric4, metric5 = st.columns(5)
    metric1.metric("Rows", data["rows"])
    metric2.metric("Columns", data["column_count"])
    metric3.metric("Numeric columns", len(data["numeric_columns"]))
    metric4.metric("Missing cells", sum(data["missing"].values()))
    metric5.metric("Duplicate rows", duplicates.get("duplicate_row_count", 0))

    quality_tab, overview_tab, missing_tab, duplicates_tab, stats_tab, charts_tab = st.tabs(
        ["Data quality", "Overview", "Missing values", "Duplicates", "Statistics", "Charts"]
    )

    with quality_tab:
        render_data_quality_tab(data, key_prefix=f"{data.get('filename', 'file')}-")

    with overview_tab:
        st.subheader(f"File: {data['filename']}")
        schema = pd.DataFrame(
            {
                "column": data["columns"],
                "dtype": [data["dtypes"][col] for col in data["columns"]],
                "unique_values": [data["unique_counts"][col] for col in data["columns"]],
                "missing": [data["missing"][col] for col in data["columns"]],
            }
        )
        st.dataframe(schema, use_container_width=True, hide_index=True)
        st.subheader("Preview")
        st.dataframe(pd.DataFrame(data["preview"]), use_container_width=True, hide_index=True)

    with missing_tab:
        missing_df = pd.DataFrame(
            {
                "column": list(data["missing"].keys()),
                "missing_count": list(data["missing"].values()),
            }
        )
        missing_df["missing_percent"] = (missing_df["missing_count"] / data["rows"] * 100).round(2)
        st.dataframe(missing_df, use_container_width=True, hide_index=True)
        if missing_df["missing_count"].sum() > 0:
            fig = px.bar(missing_df, x="column", y="missing_count", title="Missing values by column")
            fig.update_traces(marker_color="#4FD1C5")
            st.plotly_chart(_style_plotly(fig), use_container_width=True)
        else:
            st.success("No missing values found.")

    with duplicates_tab:
        st.subheader("Duplicate rows")
        dup1, dup2, dup3 = st.columns(3)
        dup1.metric("Extra duplicate rows", duplicates.get("duplicate_row_count", 0))
        dup2.metric("Rows involved in duplicates", duplicates.get("rows_involved_in_duplicates", 0))
        dup3.metric("Duplicate groups", duplicates.get("unique_duplicate_groups", 0))
        st.caption(
            "Extra duplicate rows count copies after the first occurrence. "
            "Rows involved includes every row that is part of a duplicated set."
        )

        by_column = duplicates.get("by_column", {})
        if by_column:
            dup_col_df = pd.DataFrame(
                {
                    "column": list(by_column.keys()),
                    "extra_duplicate_values": list(by_column.values()),
                }
            )
            dup_col_df["duplicate_percent"] = (
                dup_col_df["extra_duplicate_values"] / data["rows"] * 100
            ).round(2)
            st.subheader("Duplicate values by column")
            st.dataframe(dup_col_df, use_container_width=True, hide_index=True)
            fig = px.bar(
                dup_col_df,
                x="column",
                y="extra_duplicate_values",
                title="Extra duplicate values by column",
            )
            fig.update_traces(marker_color="#F87171")
            st.plotly_chart(_style_plotly(fig), use_container_width=True)

        preview_dups = duplicates.get("preview", [])
        if preview_dups:
            st.subheader("Duplicate row preview")
            st.dataframe(pd.DataFrame(preview_dups), use_container_width=True, hide_index=True)
        elif duplicates.get("duplicate_row_count", 0) == 0:
            st.success("No fully duplicated rows found.")

    with stats_tab:
        numeric_statistics = data.get("numeric_statistics") or {}
        if numeric_statistics:
            st.subheader("Numeric statistical analysis")
            stats_df = pd.DataFrame(numeric_statistics).T
            st.dataframe(stats_df, use_container_width=True)
        elif data.get("numeric_summary"):
            st.subheader("Numeric summary")
            st.dataframe(pd.DataFrame(data["numeric_summary"]).T, use_container_width=True)
        else:
            st.warning("No numeric columns available for statistical analysis.")

        categorical_statistics = data.get("categorical_statistics") or {}
        if categorical_statistics:
            st.subheader("Categorical statistical analysis")
            cat_rows = []
            for col, stats in categorical_statistics.items():
                cat_rows.append(
                    {
                        "column": col,
                        "count": stats.get("count"),
                        "unique": stats.get("unique"),
                        "mode": stats.get("mode"),
                        "mode_count": stats.get("mode_count"),
                    }
                )
            st.dataframe(pd.DataFrame(cat_rows), use_container_width=True, hide_index=True)

            selected_cat = st.selectbox(
                "Top values for column",
                list(categorical_statistics.keys()),
                key=f"cat-{data.get('filename', 'file')}",
            )
            top_values = pd.DataFrame(categorical_statistics[selected_cat].get("top_values", []))
            if not top_values.empty:
                fig = px.bar(top_values, x="value", y="count", title=f"Top values in {selected_cat}")
                fig.update_traces(marker_color="#4FD1C5")
                st.plotly_chart(_style_plotly(fig), use_container_width=True)

        if data["correlation"]:
            st.subheader("Correlation")
            corr_df = pd.DataFrame(data["correlation"])
            st.dataframe(corr_df, use_container_width=True)
            fig = px.imshow(
                corr_df,
                text_auto=True,
                aspect="auto",
                title="Correlation heatmap",
                color_continuous_scale="Teal",
            )
            st.plotly_chart(_style_plotly(fig), use_container_width=True)

    with charts_tab:
        numeric_cols = data["numeric_columns"]
        if not numeric_cols:
            st.warning("No numeric columns to chart.")
        else:
            preview_df = pd.DataFrame(data["preview"])
            x_col = st.selectbox("X axis", numeric_cols, key=f"x-{data.get('filename', 'file')}")
            y_col = st.selectbox(
                "Y axis",
                numeric_cols,
                index=min(1, len(numeric_cols) - 1),
                key=f"y-{data.get('filename', 'file')}",
            )
            fig = px.scatter(preview_df, x=x_col, y=y_col, title="Preview scatter (first rows)")
            fig.update_traces(marker_color="#4FD1C5")
            st.plotly_chart(_style_plotly(fig), use_container_width=True)
            hist_col = st.selectbox(
                "Histogram column",
                numeric_cols,
                key=f"hist-{data.get('filename', 'file')}",
            )
            fig_hist = px.histogram(preview_df, x=hist_col, title=f"Distribution of {hist_col} (preview)")
            fig_hist.update_traces(marker_color="#4FD1C5")
            st.plotly_chart(_style_plotly(fig_hist), use_container_width=True)


def render_integration(data: dict) -> None:
    st.subheader("Multiple dataset integration")
    metric1, metric2, metric3 = st.columns(3)
    metric1.metric("Datasets", data["dataset_count"])
    metric2.metric("Compared pairs", len(data.get("pairs", [])))
    metric3.metric("Suggestions", len(data.get("suggestions", [])))

    quality_tab, datasets_tab, relations_tab, integration_tab, suggestions_tab = st.tabs(
        ["Data quality", "Datasets", "Relations", "Integrated data", "Suggestions"]
    )

    with quality_tab:
        st.caption("Quality is scored independently for each uploaded dataset.")
        summary_rows = []
        dataset_labels = [d["filename"] for d in data.get("datasets", [])]
        selected_ds = st.selectbox("Dataset", dataset_labels, key="quality-dataset-select")
        selected_report = None
        selected_data = None
        for dataset in data.get("datasets", []):
            report = compute_quality_report(dataset)
            summary_rows.append(
                {
                    "dataset": dataset["filename"],
                    "overall_score": report["overall"],
                    "completeness": report["completeness"],
                    "uniqueness": report["uniqueness"],
                    "consistency": report["consistency"],
                    "flagged_columns": f"{report['flagged_columns']}/{report['total_columns']}",
                }
            )
            if dataset["filename"] == selected_ds:
                selected_report = report
                selected_data = dataset

        st.subheader("Quality summary across datasets")
        summary_df = pd.DataFrame(summary_rows)
        fig = px.bar(
            summary_df,
            x="dataset",
            y="overall_score",
            color="overall_score",
            color_continuous_scale=["#F87171", "#FBBF24", "#34D399"],
            range_color=[0, 100],
            title="Overall data quality score by dataset",
        )
        st.plotly_chart(_style_plotly(fig), use_container_width=True)
        st.dataframe(summary_df, use_container_width=True, hide_index=True)

        st.divider()
        st.subheader(f"Detail: {selected_ds}")
        if selected_data is not None:
            render_data_quality_tab(selected_data, key_prefix=f"{selected_ds}-")

    with datasets_tab:
        for dataset in data.get("datasets", []):
            st.markdown(f"**{dataset['filename']}** (`{dataset['label']}`)")
            cols = st.columns(4)
            cols[0].metric("Rows", dataset["rows"])
            cols[1].metric("Columns", dataset["column_count"])
            cols[2].metric("Missing cells", sum(dataset["missing"].values()))
            cols[3].metric("Duplicate rows", dataset.get("duplicates", {}).get("duplicate_row_count", 0))
            st.dataframe(pd.DataFrame(dataset["preview"]), use_container_width=True, hide_index=True)

    with relations_tab:
        pairs = data.get("pairs", [])
        if not pairs:
            st.info("No dataset pairs to compare.")
        else:
            pair_labels = [f"{pair['left']} ↔ {pair['right']}" for pair in pairs]
            selected = st.selectbox("Dataset pair", pair_labels)
            pair = pairs[pair_labels.index(selected)]

            st.write("Shared column names:", ", ".join(pair.get("common_columns") or ["none"]))

            candidates = pair.get("join_candidates") or []
            if candidates:
                st.subheader("Possible join keys")
                st.dataframe(pd.DataFrame(candidates), use_container_width=True, hide_index=True)
            else:
                st.warning("No overlapping identifiers were found for a join.")

            relations = pair.get("cross_relations") or []
            if relations:
                st.subheader("Numeric relationships after join")
                rel_df = pd.DataFrame(relations)
                st.dataframe(rel_df, use_container_width=True, hide_index=True)
                fig = px.bar(
                    rel_df,
                    x="left_column",
                    y="correlation",
                    color="right_column",
                    title="Cross-dataset correlations",
                )
                st.plotly_chart(_style_plotly(fig), use_container_width=True)
            else:
                st.info("Join the files on a key to estimate relationships between numeric columns.")

    with integration_tab:
        pairs = data.get("pairs", [])
        if not pairs:
            st.info("No dataset pairs to integrate.")
        else:
            pair_labels = [f"{pair['left']} ↔ {pair['right']}" for pair in pairs]
            selected = st.selectbox("Integrated pair", pair_labels, key="integrated-pair")
            pair = pairs[pair_labels.index(selected)]
            summary = pair.get("integration")
            concat_info = pair.get("concat")

            if concat_info:
                if concat_info.get("compatible_for_stack"):
                    st.success("These tables have the same columns and can be stacked.")
                else:
                    st.caption("Shared columns: " + (", ".join(concat_info.get("shared_columns") or ["none"])))

            if summary:
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Join", f"{summary['left_on']} = {summary['right_on']}")
                c2.metric("Matched rows", summary["matched_rows"])
                c3.metric(f"Only {pair['left']}", summary["left_only_rows"])
                c4.metric(f"Only {pair['right']}", summary["right_only_rows"])
                st.caption(
                    f"Coverage: {summary['left_coverage_pct']}% of {pair['left']} and "
                    f"{summary['right_coverage_pct']}% of {pair['right']} matched."
                )
                preview = pair.get("integrated_preview") or []
                if preview:
                    st.subheader("Integrated preview")
                    st.dataframe(pd.DataFrame(preview), use_container_width=True, hide_index=True)
            else:
                st.warning("Could not build an integrated table for this pair.")

    with suggestions_tab:
        suggestions = data.get("suggestions") or []
        if not suggestions:
            st.info("No suggestions yet.")
        for item in suggestions:
            if item["priority"] == "high":
                st.success(f"**{item['title']}** — {item['detail']}")
            elif item["priority"] == "medium":
                st.warning(f"**{item['title']}** — {item['detail']}")
            else:
                st.info(f"**{item['title']}** — {item['detail']}")


with st.sidebar:
    st.subheader("Connection")
    api_url = st.text_input("FastAPI URL", value=DEFAULT_API_URL, label_visibility="collapsed").rstrip("/")

    status_placeholder = st.empty()
    try:
        start = time.perf_counter()
        health = requests.get(f"{api_url}/health", timeout=3)
        elapsed_ms = (time.perf_counter() - start) * 1000
        with status_placeholder:
            render_connection_status(connected=health.ok, latency_ms=elapsed_ms)
        if not health.ok:
            with status_placeholder:
                render_connection_status(connected=False, latency_ms=None, error="backend is not healthy")
    except requests.RequestException:
        with status_placeholder:
            render_connection_status(connected=False, latency_ms=None)

    st.subheader("Upload data")
    uploaded_files = st.file_uploader(
        "CSV or Excel file (one or more)",
        type=["csv", "xlsx", "xls"],
        accept_multiple_files=True,
        label_visibility="collapsed",
    )
    st.caption(
        "Upload one file for analysis, or two or more files to integrate them, "
        "find relationships, and get suggestions. Try `sample_data.csv` with `sample_activity.csv`."
    )

if not uploaded_files:
    st.info(
        "Upload a dataset in the sidebar. For integration, select multiple files "
        "such as `sample_data.csv` and `sample_activity.csv`."
    )
    st.stop()

if len(uploaded_files) == 1:
    uploaded_file = uploaded_files[0]
    with st.spinner("Sending file to FastAPI for analysis..."):
        try:
            response = requests.post(
                f"{api_url}/analyze",
                files={"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)},
                timeout=60,
            )
        except requests.RequestException as exc:
            st.error(f"Could not connect to the backend: {exc}")
            st.stop()
    if not response.ok:
        st.error(f"Backend error ({response.status_code}): {_error_detail(response)}")
        st.stop()
    render_single_analysis(response.json())
else:
    with st.spinner("Integrating datasets and finding relationships..."):
        try:
            response = requests.post(
                f"{api_url}/integrate",
                files=[
                    ("files", (item.name, item.getvalue(), item.type or "application/octet-stream"))
                    for item in uploaded_files
                ],
                timeout=90,
            )
        except requests.RequestException as exc:
            st.error(f"Could not connect to the backend: {exc}")
            st.stop()
    if not response.ok:
        st.error(f"Backend error ({response.status_code}): {_error_detail(response)}")
        st.stop()
    render_integration(response.json())
