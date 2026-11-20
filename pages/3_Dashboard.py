import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
from datetime import datetime

st.set_page_config(layout="wide")
st.title("📈 Dashboard")
st.write("Use the filters in the sidebar to explore AI agent security incidents and vulnerabilities.")
# ------------------------------------------------------------
# DATA LOADING
# Same loading steps as the EDA Gallery (incidents + vulnerabilities)
# @st.cache_data = load once, reuse on every rerun (faster)
# ------------------------------------------------------------
DATA_DIR = Path(__file__).resolve().parent.parent / "dataset"
DATA_FILE = DATA_DIR / "ai_agent_incidents_full.csv"
SEVERITY_ORDER = ["critical", "high", "medium", "low", "info"]
@st.cache_data
def load_data():
    df = pd.read_csv(DATA_FILE)
    df = df[df["kind"].isin(["incident", "vulnerability"])].copy()
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["month"] = pd.to_datetime(df["month"])
    tax = pd.read_csv(DATA_DIR / "taxonomy_attack_types.csv")
    type_names = dict(zip(tax["type_code"], tax["type_name"]))
    return df, type_names


df, type_names = load_data()
# ------------------------------------------------------------
# FILTERS (sidebar) — 3 controls
#   1. Date range slider
#   2. Severity multiselect
#   3. Attack type multiselect
# Every KPI and chart below uses the filtered table: fdf
# ------------------------------------------------------------
st.sidebar.header("Filters")
#1. Date Range
min_month = df["month"].min().to_pydatetime()
max_month = df["month"].max().to_pydatetime()
date_range = st.sidebar.slider(
    "Date range",
    min_value=min_month,
    max_value=max_month,
    value=(min_month, max_month),
    format="MMM YYYY",
)
# 2. Severity (only levels that exist in the data, in logical order)
sev_options = [s for s in SEVERITY_ORDER if s in df["severity"].unique()]
chosen_sev = st.sidebar.multiselect("Severity", sev_options, default=sev_options)

# 3. Attack type (readable names; data stores codes)
name_to_code = {name: code for code, name in type_names.items()}
type_options = sorted(type_names.values())
chosen_types = st.sidebar.multiselect("Attack type", type_options, default=type_options)
chosen_codes = {name_to_code[name] for name in chosen_types}

# Apply all three filters at once
mask = (
    df["month"].between(date_range[0], date_range[1])
    & df["severity"].isin(chosen_sev)
    & df["type"].str.split(";").apply(lambda codes: bool(set(codes) & chosen_codes))
)
fdf = df[mask]

st.caption(f"{len(fdf)} of {len(df)} records match your filters")

# Stop early if the filters remove everything
if fdf.empty:
    st.warning("No records match these filters. Try widening the date range or adding options.")
    st.stop()
# ------------------------------------------------------------
# KPIs — 4 headline numbers that update with the filters
#   1. Total records   2. % high or critical
#   3. Most common attack type   4. Avg records per month
# ------------------------------------------------------------
k1, k2, k3, k4 =st.columns(4)
# Total records 
k1.metric("Total records", len(fdf))

# Share rated high or critical 
sev_share = fdf["severity"].isin(["critical", "high"]).mean() * 100 
k2.metric("High or critical",f"{sev_share:.0f}%" )
# most common attack (only among the types the user selected)

fdf_types = fdf["type"].str.split(";").explode().str.strip()
fdf_types = fdf_types[fdf_types.isin(chosen_codes)]
type_freq = fdf_types.value_counts()
top_codes = type_freq[type_freq == type_freq.max()].index.tolist()

if len(top_codes) == 1:
    k3.metric("Most common type", top_codes[0],
              help=type_names.get(top_codes[0], top_codes[0]))
else:
    k3.metric("Most common type", f"{len(top_codes)}-way tie",
              help="Tied: " + ", ".join(type_names.get(c, c) for c in top_codes))
#  Average records per month in the selected date range
start, end = date_range
n_months = (end.year - start.year) * 12 + (end.month - start.month) + 1
k4.metric("Avg records / month", f"{len(fdf) / n_months:.1f}")


# ------------------------------------------------------------
# LINKED CHARTS — both built from fdf, so both update with the filters
#   Chart A: stacked bar, records per month by severity
#   Chart B: horizontal bar, records by attack type
# Colors match the EDA Gallery (Okabe-Ito, color-blind safe)
# ------------------------------------------------------------
SEVERITY_COLORS = {
    "critical": "#D55E00",   # vermillion
    "high": "#E69F00",       # orange
    "medium": "#56B4E9",     # sky blue
    "low": "#0072B2",        # blue
}

c1, c2 = st.columns(2)

# Chart A: records per month, stacked by severity
monthly = fdf.groupby(["month", "severity"]).size().reset_index(name="Records")

figA = px.bar(
    monthly,
    x="month",
    y="Records",
    color="severity",
    category_orders={"severity": SEVERITY_ORDER},
    color_discrete_map=SEVERITY_COLORS,
    title="Records per month by severity",
    labels={"month": "Month", "Records": "Number of records", "severity": "Severity"},
)
figA.update_layout(barmode="stack", hovermode="x unified")
figA.update_xaxes(hoverformat="%b %Y")
figA.update_traces(hovertemplate="%{fullData.name}: %{y}<extra></extra>")
c1.plotly_chart(figA)

# Chart B: records by attack type (reuses fdf_types from the KPI section)
type_counts = (
    fdf_types.map(lambda code: type_names.get(code, code))
    .value_counts()
    .reset_index()
)
type_counts.columns = ["Attack type", "Count"]

figB = px.bar(
    type_counts.sort_values("Count"),
    x="Count",
    y="Attack type",
    orientation="h",
    title="Records by attack type",
    labels={"Count": "Number of records", "Attack type": ""},
    color_discrete_sequence=["#0072B2"],
)
figB.update_traces(hovertemplate="<b>%{y}</b><br>Records: %{x}<extra></extra>")
c2.plotly_chart(figB)

# ------------------------------------------------------------
# INSIGHTS — 3–6 bullets: patterns, comparisons, limitations
# No causal claims; describes what the data shows
# ------------------------------------------------------------
st.subheader("Insights")

st.markdown(
    f"**Your current selection:** {len(fdf)} records, "
    f"{sev_share:.0f}% rated high or critical, "
    f"about {len(fdf) / n_months:.1f} per month."
)

st.markdown("""
- **Severe records dominate.** About three-quarters of all records are rated high or critical, and since early 2026 almost every new record falls in those two levels.
- **Credential theft stands out.** It is the most common attack type overall and one of the most severe (89% high or critical), backed by the largest number of records.
- **Volume is rising.** Monthly records roughly doubled from early 2025 to mid-2026, with a one-month spike in September 2026.
- **Try it:** select only *medium* and *low* severity to see that the less severe records are spread fairly evenly across attack types.
- **Limitations:** this dataset reflects incidents that were *reported and collected*, not every attack that happened. Severity is assigned by the dataset author, October 2026 is a partial month, and some attack types have very few records, so small groups should not be compared directly.
""")

# ------------------------------------------------------------
# REPRODUCIBILITY — data source badge + last refreshed timestamp
# ------------------------------------------------------------
# ------------------------------------------------------------
# ETHICS NOTE — real organizations and people; reporting bias
# ------------------------------------------------------------
st.info(
    "**Ethics note:** This dataset describes real incidents involving real organizations and, "
    "in some cases, the people affected by them. Because it is built from publicly reported "
    "sources, it may over-represent English-language and US coverage and under-count incidents "
    "that were never disclosed. The charts show patterns in what was reported. They should not "
    "be used to judge specific companies or to draw conclusions about attacks that were not reported."
)

st.divider()

KAGGLE_URL = "https://www.kaggle.com/datasets/muhammadahmerkhan/ai-agent-security-and-real-world-incidents-2024-26"
st.markdown(
    f"[![Data source: Kaggle](https://img.shields.io/badge/Data%20source-Kaggle-20BEFF?logo=kaggle)]({KAGGLE_URL})"
)

last_updated = datetime.fromtimestamp(DATA_FILE.stat().st_mtime)
st.caption(
    f"Data file last updated: {last_updated:%b %d, %Y at %I:%M %p} · "
    "Incidents + vulnerabilities only (policy, research, and report entries excluded)."
)

# Sidebar contact info (same on every page)
st.sidebar.markdown("**Sayo Owolabi**")
st.sidebar.markdown("[LinkedIn](https://www.linkedin.com/in/sayo-owolabi)")
