import streamlit as st
from datetime import datetime

# Initialize session state to store hits
if 'hits' not in st.session_state:
    st.session_state['hits'] = []

# Title of the Streamlit App
st.title("📄 PDF Open Tracker")

# Description of the functionality
st.write("➡️ This app tracks when your PDF is opened via a tracking URL. Every time the PDF link is opened, you will see a notification here.")

# Display current logs of the PDF opens
st.subheader("🔔 Notifications (PDF Open Logs):")
if st.session_state['hits']:
    for hit in reversed(st.session_state['hits']):
        st.info(f"PDF was opened at: {hit}")
else:
    st.write("No opens yet. Waiting for someone to open your PDF...")

# Set your app's public URL manually here 👇
PUBLIC_APP_URL = "https://your-app-name.streamlit.app"  # Replace with your live app URL

# Create a unified tracking URL that will send the 'ping' signal when the URL is accessed
st.subheader("🔗 Your Tracking URL (PDF Link to Embed):")
tracking_url = f"{PUBLIC_APP_URL}?track=open"
st.code(tracking_url)

# Use st.query_params to get the tracking query params
query_params = st.query_params

# When someone accesses the URL with the tracking link, a "ping" will be registered
if "track" in query_params and query_params["track"][0] == "open":
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Append the time of the PDF open event to the session state
    st.session_state['hits'].append(now)
    
    # Display a success message with the timestamp
    st.success(f"✅ Tracker ping received at {now}!")
