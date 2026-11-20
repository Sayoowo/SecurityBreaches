import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
import numpy as np

st.set_page_config(layout="wide")
st.title("📊 EDA Gallery")
st.write("Exploring real-world AI agent security incidents and vulnerabilities (2024–26).")

# ------------------------------------------------------------
# DATA LOADING
# Loads the incidents CSV + taxonomy (code -> readable name).
# @st.cache_data = load once, reuse on every rerun (faster).
# ------------------------------------------------------------
DATA_DIR = Path(__file__).resolve().parent.parent / "dataset"
SEVERITY_ORDER = ["critical", "high", "medium", "low", "info"]


@st.cache_data
def load_data():
    # Main dataset + taxonomy lookup
    df = pd.read_csv(DATA_DIR / "ai_agent_incidents_full.csv")
    tax = pd.read_csv(DATA_DIR / "taxonomy_attack_types.csv")

    # Keep real attacks and vulnerabilities only (217 rows)
    df = df[df["kind"].isin(["incident", "vulnerability"])].copy()

    # Turn text dates into real dates so we can sort and group by time
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["month"] = pd.to_datetime(df["month"])

    # Lookup table: "IPI" -> "Indirect Prompt Injection (IPI)"
    type_names = dict(zip(tax["type_code"], tax["type_name"]))

    return df, type_names


df, type_names = load_data()

st.caption(
    f"Showing {len(df)} records (incidents + vulnerabilities only). "
    "Policy, research, and report entries are excluded."
)

# ------------------------------------------------------------
# CHART 1: BAR CHART (horizontal, sorted)
# Question (Q1): Which attack types appear most in recent months?
# Interactive: YES (hover tooltips: exact count per type)
# Data note: multi-type rows split with str.split(";").explode()
# ------------------------------------------------------------
st.subheader("Q1: Which attack types appear most in recent months?")

# "Recent" = the last 6 months of data (change this number to adjust)
Recent_Months = 6
latest_month = df["month"].max()
cutoff = latest_month - pd.DateOffset(months=Recent_Months - 1)
recent = df[df["month"] >= cutoff]

# Split multi-type rows ("IPI;EXFIL" -> IPI, EXFIL), then count each type
type_counts = (
    recent["type"]
    .str.split(";")
    .explode()
    .str.strip()
    .map(lambda code: type_names.get(code, code))
    .value_counts()
    .reset_index()
)
type_counts.columns = ["Attack type", "Count"]

fig1 = px.bar(
    type_counts.sort_values("Count"),
    x="Count",
    y="Attack type",
    orientation="h",
    title=f"Attack types, {cutoff:%b %Y} – {latest_month:%b %Y}",
    labels={"Count": "Number of records", "Attack type": ""},
    color_discrete_sequence=["#0072B2"],
)
# Clean hover text: type name in bold, then the count
fig1.update_traces(hovertemplate="<b>%{y}</b><br>Records: %{x}<extra></extra>")
st.plotly_chart(fig1)

st.markdown("""
**How to read this chart**
- Each bar is one attack type; longer bars mean more records.
- Bars are sorted with the most common type at the top.
- Hover over a bar to see the exact count.
- One record can have more than one attack type, so the bars add up to more than the total number of records.

**Observations**
- Credential & Secret Theft is the most common attack type in the last six months (~26 records), followed by AI Weaponization (~24) and Infrastructure Compromise (~21).
- The top five types are fairly close together (18–26), so no single type dominates recent activity.
- Data & Model Exfiltration rarely appears alone; it shows up mostly alongside other attack types.
- Governance & Policy Failure is near the bottom because policy records were excluded from this view.
""")

st.caption(
    "Source: AI Agent Security and Real-World Incidents (2024–26), Kaggle, "
    "muhammadahmerkhan. Window: last 6 months of available data."
)

# ------------------------------------------------------------
# CHART 2: LINE CHART (3 lines: High + Critical, Medium + Low, Total)
# Question (Q2): How have incidents changed over time,
#                and where could the trend go by 2028?
# Interactive: YES ✅ INTERACTIVE #2
#   - Toggle (st.toggle) shows/hides the 2028 projection
#   - Hover tooltips on each point
# Projection: dashed line + shaded uncertainty band;
#             labeled "projection," not "prediction"
# ------------------------------------------------------------
st.subheader("Q2: How have attacks and vulnerabilities changed over time?")

# Count records per month for each severity level
monthly = (
    df.groupby(["month", "severity"])
    .size()
    .unstack(fill_value=0)
    .reindex(columns=SEVERITY_ORDER, fill_value=0)
    .asfreq("MS", fill_value=0)
)
monthly["total"] = monthly.sum(axis=1)

# Combine severities into two groups, plus the total
trend = pd.DataFrame({
    "High + Critical": monthly["critical"] + monthly["high"],
    "Medium + Low": monthly["medium"] + monthly["low"],
    "Total": monthly["total"],
})
trend = trend.loc["2025-01-01":]   # start at Jan 2025 (Dec 2024 had only 1 record)

# Reshape from "wide" (one column per line) to "long" (one row per point)
trend_long = trend.reset_index().melt(
    id_vars="month", var_name="Group", value_name="Records"
)

# Color-blind-safe colors (Okabe-Ito); severe = warm, less severe = cool
LINE_COLORS = {
    "High + Critical": "#D55E00",   # vermillion
    "Medium + Low": "#56B4E9",      # sky blue
    "Total": "#CCCCCC",             # light gray
}

fig2 = px.line(
    trend_long,
    x="month",
    y="Records",
    color="Group",
    markers=True,
    color_discrete_map=LINE_COLORS,
    title="Monthly records by severity group, Jan 2025 – Oct 2026",
    labels={"month": "Month", "Records": "Number of records", "Group": ""},
)
fig2.update_traces(line_width=3, selector=dict(name="Total"))
fig2.update_layout(hovermode="x unified")
# Clean hover text: "High + Critical: 12" and a "Mar 2026" date header
fig2.update_traces(hovertemplate="%{fullData.name}: %{y}<extra></extra>")
fig2.update_xaxes(hoverformat="%b %Y")

# Annotate the outlier and the partial month
fig2.add_annotation(
    x="2026-09-01", y=trend.loc["2026-09-01", "Total"],
    text="Sept 2026 spike:<br>may reflect collection effort",
    showarrow=True, arrowhead=2, ax=-90, ay=-30,
)
fig2.add_annotation(
    x="2026-10-01", y=trend.loc["2026-10-01", "Total"],
    text="Oct 2026:<br>partial month",
    showarrow=True, arrowhead=2, ax=50, ay=50,   # below the line, clear of the projection
)

# --- Projection toggle (INTERACTIVE #2) ---
show_projection = st.toggle("Show projection to Dec 2028", value=False)

if show_projection:
    # Fit a straight line to monthly totals, Jan 2025 – Sept 2026 (Oct is partial)
    fit_data = trend.loc["2025-01-01":"2026-09-01", "Total"]
    x = np.arange(len(fit_data))          # months as numbers: 0, 1, 2, ...
    y = fit_data.values
    slope, intercept = np.polyfit(x, y, 1)

    # Future months to project
    future_months = pd.date_range("2026-10-01", "2028-12-01", freq="MS")
    x_future = np.arange(len(x), len(x) + len(future_months))
    y_future = slope * x_future + intercept

    # 95% range: wider the further we go from the data
    residuals = y - (slope * x + intercept)
    se = np.sqrt(np.sum(residuals**2) / (len(x) - 2))
    margin = 1.96 * se * np.sqrt(
        1 + 1 / len(x) + (x_future - x.mean())**2 / np.sum((x - x.mean())**2)
    )
    upper = y_future + margin
    lower = np.clip(y_future - margin, 0, None)   # counts can't go below 0

    # Shaded band (upper edge, then lower edge filled up to it)
    fig2.add_scatter(x=future_months, y=upper, mode="lines",
                     line=dict(width=0), showlegend=False, hoverinfo="skip")
    fig2.add_scatter(x=future_months, y=lower, mode="lines",
                     line=dict(width=0), fill="tonexty",
                     fillcolor="rgba(204,204,204,0.12)",
                     name="Likely range (95%)", hoverinfo="skip")

    # Dashed projection line
    fig2.add_scatter(x=future_months, y=y_future, mode="lines",
                     line=dict(color="#CCCCCC", dash="dash", width=3),
                     name="Projected total (linear trend)",
                     hovertemplate="Projected: %{y:.0f}<extra></extra>")

    st.caption(
        f"Projection: straight-line trend fitted to Jan 2025 – Sept 2026 "
        f"(about +{slope:.1f} records per month). This is not a prediction. It shows "
        "where counts would go *if* the past trend continued. The Sept 2026 spike "
        "pulls the line upward, and reporting changes could shift the real numbers."
    )

st.plotly_chart(fig2)

st.markdown("""
**How to read this chart**
- Each line shows how many records were logged per month; the gray line is the total.
- Orange = high + critical severity; blue = medium + low.
- Hover over any month to see all three values at once.
- Turn on the toggle to see a straight-line projection (dashed) and its likely range (shaded); the wider the band, the less certain the projection.

**Observations**
- Monthly records roughly doubled from early 2025 (~5/month) to mid-2026 (~10–13/month).
- Since early 2026, almost all records are high or critical severity; medium and low dropped to near zero.
- September 2026 had 45 records, about four times a typical recent month, mostly high severity.
- If the 2025–26 trend continued, the projection reaches about 42 records/month by late 2028, but the 95% range (~10 to 62) is wide, so the data can't say precisely how much growth to expect.
""")

st.caption(
    "Source: AI Agent Security and Real-World Incidents (2024–26), Kaggle. "
    "Incidents + vulnerabilities only. October 2026 is a partial month."
)

# ------------------------------------------------------------
# CHART 3: HISTOGRAM (severity score, 1 = low → 4 = critical)
# Question (Q3): What share of incidents are high or critical?
# Interactive: YES (hover tooltips: severity + count)
# KPI above the chart shows the % high or critical
# Colors: warm = more severe, cool = less severe (Okabe-Ito,
#         same scheme as Chart 2), color-blind safe
# ------------------------------------------------------------
st.subheader("Q3: How severe are the attacks, and are some types more severe?")

# Turn severity labels into numbers so we can do math with them
# (SEVERITY_ORDER stays the same; this is a separate lookup)
SEVERITY_SCORE = {"critical": 4, "high": 3, "medium": 2, "low": 1, "info": 0}
df["severity_score"] = df["severity"].map(SEVERITY_SCORE)

# Colors per severity: warm = severe, cool = less severe (matches Chart 2)
SEVERITY_COLORS = {
    "critical": "#D55E00",   # vermillion
    "high": "#E69F00",       # orange
    "medium": "#56B4E9",     # sky blue
    "low": "#0072B2",        # blue
}

# --- Type dropdown: answers Q3b ("are some types more severe?") ---
name_to_code = {name: code for code, name in type_names.items()}
type_options = ["All types"] + sorted(type_names.values())
chosen_type = st.selectbox("Filter by attack type", type_options)

if chosen_type == "All types":
    sev_df = df
else:
    chosen_code = name_to_code[chosen_type]
    sev_df = df[df["type"].str.split(";").apply(lambda codes: chosen_code in codes)]

st.caption(f"{len(sev_df)} records in this view")

# KPI: answers "what share are high or critical?" in one number
high_crit_share = sev_df["severity"].isin(["critical", "high"]).mean() * 100
st.metric("High or critical severity", f"{high_crit_share:.0f}% of records")

fig3 = px.histogram(
    sev_df,
    x="severity_score",
    color="severity",
    category_orders={"severity": SEVERITY_ORDER},
    color_discrete_map=SEVERITY_COLORS,
    title="Number of records at each severity level",
    labels={"severity_score": "Severity", "severity": "Severity"},
)
# One bar centered on each score (1, 2, 3, 4)
fig3.update_traces(
    xbins=dict(start=0.5, end=4.5, size=1),
    hovertemplate="%{fullData.name}: %{y} records<extra></extra>",
)
# Show words instead of numbers on the x-axis
fig3.update_xaxes(tickvals=[1, 2, 3, 4], ticktext=["Low", "Medium", "High", "Critical"])
fig3.update_layout(yaxis_title="Number of records", bargap=0.1)

st.plotly_chart(fig3)

st.markdown("""
**How to read this chart**
- Each bar counts records at one severity level, from Low (left) to Critical (right).
- Warm colors (orange, red) are more severe; cool colors (blues) are less severe.
- The number above the chart shows the share rated high or critical.
- Use the dropdown to see one attack type at a time; check the record count, since small groups give less reliable percentages.

**Observations**
- 76% of all records are rated high or critical; medium and low together make up about a quarter.
- Attack types that steal data or access are rated most severe: exfiltration (94% of 16), credential theft (89% of 53), and prompt injection (87% of 23).
- Credential theft is both the most common recent type (Chart 1) and one of the most severe, backed by the largest number of records.
- MCP exploits (56%) and evaluation poisoning (58%) have the most mixed severity, with nearly half rated medium or low.
- Governance has only 2 records, too few to say anything about its severity.
""")

st.caption(
    "Source: AI Agent Security and Real-World Incidents (2024–26), Kaggle. "
    "Incidents + vulnerabilities only. Severity ratings are assigned by the dataset author. "
    "Records with multiple attack types count toward each type."
)

# ------------------------------------------------------------
# CHART 4: TREEMAP
# Question (Q4): How are incidents split across regions?
# Interactive: YES (hover tooltips; click a box to zoom in)
# Includes GLOBAL so viewers see that most incidents are worldwide
# ------------------------------------------------------------
st.subheader("Q4: How are incidents split across regions?")

# Readable names for region codes (also reused by the bubble map)
REGION_NAMES = {
    "GLOBAL": "Global", "US": "United States", "CN": "China",
    "EU": "European Union", "LATAM": "Latin America", "KR": "South Korea",
    "AU": "Australia", "JP": "Japan", "UK": "United Kingdom",
    "TW": "Taiwan", "HK": "Hong Kong", "SEA": "Southeast Asia",
    "APAC": "Asia-Pacific",
}

# Split multi-region rows ("CN;GLOBAL" -> CN, GLOBAL) and count
regions = (
    df["region"]
    .str.split(";")
    .explode()
    .str.strip()
    .map(lambda code: REGION_NAMES.get(code, code))
)
region_counts = regions.value_counts().reset_index()   # region names become a column
region_counts.columns = ["Region", "Count"]

# Group into two levels: worldwide vs. a specific place
region_counts["Scope"] = region_counts["Region"].apply(
    lambda r: "Worldwide" if r == "Global" else "Specific region"
)

fig4 = px.treemap(
    region_counts,
    path=[px.Constant("All records"), "Scope", "Region"],
    values="Count",
    color="Scope",
    color_discrete_map={
        "(?)": "#333333",               # the top "All records" box
        "Worldwide": "#999999",         # gray
        "Specific region": "#0072B2",   # blue
    },
    title="Worldwide vs. specific regions",
)
fig4.update_traces(
    textinfo="label+value+percent root",
    hovertemplate="<b>%{label}</b><br>%{value} records<br>%{percentRoot:.0%} of all<extra></extra>",
)
# Hide labels too small to read (they still show on hover or zoom)
fig4.update_layout(uniformtext=dict(minsize=11, mode="hide"))
st.plotly_chart(fig4)

st.markdown("""
**How to read this chart**
- Each box's size shows its share of all records: bigger box = more records.
- Gray = incidents affecting AI systems worldwide; blue = incidents tied to a specific country or region.
- Click the blue "Specific region" box to zoom in on the smaller regions; click the top bar to zoom back out.
- Hover over any box to see its count and percent of the total.

**Observations**
- About three-quarters of records (170) are worldwide rather than tied to one place.
- Among location-specific records, the United States (22) and China (15) account for most.
- Every other region has only 1–4 records, too few to compare reliably.
""")

st.caption(
    "Source: AI Agent Security and Real-World Incidents (2024–26), Kaggle. "
    "Incidents + vulnerabilities only. Records listing more than one region count "
    "toward each, so totals are slightly above 217. Region reflects where incidents "
    "were reported, which may favor English-language and US coverage."
)

# ------------------------------------------------------------
# CHART 5: BUBBLE MAP (scatter_geo)
# Question (Q4): Where are the location-specific incidents?
# Interactive: YES ✅ INTERACTIVE #1
#   - Hover a bubble: region name + count
#   - Drag to pan, scroll to zoom the map
# Excludes GLOBAL (can't be placed on a map); stated in caption
# ------------------------------------------------------------
# TODO: st.subheader("Q4 (map view): Where are the location-specific incidents?")

# Approximate center (latitude, longitude) for each region
REGION_COORDS = {
    "United States": (39.8, -98.6),
    "China": (35.9, 104.2),
    "European Union": (50.1, 9.7),
    "Latin America": (-10.0, -55.0),
    "South Korea": (36.5, 127.9),
    "Australia": (-25.3, 133.8),
    "Japan": (36.2, 138.3),
    "United Kingdom": (54.0, -2.0),
    "Taiwan": (23.7, 121.0),
    "Hong Kong": (22.3, 114.2),
    "Southeast Asia": (10.0, 106.0),
    "Asia-Pacific": (5.0, 125.0),
}
coords = pd.DataFrame.from_dict(REGION_COORDS, orient="index", columns=["lat", "lon"])

# Reuse the treemap counts, minus Global, then attach coordinates
global_count = region_counts.loc[region_counts["Region"] == "Global", "Count"].sum()
map_df = region_counts[region_counts["Region"] != "Global"].merge(
    coords, left_on="Region", right_index=True, how="inner"
)

fig5 = px.scatter_geo(
    map_df,
    lat="lat",
    lon="lon",
    size="Count",
    size_max=40,
    hover_name="Region",
    custom_data=["Count"],
    projection="natural earth",
    color_discrete_sequence=["#0072B2"],   # same blue as the treemap
    title="Location-specific records (bubble size = number of records)",
)
fig5.update_traces(
    marker=dict(sizemin=6, line=dict(width=1, color="white")),
    hovertemplate="<b>%{hovertext}</b><br>%{customdata[0]} records<extra></extra>",
)
# Map styling for a dark background
fig5.update_geos(
    showcountries=True, countrycolor="#555555",
    showland=True, landcolor="#2a2a2a",
    showocean=True, oceancolor="#0e1117",
    showframe=False, bgcolor="rgba(0,0,0,0)",
)
st.plotly_chart(fig5)
st.markdown("""
**How to read this map**
- Each bubble is a country or region; bigger bubbles mean more records.
- Hover over a bubble to see the region's name and number of records.
- Scroll to zoom and drag to move around the map; zoom in on East Asia, where bubbles overlap.
- Regions that cover several countries (EU, Latin America, Southeast Asia, Asia-Pacific) are placed at an approximate center.

**Observations**
- The United States has the most location-specific records (22), followed by China (15).
- East Asia (China, Hong Kong, Taiwan, Japan, South Korea) forms the largest cluster of bubbles on the map.
- Europe, Latin America, and Australia each have only a few records.
""")

st.caption(
    f"Source: AI Agent Security and Real-World Incidents (2024–26), Kaggle. "
    f"Incidents + vulnerabilities only. {global_count} records tagged Global are not shown, "
    "since they aren't tied to one place. Bubble positions for multi-country regions are approximate."
)

# Sidebar contact info (same on every page)
st.sidebar.markdown("**Sayo Owolabi**")
st.sidebar.markdown("[LinkedIn](https://www.linkedin.com/in/sayo-owolabi)")
