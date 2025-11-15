import streamlit as st
import pandas as pd
import time

# Refresh every 10 seconds
st_autorefresh = st.experimental_rerun
st_autorefresh_interval = 10  # seconds

if "last_refresh" not in st.session_state:
    st.session_state["last_refresh"] = time.time()
else:
    if time.time() - st.session_state["last_refresh"] > st_autorefresh_interval:
        st.session_state["last_refresh"] = time.time()
        st.experimental_rerun()


st.title("Security Question Dashboard 📊")

# Load results
import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# Connect to Google Sheets
scope = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"], scopes=scope
)
client = gspread.authorize(creds)

SHEET_NAME = "fraud_results"
sheet = client.open(SHEET_NAME).Sheet1

# Load all data
data = sheet.get_all_records()
df = pd.DataFrame(data)

st.title("Fraud Question Dashboard")
st.dataframe(df)

if not df.empty:
    pass_rate = (df["result"].str.lower() == "pass").mean() * 100
    st.metric("Overall Pass Rate", f"{pass_rate:.1f}%")


# --- Basic stats ---
st.subheader("Overall Summary")
total = len(df)
pass_count = len(df[df['result'] == 'Pass'])
fail_count = len(df[df['result'] == 'Fail'])
pass_rate = round(pass_count / total * 100, 1)

col1, col2, col3 = st.columns(3)
col1.metric("Total Responses", total)
col2.metric("Pass Rate", f"{pass_rate}%")
col3.metric("Fail Rate", f"{round(100 - pass_rate, 1)}%")

st.markdown("---")

# --- Pass/Fail rate per question ---
st.subheader("Pass/Fail Rate by Question")

agg = df.groupby(['question_text', 'category', 'result']).size().unstack(fill_value=0)
agg['Total'] = agg.sum(axis=1)
agg['Pass Rate (%)'] = (agg['Pass'] / agg['Total'] * 100).round(1)
agg = agg.reset_index()

st.dataframe(agg, use_container_width=True)

# --- Visualization ---
st.subheader("Pass Rate by Question")
st.bar_chart(agg.set_index('question_text')['Pass Rate (%)'])

st.markdown("---")

# --- Category-level summary ---
st.subheader("Pass Rate by Category")
cat_summary = df.groupby(['category', 'result']).size().unstack(fill_value=0)
cat_summary['Total'] = cat_summary.sum(axis=1)
cat_summary['Pass Rate (%)'] = (cat_summary['Pass'] / cat_summary['Total'] * 100).round(1)

st.dataframe(cat_summary, use_container_width=True)
st.bar_chart(cat_summary['Pass Rate (%)'])