import streamlit as st
from datetime import datetime

# Initialize session state for click tracking
if 'click_count' not in st.session_state:
    st.session_state.click_count = 0
if 'logs' not in st.session_state:
    st.session_state.logs = []

st.title("📈 Resume Click Tracker")

st.write("Click the button below to open my resume. Each click will be logged with date and time!")

# Google Drive resume link
resume_link = "https://drive.google.com/file/d/1cqj9BKunrcrytGSVYz8FRziXfIjSrOPx/view"

# When the user clicks the button
if st.button("📄 Open My Resume"):
    # Increment click count
    st.session_state.click_count += 1
    
    # Log the current datetime
    click_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.session_state.logs.append(f"Resume opened at: {click_time}")

    # Open the resume in a new tab
    js = f"window.open('{resume_link}', '_blank')"
    st.components.v1.html(f"<script>{js}</script>")

# Show total clicks
st.subheader(f"🔢 Total Clicks: {st.session_state.click_count}")

# Show detailed logs
st.subheader("🕒 Click Logs:")
if st.session_state.logs:
    for log in reversed(st.session_state.logs):
        st.write(log)
else:
    st.write("No clicks yet.")
