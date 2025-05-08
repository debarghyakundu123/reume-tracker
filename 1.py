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

# Check if the user accessed the tracking link automatically
query_params = st.experimental_get_query_params()
if "track" in query_params:
    # Get current datetime from PC's system time
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Log the time in session state
    st.session_state['hits'].append(now)
    
    # Display a success message
    st.success(f"✅ Resume opened at {now}!")
    st.write("Hello! You've opened the resume!")

# Time-based tracking and notifications: View total resume opens
st.subheader("📈 Resume Open Analytics:")
current_date = datetime.now().strftime("%Y-%m-%d")
today_opens = [hit for hit in st.session_state['hits'] if hit.startswith(current_date)]

# Show number of opens today
st.write(f"📅 Today's Date: {current_date}")
st.write(f"📊 Resume opened {len(today_opens)} times today.")

# Show the list of all opens with timestamps
st.subheader("📅 Full Resume Open Log (All Time):")
if st.session_state['hits']:
    for hit in st.session_state['hits']:
        st.write(f"Opened at: {hit}")
else:
    st.write("No opens yet.")
