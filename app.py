import streamlit as st
import pandas as pd
from io import BytesIO

# Google Sheet CSV export link
SHEET_URL = "https://docs.google.com/spreadsheets/d/1UNosydITZa7zCzwoAelfIaYN-iz3li35G6QCmNuU1-U/export?format=csv&gid=0"

st.set_page_config(page_title="Mobilization Analysis", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv(SHEET_URL)
    if 'Timestamp' in df.columns:
        df['Timestamp'] = pd.to_datetime(df['Timestamp'], errors='coerce')
    return df

df_raw = load_data()

st.title("📊 Mobilization Data Analysis Dashboard")

# ---------------------------
# Deduplication
# ---------------------------
df_clean = df_raw.drop_duplicates(
    subset=['Verified ID Number(Verify before entry)', ' Phone Number(verify before entry)'],
    keep='first'
)

# ---------------------------
# Sidebar filters
# ---------------------------
st.sidebar.header("Filters")
counties = st.sidebar.multiselect("Select County", sorted(df_clean['County'].dropna().unique()))
date_range = st.sidebar.date_input("Select Date Range", [])

df_filtered = df_clean.copy()
if counties:
    df_filtered = df_filtered[df_filtered['County'].isin(counties)]
if date_range and len(date_range) == 2:
    start_date, end_date = pd.to_datetime(date_range)
    df_filtered = df_filtered[
        (df_filtered['Timestamp'] >= start_date) & (df_filtered['Timestamp'] <= end_date)
    ]

# ---------------------------
# Stats BEFORE filtering (raw data)
# ---------------------------
st.subheader("📍 Stats Before Deduplication (All Data)")
col1, col2, col3 = st.columns(3)
col1.metric("Total Records", len(df_raw))
col2.metric("Unique IDs", df_raw['Verified ID Number(Verify before entry)'].nunique())
col3.metric("Unique Phones", df_raw[' Phone Number(verify before entry)'].nunique())

# ---------------------------
# Stats AFTER deduplication (filtered data)
# ---------------------------
st.subheader("📍 Stats After Deduplication (Filtered)")
col1, col2, col3 = st.columns(3)
col1.metric("Total Records", len(df_filtered))
col2.metric("Unique IDs", df_filtered['Verified ID Number(Verify before entry)'].nunique())
col3.metric("Unique Phones", df_filtered[' Phone Number(verify before entry)'].nunique())

# ---------------------------
# County breakdown table & chart (filtered)
# ---------------------------
st.subheader("📍 County Breakdown (Filtered)")
county_counts = df_filtered['County'].value_counts().reset_index()
county_counts.columns = ['County', 'Count']
st.dataframe(county_counts)

st.bar_chart(county_counts.set_index('County'))

# ---------------------------
# Download: County Breakdown Excel
# ---------------------------
def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='County Breakdown')
    processed_data = output.getvalue()
    return processed_data

county_excel = to_excel(county_counts)

st.download_button(
    label="📥 Download County Breakdown (Excel)",
    data=county_excel,
    file_name="county_submission_counts.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

# ---------------------------
# Show filtered data table
# ---------------------------
st.subheader("📍 Filtered Participant Data")
st.dataframe(df_filtered)

# ---------------------------
# Download: Full Filtered Data
# ---------------------------
st.download_button(
    "📥 Download Full Filtered Data (CSV)",
    df_filtered.to_csv(index=False).encode('utf-8'),
    "filtered_mobilization_data.csv",
    "text/csv"
)
