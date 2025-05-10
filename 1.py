import streamlit as st
import pymupdf  # ✅ Correct PyMuPDF import
import csv
import time
import os
from urllib.parse import urlparse, parse_qs

st.set_page_config(page_title="Resume Tracker", layout="wide")
st.title("📄 Resume Tracking System")

# ---- Set Up Log File ----
log_file = "tracking_logs.csv"
if not os.path.exists(log_file):
    with open(log_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Timestamp", "Visitor Info"])

# ---- Check for Tracking Link Visit ----
query_params = st.experimental_get_query_params()
if 'track' in query_params:
    tracker_id = query_params['track'][0]
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    visitor_info = f"Tracker ID: {tracker_id}"
    with open(log_file, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([timestamp, visitor_info])
    st.success(f"✅ Thanks for checking this resume! (ID: {tracker_id})")

# ---- Upload Resume Section ----
st.header("Upload and Track Your Resume")
uploaded_file = st.file_uploader("Upload your resume (PDF only)", type=['pdf'])

if uploaded_file is not None:
    with open("original_resume.pdf", "wb") as f:
        f.write(uploaded_file.read())

    # Generate a unique tracker ID (can be enhanced to be dynamic)
    tracker_id = "unique123"
    streamlit_url = "YOUR_STREAMLIT_APP_URL"  # Replace with your actual Streamlit app URL
    tracking_text = f"This resume is tracked. Verify here: {streamlit_url}/?track={tracker_id}"  # Text to insert

    doc = pymupdf.open("original_resume.pdf")
    page = doc[0]

    # Insert the tracking text at the top of the first page
    page.insert_text((50, 50), tracking_text, fontsize=8, color=(0, 0, 1))

    tracked_filename = "tracked_resume.pdf"
    doc.save(tracked_filename)
    doc.close()

    st.success("✅ Tracking link embedded into your resume!")
    with open(tracked_filename, "rb") as f:
        st.download_button("Download Tracked Resume", f, file_name="tracked_resume.pdf")

# ---- Tracking Dashboard ----
st.header("📊 Tracking Dashboard")
if os.path.exists(log_file):
    with open(log_file, 'r') as f:
        reader = csv.reader(f)
        logs = list(reader)
    if len(logs) > 1:
        st.table(logs)
    else:
        st.info("No tracking events yet.")
else:
    st.info("Tracking system not initialized.")
