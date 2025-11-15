import streamlit as st
import pandas as pd
import random
import datetime
import os

st.title("Euan's Question Generator")

# --- Load questions from CSV ---
@st.cache_data
def load_questions():
    df = pd.read_csv("questions.csv")
    return df

questions = load_questions()

if questions.empty:
    st.error("No questions found in CSV. Please check your file.")
    st.stop()

st.write(f"Loaded {len(questions)} questions across categories: {questions['category'].unique().tolist()}")

# --- Select one question from each category ---
if st.button("Select Questions"):
    selected_questions = []

    for cat in ["account", "personal", "APP"]:
        subset = questions[questions["category"].str.lower() == cat.lower()]
        if not subset.empty:
            selected_questions.append(subset.sample(1).iloc[0])
        else:
            st.warning(f"No questions found for category '{cat}'.")

    if selected_questions:
        st.session_state["selected"] = pd.DataFrame(selected_questions)
else:
    if "selected" not in st.session_state:
        st.info("Click the button above to select one question from each category.")

# --- Display selected questions and Pass/Fail buttons ---
if "selected" in st.session_state:
    selected = st.session_state["selected"]
    st.subheader("Selected Questions")

    responses = []
    for _, row in selected.iterrows():
        st.markdown(f"**Category:** {row['category'].title()}")
        st.markdown(f"**Question:** {row['question_text']}")
        result = st.radio(
            "Result:",
            ["Pass", "Fail"],
            key=row["question_id"]
        )
        responses.append({
            "timestamp": datetime.datetime.now().isoformat(),
            "question_id": row["question_id"],
            "question_text": row["question_text"],
            "category": row["category"],
            "result": result
        })
        st.markdown("---")

# ---  ---
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# Connect to Google Sheets
scope = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"], scopes=scope
)
client = gspread.authorize(creds)

# Open your sheet
SHEET_NAME = "fraud_results"  # change to your Google Sheet name
sheet = client.open(SHEET_NAME).sheet1

# Function to save results
def save_result(question, result, category):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sheet.append_row([timestamp, question, result, category])

# --- Save all responses to Google Sheets ---
if "selected" in st.session_state:
    if st.button("Save All Results"):
        for response in responses:
            save_result(
                question=response["question_text"],
                result=response["result"],
                category=response["category"],
            )
        st.success("All results saved to Google Sheets!")

