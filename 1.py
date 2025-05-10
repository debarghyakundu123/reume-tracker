import streamlit as st
import threading
import fitz  # PyMuPDF
from flask import Flask, send_file, request
import time
import csv
import os

# ---- Flask App for Tracking ----
app = Flask(__name__)
log_file = "tracking_logs.csv"

if not os.path.exists(log_file):
    with open(log_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Timestamp", "IP", "User-Agent"])

@app.route('/track/<tracker_id>.png')
def track(tracker_id):
    ip = request.remote_addr
    user_agent = request.headers.get('User-Agent')
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')

    # Log the tracking event
    with open(log_file, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([timestamp, ip, user_agent])

    # Send a 1x1 transparent pixel
    return send_file('pixel.png', mimetype='image/png')

# ---- Start Flask App in Thread ----
def run_flask():
    app.run(host='0.0.0.0', port=5000)

threading.Thread(target=run_flask, daemon=True).start()

# ---- Streamlit App ----
st.title("📄 Resume Tracking System")
st.write("Upload your resume to embed a tracking link and monitor views.")

uploaded_file = st.file_uploader("Upload your resume (PDF only)", type=['pdf'])

if uploaded_file is not None:
    # Save original file
    with open("original_resume.pdf", "wb") as f:
        f.write(uploaded_file.read())

    # Open PDF and insert tracking pixel
    doc = fitz.open("original_resume.pdf")
    page = doc[0]  # insert on the first page

    # Set tracking image URL (update with your real server URL)
    tracking_url = "http://localhost:5000/track/unique123.png"

    img_rect = fitz.Rect(50, 50, 52, 52)  # small space
    page.insert_image(img_rect, filename="pixel.png", overlay=True, keep_proportion=True)

    # Save modified PDF
    tracked_filename = "tracked_resume.pdf"
    doc.save(tracked_filename)
    doc.close()

    st.success("✅ Tracking pixel embedded!")
    with open(tracked_filename, "rb") as f:
        st.download_button("Download Tracked Resume", f, file_name="tracked_resume.pdf")

st.header("📊 Tracking Dashboard")

if os.path.exists(log_file):
    with open(log_file, 'r') as f:
        reader = csv.reader(f)
        logs = list(reader)
    if len(logs) > 1:
        st.table(logs)
    else:
        st.info("No tracking events yet.")
else:
    st.info("Tracking system not initialized.")

# ---- Add Pixel Image if Missing ----
if not os.path.exists('pixel.png'):
    from PIL import Image
    img = Image.new('RGBA', (1, 1), (0, 0, 0, 0))
    img.save('pixel.png')
