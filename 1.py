import streamlit as st
from datetime import datetime

# Initialize session state to store hits
if 'hits' not in st.session_state:
    st.session_state['hits'] = []

# Title
st.title("📄 PDF Open Tracker")

st.write("➡️ This app tracks when your PDF is opened via a tracking URL.")

# Display current logs
st.subheader("🔔 Notifications (PDF Open Logs):")
if st.session_state['hits']:
    for hit in reversed(st.session_state['hits']):
        st.info(f"PDF was opened at: {hit}")
else:
    st.write("No opens yet. Waiting for someone to open your PDF...")

# Set your app's public URL manually here 👇
PUBLIC_APP_URL = "https://your-app-name.streamlit.app"  # Replace with your live app URL

# Display the tracker link
st.subheader("🔗 Your Tracking URL:")
tracker_url = f"{PUBLIC_APP_URL}?ping=1"
st.code(tracker_url)

# ✅ Updated: Use st.query_params (no more experimental)
query_params = st.query_params
if "ping" in query_params:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.session_state['hits'].append(now)
    st.success(f"✅ Tracker ping received at {now}!")
