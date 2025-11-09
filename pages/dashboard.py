import streamlit as st
import pandas as pd

st.title("Security Question Dashboard 📊")

# Load results
@st.cache_data
def load_results():
    try:
        df = pd.read_csv("results.csv")
        return df
    except FileNotFoundError:
        st.error("No results.csv file found yet. Please complete some verifications first.")
        return pd.DataFrame()

df = load_results()

if df.empty:
    st.info("No data yet — once you have saved some results, theyll appear here.")
    st.stop()

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