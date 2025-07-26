import streamlit as st
import pandas as pd
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import seaborn as sns
import oracledb
import plotly.express as px
import plotly.graph_objects as go
import re
from testquery import DB_HOST, DB_PORT, DB_SID, DB_USER, DB_PASSWORD

# Set page layout
st.set_page_config(layout="wide")
st.markdown("""
            <style>
                .main {
                    background-color: #f8fafc;
                }
                .header {
                    padding: 1rem 0;
                    border-bottom: 1px solid #e2e8f0;
                    margin-bottom: 2rem;
                }
                .metric-card {
                    background-color: white;
                    padding: 1rem;
                    border-radius: 8px;
                    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                    margin-bottom: 1rem;
                }
                .metric-title {
                    color: #64748b;
                    font-size: 0.875rem;
                    font-weight: 500;
                }
                .metric-value {
                    color: #1e40af;
                    font-size: 1.5rem;
                    font-weight: 600;
                    margin: 0.5rem 0;
                }
                .metric-change {
                    color: #64748b;
                    font-size: 0.75rem;
                }
            </style>
        """, unsafe_allow_html=True)

st.markdown("""
            <div class="header">
                <h1 style="color: #1e40af; margin-bottom: 0.5rem;">Railway Revenue Analytics by Commodity Group</h1>
                <p style="color: #64748b; margin-top: 0;">Analysis of apportioned revenue by major commodity groups</p>
            </div>
        """, unsafe_allow_html=True)
# Define fiscal years and month mappings
years = ["25_26", "24_25", "23_24", "22_23", "21_22", "20_21", "19_20", "18_19", "17_18"]
year_labels = {
    "25_26": "2025-26", "24_25": "2024-25", "23_24": "2023-24",
    "22_23": "2022-23", "21_22": "2021-22", "20_21": "2020-21",
    "19_20": "2019-20", "18_19": "2018-19", "17_18": "2017-18"
}
dropdown_years = ["25_26", "24_25", "23_24", "22_23"]
months = {
    "April": "04", "May": "05", "June": "06", "July": "07", "August": "08",
    "September": "09", "October": "10", "November": "11", "December": "12",
    "January": "01", "February": "02", "March": "03"
}

# Select fiscal year and month
col1, col2 = st.columns(2)
with col1:
    selected_year = st.selectbox("Select Fiscal Year", [year_labels[y] for y in dropdown_years], index=1)
    selected_year_code = [k for k, v in year_labels.items() if v == selected_year][0]
with col2:
    selected_month = st.selectbox("Select Month", list(months.keys()), index=3)

start_year = int(f"20{selected_year_code[:2]}")
end_year = int(f"20{selected_year_code[3:]}")

# Create year range and label
previous_years = [(start_year - i - 1, start_year - i) for i in reversed(range(5))]
previous_year_labels = [f"{y1}-{str(y2)[-2:]}" for y1, y2 in previous_years]

month_year_label = f"{selected_month} {selected_year_code[-2:]}"

# Define table names
table_list = [f"FOISGOODS.CARR_APMT_EXCL_ADV_{code}" for code in years]

# Commodity mappings
commodity_map = {
    "01": "Cement", "02": "Coal", "03": "Container", "04": "Fertilizers",
    "05": "Food Grains", "06": "Iron & Steel", "07": "Other Goods", "08": "Pol"
}

def table_has_column(table_name, column_name):
    try:
        dsn = oracledb.makedsn(DB_HOST, DB_PORT, sid=DB_SID)
        conn = oracledb.connect(user=DB_USER, password=DB_PASSWORD, dsn=dsn)
        query = f"""
        SELECT COUNT(*) FROM ALL_TAB_COLUMNS
        WHERE TABLE_NAME = '{table_name.split('.')[-1].upper()}'
        AND OWNER = '{table_name.split('.')[0].upper()}'
        AND COLUMN_NAME = '{column_name.upper()}'
        """
        df = pd.read_sql(query, con=conn)
        return df.iloc[0, 0] > 0
    except Exception as e:
        st.error(f"Error checking column in {table_name}: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

selected_month_index = list(months.keys()).index(selected_month)
months_to_include = list(months.items())[:selected_month_index + 1]
cumulative_months_YYMM = [f"{start_year}{m_code}" for m_name, m_code in months_to_include]
cumulative_months_clause = ", ".join(f"'{m}'" for m in cumulative_months_YYMM)

# ---------- Query Function ----------
def run_query(metric_sql_expr, column_name, scale_divisor=1e6, for_table3=False):
    # Dynamically filter tables that contain the required column
    valid_tables = [tbl for tbl in table_list if table_has_column(tbl, column_name)]
    if not valid_tables:
        st.warning(f"No tables found with column: {column_name}")
        return pd.DataFrame()

    previous_year_sql = ",\n        ".join([
    f"""ROUND(SUM(CASE WHEN YYMM BETWEEN '{y1}04' AND '{y2}03' THEN VALUE ELSE 0 END)/{scale_divisor}, 3) AS \"{y1}-{str(y2)[-2:]}\""""
    for y1, y2 in previous_years
    ])


    with_clause = " UNION ALL ".join([
        f"SELECT GRP, {metric_sql_expr} AS VALUE, TO_CHAR(YYMM) AS YYMM, ZONE_FRM FROM {tbl}"
        for tbl in valid_tables
    ])

    if for_table3:
        query = f"""
        WITH all_data AS (
            {with_clause}
        ),
        main_data AS (
            SELECT 
                GRP AS COMMODITY,
                {previous_year_sql},
                ROUND(SUM(CASE WHEN YYMM IN ({cumulative_months_clause}) THEN VALUE ELSE 0 END)/{scale_divisor}, 3) AS "Selected_Month",
                ROUND(SUM(CASE WHEN YYMM BETWEEN '{start_year}04' AND '{end_year}03' THEN VALUE ELSE 0 END)/{scale_divisor}, 3) AS "Selected_Year_Total"
            FROM all_data
            WHERE GRP IS NOT NULL
            GROUP BY GRP
        ),
        final_data AS (
            SELECT 
                COMMODITY,
                {', '.join([f'"{label}"' for label in previous_year_labels])},
                "Selected_Month",
                "Selected_Year_Total"
            FROM main_data
        )
        SELECT * FROM final_data
        ORDER BY COMMODITY
        """
    else:
        query = f"""
        WITH all_data AS (
            {with_clause}
        ),
        main_data AS (
            SELECT 
                GRP AS COMMODITY,
                {previous_year_sql},
                ROUND(SUM(CASE WHEN YYMM IN ({cumulative_months_clause}) THEN VALUE ELSE 0 END)/{scale_divisor}, 3) AS "Selected_Month",
                ROUND(SUM(CASE WHEN YYMM BETWEEN '{start_year}04' AND '{end_year}03' THEN VALUE ELSE 0 END)/{scale_divisor}, 3) AS "Selected_Year_Total"
            FROM all_data
            WHERE ZONE_FRM = 'WR' AND GRP IS NOT NULL
            GROUP BY GRP
        )
        SELECT * FROM main_data ORDER BY COMMODITY
        """

    
    
    try:
        dsn = oracledb.makedsn(DB_HOST, DB_PORT, sid=DB_SID)
        conn = oracledb.connect(user=DB_USER, password=DB_PASSWORD, dsn=dsn)
        df = pd.read_sql(query, con=conn)
        return df
    except Exception as e:
        st.error(f"Database error: {e}")
        return pd.DataFrame()
    finally:
        if 'conn' in locals():
            conn.close()

# ---------- Display Function ----------
def display_table(df, title):
    if df.empty:
        st.warning("No data to display.")
        return

    df["COMMODITY"] = df["COMMODITY"].map(commodity_map).fillna(df["COMMODITY"])
    df = df.rename(columns={"Selected_Month": month_year_label})
    df = df.drop(columns=["Selected_Year_Total"], errors="ignore")
    
    total_selected_month = df[month_year_label].sum()
    percentage_column_label = f"% W.R.T Total (upto {selected_year})"
    if total_selected_month != 0:
        df[percentage_column_label] = (df[month_year_label] / total_selected_month) * 100
    else:
        df[percentage_column_label] = 0.0

    float_cols = df.select_dtypes(include='float').columns
    format_dict = {col: "{:.3f}" for col in float_cols}
    if percentage_column_label in df.columns:
        format_dict[percentage_column_label] = "{:.2f}%"

    totals = df.select_dtypes(include='number').sum(numeric_only=True)
    totals["COMMODITY"] = "Total"
    df = pd.concat([df, pd.DataFrame([totals])], ignore_index=True)

    st.markdown(title)
    st.dataframe(df.style.format(format_dict, na_rep="—"), use_container_width=True, hide_index=True)

# ---------- Table 1: CHBL_WGHT ----------
df1 = run_query("TO_NUMBER(CHBL_WGHT)", "CHBL_WGHT")
display_table(df1, "### Table 1: WR Apportioned vs Originating Freight (CHBL_WGHT)")
df1 = df1.rename(columns={"Selected_Month": month_year_label})

summary_df = df1[df1["COMMODITY"] != "Total"].copy()

# Extract fiscal year columns
year_columns = [col for col in summary_df.columns if re.match(r"\d{4}-\d{2}", col)]

# Melt for long-form format
summary_plot_df = summary_df.melt(
    id_vars="COMMODITY",
    value_vars=year_columns,
    var_name="Year",
    value_name="Value"
)

# Optional: Sort Year properly
summary_plot_df["Year"] = pd.Categorical(summary_plot_df["Year"], categories=year_columns, ordered=True)


# ----- 📊 Bar Chart (Plotly) -----
st.markdown("#### 📊 Bar Chart: Freight Over Previous 5 Fiscal Years")

fig1 = px.bar(
    summary_plot_df,
    x="Year",
    y="Value",
    color="COMMODITY",
    barmode="group",
    labels={"Value": "Freight (in Million Tonnes)"},
    title="Freight Comparison by Commodity (Last 5 Fiscal Years)"
)

fig1.update_layout(
    xaxis_title="Fiscal Year",
    yaxis_title="Freight (in Million Tonnes)",
    height=500,
    legend_title="Commodity",
    plot_bgcolor='rgba(0,0,0,0)',
    bargap=0.25
)

st.plotly_chart(fig1, use_container_width=True)

# ----- 🥧 Pie Chart (Plotly) -----
month_col = month_year_label
total_selected_month = df1[df1["COMMODITY"] != "Total"][month_col].sum()

df1_no_total = df1[df1["COMMODITY"] != "Total"].copy()
df1_no_total["Percentage"] = (df1_no_total[month_col] / total_selected_month) * 100 if total_selected_month else 0

st.markdown(f"#### 🥧 Pie Chart: Share for {month_year_label}")

fig2 = px.pie(
    df1_no_total,
    names="COMMODITY",
    values="Percentage",
    title=f"Commodity Share - {month_year_label}",
    hole=0.3  # optional donut style
)

fig2.update_traces(textinfo='percent+label')
fig2.update_layout(
    height=500,
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    legend_title="Commodity"
)

st.plotly_chart(fig2, use_container_width=True)

# ----- 📈 Line Chart (Plotly) -----
st.markdown("#### 📈 Line Chart: Trend of Freight by Commodity")

fig3 = px.line(
    summary_plot_df,
    x="Year",
    y="Value",
    color="COMMODITY",
    markers=True,
    labels={"Value": "Freight (in Million Tonnes)", "Year": "Fiscal Year"},
    title="Freight Trend Over Years"
)

fig3.update_layout(
    xaxis_title="Fiscal Year",
    yaxis_title="Freight (in Million Tonnes)",
    height=500,
    plot_bgcolor='rgba(0,0,0,0)',
    legend_title="Commodity"
)

st.plotly_chart(fig3, use_container_width=True)

# ---------- Table 2: FREIGHT ----------
df2 = run_query("TOT_FRT_INCL_GST - TOT_GST", "TOT_GST", scale_divisor=1e7)
display_table(df2, "### Table 2: WR Apportioned vs Originating Freight (Freight without GST)")
df2 = df2.rename(columns={"Selected_Month": month_year_label})

# Prepare the data
summary_df = df2[df2["COMMODITY"] != "Total"].copy()

# Extract fiscal year columns
year_columns = [col for col in summary_df.columns if re.match(r"\d{4}-\d{2}", col)]

# Melt for long-form format
summary_plot_df = summary_df.melt(
    id_vars="COMMODITY",
    value_vars=year_columns,
    var_name="Year",
    value_name="Value"
)

# Optional: Sort Year properly
summary_plot_df["Year"] = pd.Categorical(summary_plot_df["Year"], categories=year_columns, ordered=True)


# ----- 📊 Bar Chart (Plotly) -----
st.markdown("#### 📊 Bar Chart: Freight Over Previous 5 Fiscal Years")

fig1 = px.bar(
    summary_plot_df,
    x="Year",
    y="Value",
    color="COMMODITY",
    barmode="group",
    labels={"Value": "Freight (in Million Tonnes)"},
    title="Freight Comparison by Commodity (Last 5 Fiscal Years)"
)

fig1.update_layout(
    xaxis_title="Fiscal Year",
    yaxis_title="Freight (in Million Tonnes)",
    height=500,
    legend_title="Commodity",
    plot_bgcolor='rgba(0,0,0,0)',
    bargap=0.25
)

st.plotly_chart(fig1, use_container_width=True)

# ----- 🥧 Pie Chart (Plotly) -----
month_col = month_year_label
total_selected_month = df2[df2["COMMODITY"] != "Total"][month_col].sum()

df2_no_total = df2[df2["COMMODITY"] != "Total"].copy()
df2_no_total["Percentage"] = (df2_no_total[month_col] / total_selected_month) * 100 if total_selected_month else 0

st.markdown(f"#### 🥧 Pie Chart: Share for {month_year_label}")

fig2 = px.pie(
    df2_no_total,
    names="COMMODITY",
    values="Percentage",
    title=f"Commodity Share - {month_year_label}",
    hole=0.3  # optional donut style
)

fig2.update_traces(textinfo='percent+label')
fig2.update_layout(
    height=500,
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    legend_title="Commodity"
)

st.plotly_chart(fig2, use_container_width=True)

# ----- 📈 Line Chart (Plotly) -----
st.markdown("#### 📈 Line Chart: Trend of Freight by Commodity")

fig3 = px.line(
    summary_plot_df,
    x="Year",
    y="Value",
    color="COMMODITY",
    markers=True,
    labels={"Value": "Freight (in Million Tonnes)", "Year": "Fiscal Year"},
    title="Freight Trend Over Years"
)

fig3.update_layout(
    xaxis_title="Fiscal Year",
    yaxis_title="Freight (in Million Tonnes)",
    height=500,
    plot_bgcolor='rgba(0,0,0,0)',
    legend_title="Commodity"
)

st.plotly_chart(fig3, use_container_width=True)
# ---------- Table 3: WR ----------
df3 = run_query("TO_NUMBER(WR)", "WR", scale_divisor=1e7, for_table3=True)
display_table(df3, "### Table 3: WR Apportioned vs Originating Freight (WR)")
df3 = df3.rename(columns={"Selected_Month": month_year_label})

# Prepare data
summary_df = df3[df3["COMMODITY"] != "Total"].copy()

# Extract fiscal year columns
year_columns = [col for col in summary_df.columns if re.match(r"\d{4}-\d{2}", col)]

# Melt for long-form format
summary_plot_df = summary_df.melt(
    id_vars="COMMODITY",
    value_vars=year_columns,
    var_name="Year",
    value_name="Value"
)

# Optional: Sort Year properly
summary_plot_df["Year"] = pd.Categorical(summary_plot_df["Year"], categories=year_columns, ordered=True)


# ----- 📊 Bar Chart (Plotly) -----
st.markdown("#### 📊 Bar Chart: Freight Over Previous 5 Fiscal Years")

fig1 = px.bar(
    summary_plot_df,
    x="Year",
    y="Value",
    color="COMMODITY",
    barmode="group",
    labels={"Value": "Freight (in Million Tonnes)"},
    title="Freight Comparison by Commodity (Last 5 Fiscal Years)"
)

fig1.update_layout(
    xaxis_title="Fiscal Year",
    yaxis_title="Freight (in Million Tonnes)",
    height=500,
    legend_title="Commodity",
    plot_bgcolor='rgba(0,0,0,0)',
    bargap=0.25
)

st.plotly_chart(fig1, use_container_width=True)

# ----- 🥧 Pie Chart (Plotly) -----
month_col = month_year_label
total_selected_month = df3[df3["COMMODITY"] != "Total"][month_col].sum()

df3_no_total = df3[df3["COMMODITY"] != "Total"].copy()
df3_no_total["Percentage"] = (df3_no_total[month_col] / total_selected_month) * 100 if total_selected_month else 0

st.markdown(f"#### 🥧 Pie Chart: Share for {month_year_label}")

fig2 = px.pie(
    df3_no_total,
    names="COMMODITY",
    values="Percentage",
    title=f"Commodity Share - {month_year_label}",
    hole=0.3  # optional donut style
)

fig2.update_traces(textinfo='percent+label')
fig2.update_layout(
    height=500,
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    legend_title="Commodity"
)

st.plotly_chart(fig2, use_container_width=True)

# ----- 📈 Line Chart (Plotly) -----
st.markdown("#### 📈 Line Chart: Trend of Freight by Commodity")

fig3 = px.line(
    summary_plot_df,
    x="Year",
    y="Value",
    color="COMMODITY",
    markers=True,
    labels={"Value": "Freight (in Million Tonnes)", "Year": "Fiscal Year"},
    title="Freight Trend Over Years"
)

fig3.update_layout(
    xaxis_title="Fiscal Year",
    yaxis_title="Freight (in Million Tonnes)",
    height=500,
    plot_bgcolor='rgba(0,0,0,0)',
    legend_title="Commodity"
)

st.plotly_chart(fig3, use_container_width=True)

# ---------- Table 4: Ratio of WR to Freight (Table 3 / Table 2) ----------


df3_ratio = df3[df3["COMMODITY"] != "Total"].copy()
df2_ratio = df2[df2["COMMODITY"] != "Total"].copy()

merged_df = pd.merge(df3_ratio, df2_ratio, on="COMMODITY", suffixes=("_WR", "_FRT"))

# Identify year columns (e.g., "2019-20", "2020-21", ... and Month-Year column)
year_columns = [col for col in df3.columns if re.match(r"\d{4}-\d{2}", col)]
if month_year_label in df3.columns:
    year_columns.append(month_year_label)

# ----- Step 2: Calculate Ratio -----

ratio_df = pd.DataFrame()
ratio_df["COMMODITY"] = merged_df["COMMODITY"]

for col in year_columns:
    wr_col = f"{col}_WR"
    frt_col = f"{col}_FRT"
    if wr_col in merged_df.columns and frt_col in merged_df.columns:
        ratio = merged_df[wr_col] / merged_df[frt_col]
        ratio_df[col] = ratio.replace([np.inf, -np.inf], np.nan).fillna(0) * 100  # Convert to %
    else:
        ratio_df[col] = 0

# ----- Step 3: Add Average Column -----

avg_col_name = "Avg last 4 years"
ratio_df[avg_col_name] = ratio_df[year_columns[-4:]].mean(axis=1)

# ----- Step 4: Add Total/Average Row -----
# ----- Step 4: Add 'Total' Row as Table 3 Total / Table 2 Total -----

# Get the total rows from df3 and df2
# Normalize COMMODITY values
# Create normalized copies
df3_norm = df3.copy()
df2_norm = df2.copy()
df3_norm["COMMODITY"] = df3_norm["COMMODITY"].astype(str).str.strip().str.lower()
df2_norm["COMMODITY"] = df2_norm["COMMODITY"].astype(str).str.strip().str.lower()

# Extract total rows
total_row_df3 = df3[df3_norm["COMMODITY"] == "total"]
total_row_df2 = df2[df2_norm["COMMODITY"] == "total"]

# Optional: fallback to computed totals
if total_row_df3.empty:
    total_row_df3 = pd.DataFrame([{
        "COMMODITY": "Total",
        **{col: df3[col].sum() for col in year_columns if col in df3.columns}
    }])

if total_row_df2.empty:
    total_row_df2 = pd.DataFrame([{
        "COMMODITY": "Total",
        **{col: df2[col].sum() for col in year_columns if col in df2.columns}
    }])

# Warning (optional, still helpful to keep)
if total_row_df3.empty or total_row_df2.empty:
    st.warning("Missing 'Total' row in df3 or df2 — Total row in Table 4 will show zeros.")

# ✅ Initialize this before the loop
total_ratio_row = {"COMMODITY": "Total"}

# Compute ratio
for col in year_columns:
    if not total_row_df3.empty and not total_row_df2.empty:
        wr_total = total_row_df3[col].values[0] if col in total_row_df3.columns else 0
        frt_total = total_row_df2[col].values[0] if col in total_row_df2.columns else 0
        ratio = (wr_total / frt_total) * 100 if frt_total != 0 else 0
    else:
        ratio = 0
    total_ratio_row[col] = ratio

# Avg of last 4 years
total_ratio_row[avg_col_name] = np.mean([total_ratio_row[col] for col in year_columns[-4:]])

# Append total row
ratio_df = pd.concat([ratio_df, pd.DataFrame([total_ratio_row])], ignore_index=True)


# ----- Step 5: Display with Styling -----

def highlight_ratios(val):
    try:
        val_float = float(val)
        if val_float > 50:
            color = "green"
        elif val_float < 50:
            color = "red"
        else:
            color = "black"
        return f"color: {color}"
    except:
        return ""

# Format to percentage with 2 decimals
fmt = {col: "{:.2f}%" for col in ratio_df.columns if col != "COMMODITY"}

st.markdown("### Table 4: WR to Freight Ratio (%)")
st.dataframe(
    ratio_df.style
    .format(fmt)
    .applymap(highlight_ratios, subset=ratio_df.columns[1:]),
    use_container_width=True,
    hide_index=True
)

# ----- 🎯 Graphical Representation of Table 4: WR to Freight Ratio (%) -----

# Exclude 'Total' row for plotting
ratio_plot_df = ratio_df[ratio_df["COMMODITY"] != "Total"].copy()

# Melt the ratio_df for long format
ratio_long_df = ratio_plot_df.melt(
    id_vars="COMMODITY",
    value_vars=year_columns,  # Only fiscal years, not "Avg last 4 years"
    var_name="Year",
    value_name="Ratio (%)"
)

# Ensure 'Year' is properly ordered
ratio_long_df["Year"] = pd.Categorical(ratio_long_df["Year"], categories=year_columns, ordered=True)

# ----- 📊 Bar Chart: WR to Freight Ratio by Commodity -----
st.markdown("#### 📊 Bar Chart: WR to Freight Ratio by Commodity (Last Fiscal Years)")

fig_bar = px.bar(
    ratio_long_df,
    x="Year",
    y="Ratio (%)",
    color="COMMODITY",
    barmode="group",
    title="WR to Freight Ratio (%) by Commodity over Fiscal Years"
)

fig_bar.update_layout(
    xaxis_title="Fiscal Year",
    yaxis_title="WR to Freight Ratio (%)",
    height=500,
    legend_title="Commodity",
    plot_bgcolor='rgba(0,0,0,0)',
    bargap=0.25
)

st.plotly_chart(fig_bar, use_container_width=True)

# ----- 📈 Line Chart: WR to Freight Ratio Trend -----
st.markdown("#### 📈 Line Chart: WR to Freight Ratio Trend")

fig_line = px.line(
    ratio_long_df,
    x="Year",
    y="Ratio (%)",
    color="COMMODITY",
    markers=True,
    title="Trend of WR to Freight Ratio (%) by Commodity"
)

fig_line.update_layout(
    xaxis_title="Fiscal Year",
    yaxis_title="WR to Freight Ratio (%)",
    height=500,
    plot_bgcolor='rgba(0,0,0,0)',
    legend_title="Commodity"
)

st.plotly_chart(fig_line, use_container_width=True)