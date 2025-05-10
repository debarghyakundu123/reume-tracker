import streamlit as st
import uuid
import os
from datetime import datetime
import json # For storing tracking data

# --- Configuration ---
RESUMES_DIR = "resumes"
TRACKING_DATA_FILE = "tracking_data.json"

# --- Helper Functions ---

def load_tracking_data():
    """Loads tracking data from the JSON file."""
    if os.path.exists(TRACKING_DATA_FILE):
        try:
            with open(TRACKING_DATA_FILE, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {} # Return empty if file is corrupted
    return {}

def save_tracking_data(data):
    """Saves tracking data to the JSON file."""
    with open(TRACKING_DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def initialize_storage():
    """Initializes resumes directory and tracking file if they don't exist."""
    os.makedirs(RESUMES_DIR, exist_ok=True)
    if not os.path.exists(TRACKING_DATA_FILE):
        save_tracking_data({})

# Call initialization at the start
initialize_storage()

# --- Main Application Logic ---

if 'uploaded_file_details' not in st.session_state:
    st.session_state.uploaded_file_details = None

def generate_trackable_link_persistent(file_path, original_name):
    """Generates a unique trackable link ID and stores file info persistently."""
    link_id = str(uuid.uuid4())
    tracking_data = load_tracking_data()
    tracking_data[link_id] = {
        'file_path': file_path,
        'original_name': original_name,
        'view_count': 0,
        'created_timestamp': datetime.now().isoformat(),
        'last_viewed_timestamp': None,
        'view_timestamps': [] # List to store each view time
    }
    save_tracking_data(tracking_data)
    return link_id

def serve_resume_and_track(link_id):
    """Logs access persistently and serves the resume."""
    tracking_data = load_tracking_data()
    if link_id in tracking_data:
        resume_info = tracking_data[link_id]

        # --- Track the view BEFORE serving ---
        resume_info['view_count'] += 1
        current_time = datetime.now().isoformat()
        resume_info['last_viewed_timestamp'] = current_time
        resume_info['view_timestamps'].append(current_time)
        save_tracking_data(tracking_data) # Save updated data

        # --- Serve the file for download ---
        try:
            with open(resume_info['file_path'], "rb") as fp:
                st.download_button(
                    label=f"Download {resume_info['original_name']}",
                    data=fp,
                    file_name=resume_info['original_name'],
                    mime="application/pdf" # Or the appropriate MIME type
                )
            st.success(f"'{resume_info['original_name']}' download initiated. Access has been logged.")
            st.caption(f"This view was recorded at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            # We no longer stop here, allowing the dashboard to render.
            # The download button will trigger a separate browser action.
        except FileNotFoundError:
            st.error("Error: Resume file not found on server. It might have been moved or deleted.")
        except Exception as e:
            st.error(f"An error occurred while trying to serve the resume: {e}")
    else:
        st.error("Invalid or expired resume link.")

# --- Streamlit App UI ---
st.set_page_config(layout="wide")
st.title("📄 Resume Tracker Dashboard")

# --- Handle Resume Access via Query Parameter ---
query_params = st.query_params
resume_id_to_track = query_params.get("resume_id", [None])[0]

if resume_id_to_track:
    serve_resume_and_track(resume_id_to_track)
    # We do NOT stop here anymore. The download button handles the file.

# --- Main Dashboard Area ---
tab1, tab2, tab3 = st.tabs(["📤 Upload & Generate Link", "📊 Tracking Dashboard", "⚙️ Manage Data"])

with tab1:
    st.header("1. Upload Your Resume")
    uploaded_file = st.file_uploader("Choose your resume PDF", type=["pdf", "docx", "doc"])

    if uploaded_file is not None:
        save_path = os.path.join(RESUMES_DIR, uploaded_file.name)
        try:
            with open(save_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.session_state.uploaded_file_details = {
                'path': save_path,
                'name': uploaded_file.name
            }
            st.success(f"Resume '{uploaded_file.name}' uploaded successfully to '{save_path}'!")
        except Exception as e:
            st.error(f"Error saving file: {e}")

    if st.session_state.uploaded_file_details:
        st.markdown("---")
        st.header("2. Generate Trackable Link")
        if st.button("🔗 Generate Link for Last Uploaded Resume"):
            file_details = st.session_state.uploaded_file_details
            link_id = generate_trackable_link_persistent(file_details['path'], file_details['name'])

            # Construct the trackable URL
            # We'll assume the user knows the base URL of their running Streamlit app.
            # We just provide the query parameter.
            trackable_url_param = f"?resume_id={link_id}"

            st.subheader("Share this link (append to your app's URL):")
            st.code(trackable_url_param)
            st.info(f"When a user opens your Streamlit app's URL with '{trackable_url_param}' appended, the view count will be updated in the 'Tracking Dashboard'.")
            st.warning("You need to share your Streamlit app's base URL followed by the code above (e.g., `your_app_url{trackable_url_param}`).")
with tab2:
    st.header("📊 Resume View Tracking")

    if st.button("🔄 Refresh Dashboard"):
        st.rerun() # Reruns the script to fetch the latest data

    tracking_data = load_tracking_data()

    if tracking_data:
        st.markdown(f"Last dashboard update: `{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`")

        # Prepare data for display (e.g., in a more table-friendly format)
        display_data = []
        for link_id, data in tracking_data.items():
            display_data.append({
                "Resume Name": data['original_name'],
                "View Count": data['view_count'],
                "Last Viewed": datetime.fromisoformat(data['last_viewed_timestamp']).strftime('%Y-%m-%d %H:%M:%S') if data['last_viewed_timestamp'] else "Never",
                "Created": datetime.fromisoformat(data['created_timestamp']).strftime('%Y-%m-%d %H:%M:%S'),
                "Link ID": link_id,
                # "Trackable Link": f"{base_app_url}/?resume_id={link_id}" # Requires base_app_url to be defined here too
            })

        if display_data:
            st.dataframe(display_data, use_container_width=True)

            st.subheader("Detailed View Logs (Last 5 per resume)")
            for link_id, data in tracking_data.items():
                with st.expander(f"{data['original_name']} (ID: {link_id}) - {data['view_count']} views"):
                    if data['view_timestamps']:
                        st.write("Recent view times:")
                        for ts in reversed(data['view_timestamps'][-5:]): # Show last 5 views
                            st.caption(f"- {datetime.fromisoformat(ts).strftime('%Y-%m-%d %H:%M:%S')}")
                    else:
                        st.caption("No views recorded yet.")
        else:
            st.info("No resumes are currently being tracked. Upload a resume and generate a link first.")

    else:
        st.info("No tracking data found. Upload a resume and generate a trackable link to begin.")

with tab3:
    st.header("⚙️ Manage Tracking Data")
    st.warning("⚠️ Be careful with these actions. Data deletion is permanent.")

    tracking_data = load_tracking_data()
    if tracking_data:
        selected_id_to_delete = st.selectbox("Select Resume Link to Delete:", options=[""] + list(tracking_data.keys()), format_func=lambda x: tracking_data.get(x, {}).get('original_name', x) if x else "Select...")

        if selected_id_to_delete and st.button(f"🗑️ Delete Tracking for '{tracking_data[selected_id_to_delete]['original_name']}'", type="primary"):
            # Optionally, also delete the file from RESUMES_DIR
            # file_to_delete_path = tracking_data[selected_id_to_delete]['file_path']
            del tracking_data[selected_id_to_delete]
            save_tracking_data(tracking_data)
            # if os.path.exists(file_to_delete_path):
            #    os.remove(file_to_delete_path)
            #    st.success(f"Deleted resume file '{file_to_delete_path}' and its tracking data.")
            # else:
            st.success(f"Deleted tracking data for link ID '{selected_id_to_delete}'.")
            st.rerun()

        if st.button("⚠️ Delete ALL Tracking Data", type="primary"):
            if st.checkbox("I am sure I want to delete all tracking data."): # Confirmation
                save_tracking_data({}) # Clears the data
                # Optionally clear the resumes directory too, but be very careful
                # for filename in os.listdir(RESUMES_DIR):
                #    os.remove(os.path.join(RESUMES_DIR, filename))
                st.success("All tracking data has been deleted.")
                st.rerun()
    else:
        st.info("No tracking data to manage.")
