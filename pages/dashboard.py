import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

st.title("Fraud Questions Dashboard")

# --- Auto-refresh every 10 seconds ---
from streamlit_autorefresh import st_autorefresh
st_autorefresh(interval=10 * 1000, key="dashboardrefresh")

# --- Connect to Google Sheets ---
SHEET_NAME = "fraud_results"  # Must match your spreadsheet title
TAB_NAME = "Sheet1"           # Must match your tab name

scope = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"], scopes=scope
)
client = gspread.authorize(creds)
sheet = client.open(SHEET_NAME).worksheet(TAB_NAME)

# --- Load all data from sheet ---
data = sheet.get_all_records()
if not data:
    st.warning("No results yet. Enter answers in the main app.")
else:
    df = pd.DataFrame(data)

    # --- Aggregate pass/fail counts per question ---
    summary = df.groupby("question_text")["result"].value_counts().unstack(fill_value=0)
    summary["Total"] = summary.sum(axis=1)
    summary = summary.reset_index().sort_values(by="Total", ascending=False)

    st.subheader("Pass/Fail Summary")
    st.dataframe(summary)

    # --- Optional: sho
