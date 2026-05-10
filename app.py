import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="University Student Dashboard",
    page_icon="🎓",
    layout="wide"
)

@st.cache_data
def load_data():
    df = pd.read_csv("university_student_data.csv")
    return df

df = load_data()

st.title("🎓 University Student Data Dashboard")
st.markdown(
    "Interactive dashboard for analyzing applications, enrollment, retention, "
    "student satisfaction, and departmental enrollment."
)

# -----------------------------
# Sidebar filters
# -----------------------------
st.sidebar.header("Filters")

available_years = sorted(df["Year"].unique().tolist())
selected_years = st.sidebar.multiselect(
    "Select year(s)",
    options=available_years,
    default=available_years
)

available_terms = sorted(df["Term"].unique().tolist())
selected_terms = st.sidebar.multiselect(
    "Select term(s)",
    options=available_terms,
    default=available_terms
)

department_columns = {
    "Engineering": "Engineering Enrolled",
    "Business": "Business Enrolled",
    "Arts": "Arts Enrolled",
    "Science": "Science Enrolled"
}
selected_departments = st.sidebar.multiselect(
    "Select department(s)",
    options=list(department_columns.keys()),
    default=list(department_columns.keys())
)

# Avoid empty filters
if not selected_years:
    selected_years = available_years
if not selected_terms:
    selected_terms = available_terms
if not selected_departments:
    selected_departments = list(department_columns.keys())

filtered_df = df[
    (df["Year"].isin(selected_years)) &
    (df["Term"].isin(selected_terms))
].copy()

# -----------------------------
# KPI cards
# -----------------------------
st.subheader("Key Performance Indicators")

kpi_1, kpi_2, kpi_3, kpi_4, kpi_5 = st.columns(5)

kpi_1.metric("Applications", f"{filtered_df['Applications'].sum():,}")
kpi_2.metric("Admitted", f"{filtered_df['Admitted'].sum():,}")
kpi_3.metric("Enrolled", f"{filtered_df['Enrolled'].sum():,}")
kpi_4.metric("Avg. Retention", f"{filtered_df['Retention Rate (%)'].mean():.1f}%")
kpi_5.metric("Avg. Satisfaction", f"{filtered_df['Student Satisfaction (%)'].mean():.1f}%")

st.divider()

# -----------------------------
# Main visualizations
# -----------------------------
left_col, right_col = st.columns(2)

# 1. Line chart: retention trend over time
retention_by_year = (
    filtered_df.groupby("Year", as_index=False)["Retention Rate (%)"]
    .mean()
)

fig_retention = px.line(
    retention_by_year,
    x="Year",
    y="Retention Rate (%)",
    markers=True,
    title="Retention Rate Trend Over Time"
)
fig_retention.update_layout(yaxis_title="Retention Rate (%)")
left_col.plotly_chart(fig_retention, use_container_width=True)

# 2. Bar chart: student satisfaction by year
satisfaction_by_year = (
    filtered_df.groupby("Year", as_index=False)["Student Satisfaction (%)"]
    .mean()
)

fig_satisfaction = px.bar(
    satisfaction_by_year,
    x="Year",
    y="Student Satisfaction (%)",
    title="Student Satisfaction by Year"
)
fig_satisfaction.update_layout(yaxis_title="Student Satisfaction (%)")
right_col.plotly_chart(fig_satisfaction, use_container_width=True)

left_col2, right_col2 = st.columns(2)

# 3. Grouped bar chart: comparison between Spring and Fall
term_comparison = (
    filtered_df.groupby("Term", as_index=False)
    .agg({
        "Applications": "sum",
        "Admitted": "sum",
        "Enrolled": "sum"
    })
    .melt(
        id_vars="Term",
        value_vars=["Applications", "Admitted", "Enrolled"],
        var_name="Indicator",
        value_name="Total"
    )
)

fig_terms = px.bar(
    term_comparison,
    x="Term",
    y="Total",
    color="Indicator",
    barmode="group",
    title="Comparison Between Spring and Fall Terms"
)
left_col2.plotly_chart(fig_terms, use_container_width=True)

# 4. Donut chart: selected department enrollment
dept_totals = pd.DataFrame({
    "Department": selected_departments,
    "Enrolled": [
        filtered_df[department_columns[dept]].sum()
        for dept in selected_departments
    ]
})

fig_departments = px.pie(
    dept_totals,
    names="Department",
    values="Enrolled",
    hole=0.45,
    title="Enrollment Distribution by Department"
)
right_col2.plotly_chart(fig_departments, use_container_width=True)

# -----------------------------
# Supporting table
# -----------------------------
st.subheader("Filtered Data")
st.dataframe(filtered_df, use_container_width=True)

# -----------------------------
# Short interpretation
# -----------------------------
st.subheader("Interpretation")
st.write(
    "Use the filters to explore how the indicators behave across years and terms. "
    "The dashboard helps identify long-term trends in retention and satisfaction, "
    "compare Spring and Fall performance, and observe the distribution of students "
    "across departments."
)
