import streamlit as st
from datetime import datetime

# Initialize session state to store hits
if 'hits' not in st.session_state:
    st.session_state['hits'] = []

# Title
st.title("📄 Resume Open Tracker")

st.write("➡️ This app tracks when someone opens your resume PDF via the tracking URL.")

# Display current logs
st.subheader("🔔 Notifications (Resume Open Logs):")
if st.session_state['hits']:
    for hit in reversed(st.session_state['hits']):
        st.info(f"Resume was opened at: {hit}")
else:
    st.write("No opens yet. Waiting for someone to open your resume...")

# Set your app's public URL manually here 👇
PUBLIC_APP_URL = "https://reume-tracker-dk.streamlit.app/"  # Use your Streamlit app URL

# Generate and display the shareable link
st.subheader("🔗 Your Resume Tracking Link:")
tracking_link = f"{PUBLIC_APP_URL}?track=1"
st.code(tracking_link)

# Check if the user clicked the link
query_params = st.experimental_get_query_params()
if "track" in query_params:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.session_state['hits'].append(now)
    st.success(f"✅ Resume opened at {now}!")
    st.write("Hello, you've opened the resume!")
