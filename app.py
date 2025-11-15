import streamlit as st
import pandas as pd
import random
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials

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

# --- Connect to Google Sheets ---
SHEET_NAME = "fraud_results"  # Change to your Google Sheet title
TAB_NAME = "Sheet1"           # Change if your tab name is different

scope = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"], scopes=scope
)
client = gspread.authorize(creds)
sheet = client.open(SHEET_NAME).worksheet(TAB_NAME)

# --- Test Google Sheets connection ---
if st.button("Test Google Sheet Connection"):
    try:
        sheet.append_row(["TEST", "TEST", "TEST", "TEST"])
        st.success("Google Sheets connection successful!")
    except Exception as e:
        st.error(f"Google Sheets write failed: {e}")

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
        st.info("Click 'Select Questions' to pick one question from each category.")

# --- Display selected questions and Pass/Fail radios ---
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
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "question_id": row["question_id"],
            "question_text": row["question_text"],
            "category": row["category"],
            "result": result
        })
        st.markdown("---")

# --- Function to save results to Google Sheets ---
def save_result(question, result, category, timestamp):
    sheet.append_row([timestamp, question, result, category])

# --- Save all responses button ---
if "selected" in st.session_state and responses:
    if st.button("Save All Results"):
        for response in responses:
            save_result(
                question=response["question_text"],
                result=response["result"],
                category=response["category"],
                timestamp=response["timestamp"]
            )
        st.success("All results saved to Google Sheets!")
