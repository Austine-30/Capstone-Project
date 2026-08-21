"""
3_📊_Rock_Fluid_Dashboard.py
=============================
Module C — Rock & Fluid Data Dashboard.

Upload a CSV of rock/fluid sample data, view summary statistics, filter it
interactively, and explore it with a porosity histogram and a
porosity-permeability crossplot. Filtered data can be downloaded as CSV.

This page is deliberately generic about column names: it looks for
plausible porosity/permeability columns but lets the user pick manually
if auto-detection fails, so it works with more than one dataset shape.
"""

import os

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Rock & Fluid Dashboard", page_icon="📊", layout="wide")
st.title("📊 Rock & Fluid Data Dashboard")
st.caption(
    "Upload a CSV of rock or fluid sample data (e.g. porosity, permeability, "
    "lithology) to explore it. A sample dataset is provided if you don't have one."
)


def guess_column(columns, keywords):
    """Return the first column name containing any of the given keywords.

    Args:
        columns: Iterable of column name strings to search.
        keywords: Iterable of lowercase substrings to match against.

    Returns:
        The matching column name, or None if no column matches.
    """
    for col in columns:
        low = col.lower()
        if any(kw in low for kw in keywords):
            return col
    return None


uploaded = st.file_uploader("Upload CSV", type=["csv"])

sample_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                            "sample_data", "rock_fluid_sample.csv")
use_sample = False
if uploaded is None:
    if os.path.exists(sample_path):
        use_sample = st.checkbox("No file? Use the built-in sample dataset instead.", value=True)
    if not use_sample:
        st.info("Upload a CSV, or check the box above to try the sample dataset.")
        st.stop()

try:
    if uploaded is not None:
        df = pd.read_csv(uploaded)
    else:
        df = pd.read_csv(sample_path)
except Exception as e:  # noqa: BLE001 - surface any parse error to the user, not a crash
    st.error(f"Couldn't read that file as a CSV: {e}")
    st.stop()

if df.empty:
    st.error("The uploaded file has no rows.")
    st.stop()

st.subheader("Data preview")
st.dataframe(df.head(10), use_container_width=True)

st.subheader("Summary statistics")
numeric_df = df.select_dtypes(include="number")
if numeric_df.empty:
    st.warning("No numeric columns found — can't compute summary statistics or plots.")
    st.stop()
st.dataframe(numeric_df.describe().T, use_container_width=True)

st.divider()

# ------------------------------------------------------------- Filtering --
st.subheader("Filter")
numeric_cols = list(numeric_df.columns)

porosity_guess = guess_column(numeric_cols, ["poros", "phi"])
permeability_guess = guess_column(numeric_cols, ["perm", "k_md", "permeability"])

filter_col = st.selectbox(
    "Filter column",
    numeric_cols,
    index=numeric_cols.index(porosity_guess) if porosity_guess in numeric_cols else 0,
    help="Choose which numeric column to filter the dataset on.",
)
col_min, col_max = float(df[filter_col].min()), float(df[filter_col].max())
if col_min == col_max:
    st.info(f"'{filter_col}' has a single value ({col_min}) across all rows — nothing to filter.")
    threshold = col_min
    filtered_df = df.copy()
else:
    threshold = st.slider(
        f"Show only rows where {filter_col} >",
        min_value=col_min, max_value=col_max, value=col_min,
        help=f"Drag to filter rows by minimum {filter_col}.",
    )
    filtered_df = df[df[filter_col] > threshold]

st.caption(f"Showing {len(filtered_df)} of {len(df)} rows.")
st.dataframe(filtered_df, use_container_width=True)

st.divider()

# ---------------------------------------------------------------- Charts --
st.subheader("Charts")
c1, c2 = st.columns(2)

with c1:
    st.markdown(f"**Histogram — {filter_col}**")
    if not filtered_df.empty:
        hist_source = filtered_df[[filter_col]].dropna()
        st.bar_chart(hist_source[filter_col].value_counts(bins=15).sort_index())
    else:
        st.info("No rows match the current filter.")

with c2:
    st.markdown("**Porosity–Permeability crossplot**")
    x_col = st.selectbox(
        "X axis", numeric_cols,
        index=numeric_cols.index(porosity_guess) if porosity_guess in numeric_cols else 0,
        key="crossplot_x",
    )
    y_col = st.selectbox(
        "Y axis", numeric_cols,
        index=numeric_cols.index(permeability_guess) if permeability_guess in numeric_cols
        else min(1, len(numeric_cols) - 1),
        key="crossplot_y",
    )
    if not filtered_df.empty:
        st.scatter_chart(filtered_df, x=x_col, y=y_col)
        st.caption(
            "Tip: permeability commonly spans orders of magnitude — if your "
            "crossplot looks squashed, consider a log-scaled permeability "
            "column in your source data."
        )
    else:
        st.info("No rows match the current filter.")

st.divider()

# ------------------------------------------------------------------ Export
st.subheader("Export")
csv_bytes = filtered_df.to_csv(index=False).encode("utf-8")
st.download_button(
    "Download filtered data as CSV",
    data=csv_bytes,
    file_name="filtered_rock_fluid_data.csv",
    mime="text/csv",
)
