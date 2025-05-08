import streamlit as st
from datetime import datetime

# Initialize session state to store hits
if 'hits' not in st.session_state:
    st.session_state['hits'] = []

# Title
st.title("📄 Link Click Tracker")

st.write("➡️ This app tracks when someone clicks on the tracking link.")

# Display current logs
st.subheader("🔔 Notifications (Click Logs):")
if st.session_state['hits']:
    for hit in reversed(st.session_state['hits']):
        st.info(f"Link was clicked at: {hit}")
else:
    st.write("No clicks yet. Waiting for someone to click the link...")

# Set your app's public URL manually here 👇
# Replace this with your actual Streamlit app URL when deployed
PUBLIC_APP_URL = "https://your-app-name.streamlit.app"  # Use your Streamlit app URL

# Generate and display the shareable link
st.subheader("🔗 Your Tracking Link:")
tracking_link = f"{PUBLIC_APP_URL}?track=1"
st.code(tracking_link)

# Check if the user clicked the link
query_params = st.experimental_get_query_params()
if "track" in query_params:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.session_state['hits'].append(now)
    st.success(f"✅ Link clicked at {now}!")
    st.write("Hello!")
