import streamlit as st
import hashlib
import time
import pandas as pd
from datetime import datetime
import os
from urllib.parse import quote
import base64  # Import base64

# Configuration
UPLOAD_FOLDER = 'uploads'  # Directory to store uploaded resumes
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Data Structures (using dictionaries for simplicity, can be replaced with a database)
user_resumes = {}  # {user_id: {resume_id: {filename: ..., tracking_id: ..., views: 0, view_log: []}}}
user_profiles = {} # {user_id: {profile_views: 0, unique_profile_viewers: set()}}


# Helper Functions
def generate_tracking_id(user_id, filename):
    """Generates a unique tracking ID for a resume.  Includes user ID."""
    timestamp = str(time.time())
    data = f"{user_id}-{filename}-{timestamp}".encode('utf-8') # Include user_id
    return hashlib.sha256(data).hexdigest()[:16] # Shorten for URL

def get_file_extension(filename):
    """Gets the file extension of a filename."""
    return os.path.splitext(filename)[1]

def is_valid_file_type(file):
    """Checks if the uploaded file is a valid type (PDF, DOC, DOCX)."""
    allowed_extensions = ['.pdf', '.doc', '.docx']
    return get_file_extension(file.name).lower() in allowed_extensions

def store_resume(user_id, file):
    """Stores the uploaded resume file and its metadata.

    Handles file storage and updates the user_resumes dictionary.  Checks for
    duplicate filenames and appends a unique identifier if necessary.
    """
    if user_id not in user_resumes:
        user_resumes[user_id] = {}

    # Check for duplicate filenames
    filename = file.name
    base_filename, ext = os.path.splitext(filename)
    counter = 1
    while any(resume_info['filename'] == filename for resume_info in user_resumes[user_id].values()):
        filename = f"{base_filename}_{counter}{ext}"
        counter += 1

    # Generate tracking ID
    tracking_id = generate_tracking_id(user_id, filename)

    # Save the file
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    with open(filepath, "wb") as f:
        f.write(file.read())

    # Store resume metadata
    resume_id = len(user_resumes[user_id]) + 1  # Simple ID, could use a UUID
    user_resumes[user_id][resume_id] = {
        'filename': filename,
        'tracking_id': tracking_id,
        'views': 0,
        'view_log': [],
        'filepath': filepath, # store the file path
    }
    return tracking_id, filename # Return filename

def get_user_id():
    """
    Gets the user ID from the session state, or defaults to a hardcoded value for
    demonstration purposes.  In a real application, this would come from
    your authentication system.
    """
    # In a real application, you would get the user ID from the authentication system.
    # For this example, we'll use a hardcoded user ID.
    # if 'user_id' in st.session_state:
    #     return st.session_state['user_id']
    # else:
    #     return 'test_user'  # Hardcoded user ID for demonstration
    if 'user_id' not in st.session_state:
        st.session_state['user_id'] = 'test_user'  # Default user
    return st.session_state['user_id']

def record_view(tracking_id, viewer_ip, referrer):
    """Records a view of a resume.  Now updates the user_resumes dict."""
    user_id = get_user_id() # added user_id
    if user_id in user_resumes: #check user exists
        for resume_id, resume_info in user_resumes[user_id].items():
            if resume_info['tracking_id'] == tracking_id:
                resume_info['views'] += 1
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                resume_info['view_log'].append({'timestamp': timestamp, 'viewer_ip': viewer_ip, 'referrer': referrer})
                return True  # Indicate success
    return False #Indicate failure

def get_resume_info(tracking_id):
    """Retrieves resume information based on the tracking ID. Now searches within user_resumes."""
    user_id = get_user_id()
    if user_id in user_resumes:
        for resume_id, resume_info in user_resumes[user_id].items():
            if resume_info['tracking_id'] == tracking_id:
                return resume_info
    return None

def display_resume(tracking_id):
    """Displays the resume file.  This is a simplified version."""
    resume_info = get_resume_info(tracking_id)
    if resume_info:
        filepath = resume_info['filepath']
        #st.write(f"Displaying resume: {resume_info['filename']}")
        # Instead of displaying,  open the file
        with open(filepath, "rb") as f:
            file_data = f.read()
        file_extension = get_file_extension(resume_info['filename']).lower()

        if file_extension == ".pdf":
            st.header(f"Displaying Resume: {resume_info['filename']}")
            # Use base64 encoding to display PDF directly in the browser
            base64_pdf = base64.b64encode(file_data).decode('utf-8')
            pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="800" height="800" type="application/pdf"></iframe>'
            st.markdown(pdf_display, unsafe_allow_html=True)

        elif file_extension in [".doc", ".docx"]:
            st.warning(
                "Displaying DOC/DOCX files directly in the browser is not reliably supported.  "
                "Please download the file to view it."
            )
            st.download_button(
                label=f"Download {resume_info['filename']}",
                data=file_data,
                file_name=resume_info['filename'],
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                if file_extension == ".docx"
                else "application/msword",
            )
        else:
            st.error("Unsupported file type.  Please upload a PDF, DOC, or DOCX file.")
    else:
        st.error("Resume not found.")



def track_profile_view():
    """Tracks a view of the user's profile."""
    user_id = get_user_id()
    # viewer_ip = st.request.remote_ip # Removed st.request
    # Get IP from session state if available (set in main), otherwise, use a placeholder
    viewer_ip = st.session_state.get('viewer_ip', 'Unknown')
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if user_id not in user_profiles:
        user_profiles[user_id] = {'profile_views': 0, 'unique_profile_viewers': set()}

    user_profiles[user_id]['profile_views'] += 1
    user_profiles[user_id]['unique_profile_viewers'].add(viewer_ip)
    st.session_state['last_profile_view'] = timestamp  # Store timestamp

def display_tracking_info(tracking_id):
    """Displays the tracking information for a given resume."""
    resume_info = get_resume_info(tracking_id)
    if resume_info:
        st.header(f"Tracking Information for {resume_info['filename']}")
        st.write(f"Tracking ID: {tracking_id}")
        st.write(f"Total Views: {resume_info['views']}")

        # Display view log
        st.subheader("View Log")
        if resume_info['view_log']:
            df = pd.DataFrame(resume_info['view_log'])
            st.dataframe(df)
        else:
            st.write("No views recorded yet.")
    else:
        st.error("Invalid Tracking ID")

def display_all_resumes():
    """Displays all resumes uploaded by the user."""
    user_id = get_user_id()
    if user_id in user_resumes:
        st.header("Your Uploaded Resumes")
        if user_resumes[user_id]: # Check if there are any resumes
             for resume_id, resume_info in user_resumes[user_id].items():
                st.subheader(resume_info['filename'])
                st.write(f"Tracking ID: {resume_info['tracking_id']}")
                st.write(f"Views: {resume_info['views']}")
                # Create a download button
                with open(resume_info['filepath'], "rb") as f:
                    file_data = f.read()
                st.download_button(
                    label=f"Download {resume_info['filename']}",
                    data=file_data,
                    file_name=resume_info['filename'],
                    mime="application/octet-stream",  # Generic MIME type
                )

                # Add a button to view tracking info for each resume
                if st.button(f"View Tracking Info for {resume_info['filename']}", key=f"track-{resume_info['tracking_id']}"):
                    display_tracking_info(resume_info['tracking_id'])
        else:
            st.write("You have not uploaded any resumes yet.")
    else:
        st.write("You have not uploaded any resumes yet.") #moved here

def display_profile_views():
    """Displays the view count for the user's profile."""
    user_id = get_user_id()
    if user_id in user_profiles:
        st.header("Your Profile Views")
        st.write(f"Total Profile Views: {user_profiles[user_id]['profile_views']}")
        st.write(f"Unique Profile Viewers: {len(user_profiles[user_id]['unique_profile_viewers'])}")
        if 'last_profile_view' in st.session_state:
            st.write(f"Last Profile View: {st.session_state['last_profile_view']}")
        else:
            st.write("No profile views recorded yet.")
    else:
        st.write("No profile views recorded yet.")

def get_viewer_ip():
    """
    Gets the viewer's IP address.  This function attempts to get the IP address
    from the X-Forwarded-For header if available (which is common when the
    Streamlit app is behind a proxy), and falls back to 'Unknown' if not.
    """
    # Try to get the IP address from the X-Forwarded-For header
    forwarded_for = st.session_state.get('X-Forwarded-For')
    if forwarded_for:
        # If there are multiple IPs in the header, take the first one (leftmost)
        viewer_ip = forwarded_for.split(',')[0].strip()
    else:
        viewer_ip = "Unknown"
    return viewer_ip
def main():
    """Main function for the Streamlit app."""
    st.title("Intelligent Resume Tracking System")

    # Get User ID
    user_id = get_user_id()

    # Get Viewer IP and store it in session state
    # This is the workaround for not having st.request
    viewer_ip =  get_viewer_ip() #st.session_state.get('viewer_ip') #changed to use get_viewer_ip()
    st.session_state['viewer_ip'] = viewer_ip

    # Sidebar for Navigation
    menu = ["Upload Resume", "View Resumes", "View Profile", "Track Resume"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Upload Resume":
        st.header("Upload Your Resume")
        uploaded_file = st.file_uploader("Choose a file", type=['pdf', 'doc', 'docx'])
        if uploaded_file is not None:
            if is_valid_file_type(uploaded_file):
                tracking_id, filename = store_resume(user_id, uploaded_file)
                st.success(f"Resume uploaded successfully!  Use this tracking ID: {tracking_id} to track views. Filename: {filename}")
                # Display the tracking link (made it clickable)
                tracking_link = f"/?tracking_id={tracking_id}"  # Simplified URL
                st.markdown(f"Share this link to track views: [{tracking_link}]({tracking_link})")
            else:
                st.error("Invalid file type. Please upload a PDF, DOC, or DOCX file.")

    elif choice == "View Resumes":
        display_all_resumes()

    elif choice == "View Profile":
        track_profile_view()
        display_profile_views()

    elif choice == "Track Resume":
        st.header("Track Resume Views")
        tracking_id = st.text_input("Enter the tracking ID of the resume you want to track:")
        if tracking_id:
            display_tracking_info(tracking_id)

    # Handle tracking via URL parameter (for shared links)
    query_params = st.query_params # changed to st.query_params()
    if "tracking_id" in query_params:
        tracking_id = query_params["tracking_id"][0]
        # st.write(f"Tracking ID from URL: {tracking_id}") #debug
        #st.stop() #debug
        viewer_ip = st.session_state.get('viewer_ip', 'Unknown') # Get from session, default to "Unknown"
        referrer = st.session_state.get('HTTP_REFERER', 'Direct') #  get the referrer
        record_view(tracking_id, viewer_ip, referrer) #record view
        display_resume(tracking_id) #show resume


if __name__ == "__main__":
    main()
