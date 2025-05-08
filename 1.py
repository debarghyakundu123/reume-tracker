import streamlit as st
from datetime import datetime

# Initialize session state for storing the click logs and count
if 'click_logs' not in st.session_state:
    st.session_state['click_logs'] = []
if 'click_count' not in st.session_state:
    st.session_state['click_count'] = 0

# Title for the app
st.title("📄 Resume Open Tracker")

# Instructions
st.write("➡️ Track how many times your resume link is clicked.")

# Your original Google Drive resume link (can be any link)
RESUME_LINK = "https://drive.google.com/file/d/1cqj9BKunrcrytGSVYz8FRziXfIjSrOPx/view?usp=sharing"

# Create a custom tracking URL for the resume (without relying on Bitly or other services)
TRACKING_URL = f"{st.experimental_get_url()}?track=1"

# Display the tracking URL (shareable link)
st.subheader("🔗 Your Custom Tracking Link:")
st.code(TRACKING_URL)

# When the link is clicked (query parameters check)
query_params = st.experimental_get_query_params()

if "track" in query_params:
    # Log the timestamp when the resume link is clicked
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.session_state['click_logs'].append(f"Resume opened at: {now}")
    st.session_state['click_count'] += 1  # Increment click count
    st.success(f"✅ Resume clicked at {now}!")

# Display the number of clicks and the click logs
st.subheader("🔔 Click Statistics:")
st.write(f"Total Clicks: {st.session_state['click_count']}")

st.subheader("🔔 Click Logs:")
if st.session_state['click_logs']:
    for log in st.session_state['click_logs']:
        st.info(log)
else:
    st.write("No clicks yet. Waiting for someone to click the resume link...")

# Optionally, you can show a button to reset the logs (for testing purposes)
if st.button("Reset Logs"):
    st.session_state['click_logs'] = []
    st.session_state['click_count'] = 0
    st.write("Logs have been reset.")
