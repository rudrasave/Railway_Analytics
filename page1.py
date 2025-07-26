import streamlit as st
st.set_page_config(layout="wide")
import oracledb
import pandas as pd
import plotly.express as px
from testquery import DB_HOST, DB_SID, DB_USER, DB_PASSWORD, DB_PORT


# Dropdown for year selection
years = [
    "25_26", "24_25", "23_24", "22_23", "21_22", "20_21", "19_20", "18_19", "17_18"
]
year_labels = {
    "25_26": "2025-26",
    "24_25": "2024-25",
    "23_24": "2023-24",
    "22_23": "2022-23",
    "21_22": "2021-22",
    "20_21": "2020-21",
    "19_20": "2019-20",
    "18_19": "2018-19",
    "17_18": "2017-18"
}
selected_year = st.selectbox("Select Year", [year_labels[y] for y in years[:5]])

# Get the index of the selected year
selected_idx = [year_labels[y] for y in years].index(selected_year)
# Get the 5 years (selected and previous 4)
table_years = years[selected_idx:selected_idx+5]

# Prepare table names
table_names = [f"carr_apmt_excl_adv_{y}" for y in table_years]

# Oracle connection string
dsn = oracledb.makedsn(DB_HOST, DB_PORT, sid=DB_SID)
conn = oracledb.connect(user=DB_USER, password=DB_PASSWORD, dsn=dsn)
cur = conn.cursor()

TARGET_SCHEMA = "FOISGOODS"

# SQL templates
queries = [
    "SELECT SUM(CHBL_WGHT) AS SUM_DIFF FROM {schema}.{table} WHERE ZONE_FRM = 'WR'",
    "SELECT SUM(TOT_FRT_INCL_GST - TOT_GST) AS SUM_DIFF FROM {schema}.{table} WHERE ZONE_FRM = 'WR'",
    "SELECT SUM(WR) AS SUM_DIFF FROM {schema}.{table} WHERE ZONE_FRM = 'WR'",
    "SELECT SUM(WR) AS SUM_DIFF FROM {schema}.{table} WHERE ZONE_FRM != 'WR'"
]

results = []
for table in table_names:
    row_vals = []
    for q in queries:
        cur.execute(q.format(schema=TARGET_SCHEMA, table=table))
        val = cur.fetchone()[0] or 0
        row_vals.append(val)
    # Derived rows
    row3, row4 = row_vals[2], row_vals[3]
    row5 = row3 + row4
    row2 = row_vals[1]
    row6 = row5 / row2 if row2 else None
    row7 = row3 / row2 if row2 else None
    row8 = row3 / row5 if row5 else None
    row9 = row4 / row5 if row5 else None
    # Convert all values to crore for display
    row_vals_crore = [v / 1e7 if isinstance(v, (int, float)) else v for v in [row_vals[0], row2, row3, row4, row5]]
    # Convert ratios to percentage (if not None)
    derived_percent = [round(r * 100, 2) if r is not None else None for r in [row6, row7, row8, row9]]
    results.append(row_vals_crore + derived_percent)

cur.close()
conn.close()

# Define row names before creating DataFrame
row_names = [
    "SUM(CHBL_WGHT) (WR)", "SUM(TOT_FRT_INCL_GST - TOT_GST) (WR)",
    "SUM(WR) (WR)", "SUM(WR) (not WR)", "row 3 + row 4",
    "row 5 / row 2 (%)", "row 3 / row 2 (%)", "row 3 / row 5 (%)", "row 4 / row 5 (%)"
]

# Create DataFrame with years in correct order
df = pd.DataFrame(results, columns=row_names, index=[year_labels[y] for y in table_years])
df = df.T

# Prepare summary table (first 5 rows)
summary_rows = [
    "SUM(CHBL_WGHT) (WR)",
    "SUM(TOT_FRT_INCL_GST - TOT_GST) (WR)",
    "SUM(WR) (WR)",
    "SUM(WR) (not WR)",
    "row 3 + row 4"
]
summary_names = [
    "Loading",
    "Originating Revenue",
    "Apportioned Revenue (Outward Retained Share)",
    "Apportioned Revenue (Inward Share)",
    "Total Apportioned Revenue (3+4)"
]
summary_df = df.loc[summary_rows].copy()
summary_df.index = summary_names

# Calculate % var w.r.t P.Y. for each row and add as a new column
def pct_var(series):
    vals = series.values
    if len(vals) < 2:
        return None
    # Use first value as current year and second value as previous year
    # since table_years is in descending order
    curr = vals[0]  # Current year value
    prev = vals[1]  # Previous year value
    if prev and prev != 0:
        pct_change = ((curr - prev) / prev) * 100
        return f"{round(pct_change, 2)}%"
    return None

summary_df["% var w.r.t P.Y."] = summary_df.apply(pct_var, axis=1)

# Ensure columns are years (not rows), and all data is visible in one glance
summary_df = summary_df.reset_index()
summary_df.rename(columns={'index': 'Particulars'}, inplace=True)
# Move "% var w.r.t P.Y." to the last column
cols = [col for col in summary_df.columns if col != "% var w.r.t P.Y."] + ["% var w.r.t P.Y."]
summary_df = summary_df[cols]

# Prepare ratio table
ratio_rows = [
    "row 5 / row 2 (%)",
    "row 3 / row 2 (%)",
    "row 3 / row 5 (%)",
    "row 4 / row 5 (%)"
]
ratio_names = [
    "Ratio of Apportioned to Originating Revenue (5/2)",
    "Ratio of Outward Retained Share to Originating Revenue (3/2)",
    "Ratio of Outward Retained Share to Total Apportioned Revenue (3/5)",
    "Ratio of Inward Share to Total Apportioned Revenue (4/5)"
]

# Create ratio dataframe with proper year ordering
ratio_df = df.loc[ratio_rows].copy()
ratio_df.index = ratio_names
year_columns = [year_labels[y] for y in table_years]
ratio_df = ratio_df[year_columns]  # Keep original year order

# Calculate average of last 5 years
for idx in ratio_df.index:
    vals = [v for v in ratio_df.loc[idx].values if v is not None and not pd.isna(v)]
    if vals:
        avg = sum(vals) / len(vals)
        ratio_df.loc[idx, "Avg of last 5 years"] = round(avg, 2)

# Format all numbers as percentages
for col in ratio_df.columns:
    ratio_df[col] = ratio_df[col].apply(lambda x: f"{x:.2f}%" if pd.notnull(x) else "")

ratio_df = ratio_df.reset_index()
ratio_df.rename(columns={'index': 'Ratio'}, inplace=True)

# Display tables with full width and no scroll
st.markdown("**Summary of Goods Traffic Pattern for the last four years as per FOIS RR Data for Carried Route (ST-7C)**")
st.dataframe(
    summary_df,
    use_container_width=True,
    hide_index=True,
    column_config={col: st.column_config.Column(width="auto") for col in summary_df.columns}
)

st.markdown("**Ratio**")
st.dataframe(
    ratio_df,
    use_container_width=True,
    hide_index=True,
    column_config={col: st.column_config.Column(width="auto") for col in ratio_df.columns}
)

# --- 📊 Bar Chart for Summary Table ---
st.markdown("### 📊 Summary Bar Chart")

            # 1️⃣ Multiply 'Loading' row values by 10 in all year columns
for col in summary_df.columns[1:-1]:  # Skip 'Particulars' and '% var w.r.t P.Y.'
            summary_df.loc[summary_df['Particulars'] == 'Loading', col] *= 10

        # 2️⃣ Melt the DataFrame (long format for Plotly)
summary_plot_df = summary_df.drop(columns=["% var w.r.t P.Y."])
summary_plot_df = summary_plot_df.melt(id_vars=["Particulars"], var_name="Year", value_name="Value")

        # 3️⃣ Convert Year to string (important for Plotly legend)
summary_plot_df["Year"] = summary_plot_df["Year"].astype(str)

        # 4️⃣ Plotly bar chart
fig = px.bar(
            summary_plot_df,
            x="Particulars",
            y="Value",
            color="Year",
            barmode="group",
            labels={"Value": "₹ in Crores"},
            title="Goods Traffic Summary by Year",
        )

fig.update_layout(
            xaxis_title="Particulars",
            yaxis_title="Revenue (₹ Cr)",
            height=500,
            legend_title="Year",
            plot_bgcolor='rgba(0,0,0,0)',
            bargap=0.25
        )

st.plotly_chart(fig, use_container_width=True)