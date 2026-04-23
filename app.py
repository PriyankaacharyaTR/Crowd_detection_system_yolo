import streamlit as st
import cv2
import tempfile
import os
from backend import CrowdAnalyzer

st.set_page_config(page_title="Local Edge AI Monitor", layout="wide")
st.title("🚨 Crowd & Incident Detector (Local GPU)")

uploaded_video = st.file_uploader("Upload Surveillance Video", type=["mp4", "mov", "avi"])

if uploaded_video is not None:
    # Save the file locally temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tfile:
        tfile.write(uploaded_video.read())
        video_path = tfile.name

    analyzer = CrowdAnalyzer()
    
    if st.button("▶️ Start Analysis"):
        cap = cv2.VideoCapture(video_path)
        st_frame = st.empty()
        st_metric = st.empty()
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret: break
            
            # Process frame
            img, count = analyzer.process_frame(frame)
            urgent, growth = analyzer.check_urgency(count)
            
            # Update UI
            st_frame.image(img, channels="BGR", use_container_width=True)
            
            if urgent:
                st_metric.error(f"URGENCY: {count} people (Sudden +{growth})")
            else:
                st_metric.info(f"Status: Normal | People: {count}")
                
        cap.release()
        os.remove(video_path) # Clean up temp file