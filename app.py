import streamlit as st
import pandas as pd

# Google Sheet CSV export link
SHEET_URL = "https://docs.google.com/spreadsheets/d/1UNosydITZa7zCzwoAelfIaYN-iz3li35G6QCmNuU1-U/export?format=csv&gid=0"

st.set_page_config(page_title="Mobilization Analysis", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv(SHEET_URL)
    # Ensure date column is datetime if present
    if 'Timestamp' in df.columns:
        df['Timestamp'] = pd.to_datetime(df['Timestamp'], errors='coerce')
    return df

df_raw = load_data()

st.title("📊 Mobilization Data Analysis Dashboard")

# ---------------------------
# Stats before deduplication
# ---------------------------
st.subheader("Data Overview (Before Deduplication)")
col1, col2, col3 = st.columns(3)
col1.metric("Total Records", len(df_raw))
col2.metric("Unique IDs", df_raw['Verified ID Number(Verify before entry)'].nunique())
col3.metric("Unique Phones", df_raw[' Phone Number(verify before entry)'].nunique())

# ---------------------------
# Deduplication
# ---------------------------
df_clean = df_raw.drop_duplicates(
    subset=['Verified ID Number(Verify before entry)', ' Phone Number(verify before entry)'],
    keep='first'
)

# ---------------------------
# Stats after deduplication
# ---------------------------
st.subheader("Data Overview (After Deduplication)")
col1, col2, col3 = st.columns(3)
col1.metric("Total Records", len(df_clean))
col2.metric("Unique IDs", df_clean['Verified ID Number(Verify before entry)'].nunique())
col3.metric("Unique Phones", df_clean[' Phone Number(verify before entry)'].nunique())

# ---------------------------
# Filters
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
# County breakdown chart
# ---------------------------
st.subheader("County Breakdown")
county_counts = df_filtered['County'].value_counts().reset_index()
county_counts.columns = ['County', 'Count']

st.bar_chart(county_counts.set_index('County'))

# ---------------------------
# Show filtered data
# ---------------------------
st.subheader("Filtered Data")
st.dataframe(df_filtered)

# ---------------------------
# Download options
# ---------------------------
st.download_button(
    "Download Clean Data as CSV",
    df_clean.to_csv(index=False).encode('utf-8'),
    "clean_mobilization_data.csv",
    "text/csv"
)
