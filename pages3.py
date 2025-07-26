import streamlit as st
import oracledb
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from testquery import DB_HOST, DB_PORT, DB_SID, DB_USER, DB_PASSWORD

# Streamlit UI
st.markdown(
    "<h3 style='text-align: center; color: black;'>SCENARIO-B: Estimated Apportioned Revenue Trend of Apportioned Revenue for the last Five Years as per Commodity wise traffic pattern from (APR - OCT) & (NOV - MAR) (Revenue in Crs.)</h3>",
    unsafe_allow_html=True
)

# st.title(" SCENARIO-B: Estimated Apportioned Revenue for 2023_24 Trend of Apportioned Revenue for the last Five Years as per Commodity wise traffic pattern from (APR - OCT) & (NOV - MAR) (Revenue in Crs.)")

# Year and Month Dropdowns
year_options = ["2017_18", "2018_19", "2019_20", "2020_21", "2021_22", "2022_23", "2023_24", "2024_25", "2025_26"]
month_map = {
    "April": "04", "May": "05", "June": "06", "July": "07", "August": "08",
    "September": "09", "October": "10", "November": "11", "December": "12",
    "January": "01", "February": "02", "March": "03"
}

selected_year_label = st.selectbox("Select Financial Year", year_options[5:])  # Default: 22-23 to 25-26
selected_month_label = st.selectbox("Select Month (April to March)", list(month_map.keys()))
selected_month_code = month_map[selected_month_label]

# Calculate display years for 5 years up to selected year
end_index = year_options.index(selected_year_label)
start_index = max(0, end_index - 5)
display_years = year_options[start_index:end_index + 1]

# ------------------- Helper Functions -------------------

def get_ranges(start_year, selected_code):
    apr_to_month, month_plus_to_mar = [], []
    for i in range(6):
        y = start_year + i
        ny = y + 1
        apr_to_month.append((y, f"{y}04", f"{y}{selected_code}", f"{ny}03"))
        next_m = int(selected_code) + 1
        sm = f"{y}{next_m:02d}" if next_m <= 12 else f"{ny}01"
        em = f"{ny}03"
        month_plus_to_mar.append((y, sm, em, f"{ny}03"))
    return apr_to_month, month_plus_to_mar

def build_table_query(ranges, fy_labels, selected_index):
    select_cols, total_cols, avg_exprs = [], [], []
    for i in range(5):
        fy, s, e, me = ranges[i]
        fy_lbl = fy_labels[i]
        rev_expr = f"SUM(CASE WHEN yymm BETWEEN '{s}' AND '{e}' THEN wr ELSE 0 END)"
        total_expr = f"SUM(CASE WHEN yymm BETWEEN '{fy}04' AND '{me}' THEN wr ELSE 0 END)"
        select_cols.append(f"ROUND({rev_expr}/10000000,2) AS \"{fy_lbl}\"")
        percent = f"ROUND({rev_expr}*100.0/NULLIF({total_expr},0),2)"
        select_cols.append(f"{percent} AS \"%{fy_lbl}\"")
        total_cols.append(f"ROUND({rev_expr}/10000000,2)")
        total_cols.append(percent)
        avg_exprs.append(percent)

    select_cols.append(f"ROUND(({'+'.join(avg_exprs)})/5,2) AS \"Avg 5 Year\"")
    total_cols.append(f"ROUND(({'+'.join(avg_exprs)})/5,2)")

    fy, s, e, me = ranges[selected_index]
    fy_lbl = fy_labels[selected_index]
    if fy_lbl not in fy_labels[:5]:
        rev_expr = f"SUM(CASE WHEN yymm BETWEEN '{s}' AND '{e}' THEN wr ELSE 0 END)"
        total_expr = f"SUM(CASE WHEN yymm BETWEEN '{fy}04' AND '{me}' THEN wr ELSE 0 END)"
        select_cols.append(f"ROUND({rev_expr}/10000000,2) AS \"{fy_lbl}\"")
        select_cols.append(f"ROUND({rev_expr}*100.0/NULLIF({total_expr},0),2) AS \"%{fy_lbl}\"")
        total_cols.append(f"ROUND({rev_expr}/10000000,2)")
        total_cols.append(f"ROUND({rev_expr}*100.0/NULLIF({total_expr},0),2)")
    return select_cols, total_cols

# ------------------- Build SQL -------------------

start_year = int(display_years[0].split("_")[0])
fy_labels = [f"{start_year + i}_{start_year + i + 1}" for i in range(6)]
r1, r2 = get_ranges(start_year, selected_month_code)
sel_idx = len(display_years) - 1
cols1, total1 = build_table_query(r1, fy_labels, sel_idx)
cols2, total2 = build_table_query(r2, fy_labels, sel_idx)

base_query = """
FROM (
    SELECT grp, wr, TO_CHAR(yymm) AS yymm
    FROM FOISGOODS.CARR_APMT_EXCL_ADV_17_18
    UNION ALL SELECT grp, wr, TO_CHAR(yymm) FROM FOISGOODS.CARR_APMT_EXCL_ADV_18_19
    UNION ALL SELECT grp, wr, TO_CHAR(yymm) FROM FOISGOODS.CARR_APMT_EXCL_ADV_19_20
    UNION ALL SELECT grp, wr, TO_CHAR(yymm) FROM FOISGOODS.CARR_APMT_EXCL_ADV_20_21
    UNION ALL SELECT grp, wr, TO_CHAR(yymm) FROM FOISGOODS.CARR_APMT_EXCL_ADV_21_22
    UNION ALL SELECT grp, wr, TO_CHAR(yymm) FROM FOISGOODS.CARR_APMT_EXCL_ADV_22_23
    UNION ALL SELECT grp, wr, TO_CHAR(yymm) FROM FOISGOODS.CARR_APMT_EXCL_ADV_23_24
    UNION ALL SELECT grp, wr, TO_CHAR(yymm) FROM FOISGOODS.CARR_APMT_EXCL_ADV_24_25
    UNION ALL SELECT grp, wr, TO_CHAR(yymm) FROM FOISGOODS.CARR_APMT_EXCL_ADV_25_26
)
WHERE grp IN ('01','02','03','04','05','06','07','08')
"""

sql1 = f"""
SELECT DECODE(grp,'01','CEMENT','02','COAL','03','CONTAINER','04','FERTILIZER',
              '05','FOOD GRAINS','06','IRON AND STEEL','07','OTHER GOODS','08','POL') AS COMMODITY,
    {", ".join(cols1)}
{base_query}
GROUP BY grp
UNION ALL
SELECT 'TOTAL', {", ".join(total1)}
{base_query}
"""

sql2 = f"""
SELECT DECODE(grp,'01','CEMENT','02','COAL','03','CONTAINER','04','FERTILIZER',
              '05','FOOD GRAINS','06','IRON AND STEEL','07','OTHER GOODS','08','POL') AS COMMODITY,
    {", ".join(cols2)}
{base_query}
GROUP BY grp
UNION ALL
SELECT 'TOTAL', {", ".join(total2)}
{base_query}
"""

# Table 3
year_percent_pairs = []
total_pairs = []
totals_cte_parts = []
for y in display_years:
    start_y, end_y = y.split("_")
    end_y_full = "20" + end_y
    case_expr = f"SUM(CASE WHEN yymm BETWEEN '{start_y}04' AND '{end_y_full}03' THEN wr ELSE 0 END)"
    year_percent_pairs.append(f"ROUND({case_expr}/10000000,2) AS \"{y}\"")
    year_percent_pairs.append(f"ROUND({case_expr}*100.0 / NULLIF((SELECT total_{y} FROM totals),0),2) AS \"%{y}\"")
    total_pairs.append(f"ROUND({case_expr}/10000000,2)")
    total_pairs.append("100")
    totals_cte_parts.append(f"{case_expr} AS total_{y}")
totals_cte = ", ".join(totals_cte_parts)
sql3 = f"""
WITH all_data AS (
    SELECT grp, wr, TO_CHAR(yymm) AS yymm FROM FOISGOODS.CARR_APMT_EXCL_ADV_17_18
    UNION ALL SELECT grp, wr, TO_CHAR(yymm) FROM FOISGOODS.CARR_APMT_EXCL_ADV_18_19
    UNION ALL SELECT grp, wr, TO_CHAR(yymm) FROM FOISGOODS.CARR_APMT_EXCL_ADV_19_20
    UNION ALL SELECT grp, wr, TO_CHAR(yymm) FROM FOISGOODS.CARR_APMT_EXCL_ADV_20_21
    UNION ALL SELECT grp, wr, TO_CHAR(yymm) FROM FOISGOODS.CARR_APMT_EXCL_ADV_21_22
    UNION ALL SELECT grp, wr, TO_CHAR(yymm) FROM FOISGOODS.CARR_APMT_EXCL_ADV_22_23
    UNION ALL SELECT grp, wr, TO_CHAR(yymm) FROM FOISGOODS.CARR_APMT_EXCL_ADV_23_24
    UNION ALL SELECT grp, wr, TO_CHAR(yymm) FROM FOISGOODS.CARR_APMT_EXCL_ADV_24_25
    UNION ALL SELECT grp, wr, TO_CHAR(yymm) FROM FOISGOODS.CARR_APMT_EXCL_ADV_25_26
),
totals AS (
    SELECT {totals_cte} FROM all_data
)
SELECT DECODE(grp,'01','CEMENT','02','COAL','03','CONTAINER','04','FERTILIZER',
              '05','FOOD GRAINS','06','IRON AND STEEL','07','OTHER GOODS','08','POL') AS COMMODITY,
    {', '.join(year_percent_pairs)}
FROM all_data
WHERE grp IN ('01','02','03','04','05','06','07','08')
GROUP BY grp
UNION ALL
SELECT 'TOTAL', {', '.join(total_pairs)}
FROM all_data
"""

# ------------------- Plotting Functions -------------------

def plot_table1(df):
    df_plot = df[df['COMMODITY'] != 'TOTAL']
    value_cols = [c for c in df_plot.columns if not c.startswith('%') and c not in ['COMMODITY', 'Avg 5 Year']]
    df_melt = df_plot.melt(id_vars="COMMODITY", value_vars=value_cols, var_name="Year", value_name="Revenue")
    fig = px.bar(df_melt, x="Year", y="Revenue", color="COMMODITY", barmode="group", title="Revenue by Commodity")
    st.plotly_chart(fig, use_container_width=True)

def plot_table2(df):
    df_plot = df[df['COMMODITY'] != 'TOTAL']
    value_cols = [c for c in df_plot.columns if not c.startswith('%') and c not in ['COMMODITY', 'Avg 5 Year']]
    df_melt = df_plot.melt(id_vars="COMMODITY", value_vars=value_cols, var_name="Year", value_name="Revenue")
    fig = px.line(df_melt, x="Year", y="Revenue", color="COMMODITY", markers=True, title="Revenue Trends")
    st.plotly_chart(fig, use_container_width=True)

def plot_table3(df):
    df_plot = df[df['COMMODITY'] != 'TOTAL']
    value_cols = [c for c in df_plot.columns if not c.startswith('%') and c not in ['COMMODITY', 'Avg 5 Year']]
    df_melt = df_plot.melt(id_vars="COMMODITY", value_vars=value_cols, var_name="Year", value_name="Revenue")
    fig = px.area(df_melt, x="Year", y="Revenue", color="COMMODITY", title="Stacked Area Revenue")
    st.plotly_chart(fig, use_container_width=True)

# ------------------- Execute & Display -------------------

try:
    with oracledb.connect(user=DB_USER, password=DB_PASSWORD, dsn=DSN) as conn:
        df1 = pd.read_sql(sql1, con=conn)
        df2 = pd.read_sql(sql2, con=conn)
        df3 = pd.read_sql(sql3, con=conn)

        st.subheader(f"Table 1: April to {selected_month_label} ({selected_year_label})")
        st.dataframe(df1)
        plot_table1(df1)

        st.subheader(f"Table 2: After {selected_month_label} to March ({selected_year_label})")
        st.dataframe(df2)
        plot_table2(df2)

        st.subheader(f"Table 3: Full Year {display_years[0]} to {display_years[-1]}")
        st.dataframe(df3)
        plot_table3(df3)

except Exception as e:
    st.error(f"❌ Error: {e}")