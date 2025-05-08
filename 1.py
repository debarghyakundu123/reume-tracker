import streamlit as st
from datetime import datetime

# Initialize session state log
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

    st.write("Share this link with others: ")
    st.code(st.request.url)  # Displays your Streamlit Cloud URL

# Track access
query_params = st.experimental_get_query_params()
if 'track' in query_params:
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f'Resume viewed at {timestamp}'
    st.session_state.logs.append(log_entry)
    st.write("✅ Thanks for viewing the resume!")

    if resume_file:
        st.download_button(
            label="Download Resume",
            data=resume_file,
            file_name="My_Resume.pdf",
            mime="application/pdf"
        )

# Show logs
st.subheader("📜 View Logs")
if st.session_state.logs:
    for log in st.session_state.logs:
        st.write(log)
else:
    st.info("No views yet.")
