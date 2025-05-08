import streamlit as st
from datetime import datetime

# Initialize session state logs and view counter
if 'view_count' not in st.session_state:
    st.session_state.view_count = 0
if 'logs' not in st.session_state:
    st.session_state.logs = []

st.title("Resume Tracker 🚀")

# Upload resume
resume_file = st.file_uploader("Upload your resume (PDF):")

if resume_file:
    st.success("✅ Your resume is ready to share!")

    # Provide download button
    st.download_button(
        label="Download Resume",
        data=resume_file,
        file_name="My_Resume.pdf",
        mime="application/pdf"
    )

    # Generate unique tracking URL
    app_url = "https://your-app-name-your-username.streamlit.app"
    tracking_url = f"{app_url}?track=true"

    st.write("✅ Share this link with others to track views:")

    # Display the link that users can share
    st.code(tracking_url)

# Track access via query parameters
query_params = st.experimental_get_query_params()
if 'track' in query_params:
    # Increment view count when the resume page is accessed
    st.session_state.view_count += 1

    # Log the view with timestamp
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f'Resume viewed at {timestamp}'
    st.session_state.logs.append(log_entry)
    
    st.write("✅ Thanks for viewing the resume!")

# Show total views and logs
st.subheader("📜 View Logs")
if st.session_state.view_count > 0:
    st.write(f"Total views: {st.session_state.view_count}")
    for log in st.session_state.logs:
        st.write(log)
else:
    st.info("No views yet.")
