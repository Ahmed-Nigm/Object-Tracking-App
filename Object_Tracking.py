import streamlit as st
import cv2
import numpy as np
import tempfile
import time
import os

st.set_page_config(page_title="Object Detection App", layout="wide")

# Utility: Convert OpenCV BGR image to RGB
def convert_color(img):
    return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

# Sidebar
st.sidebar.header("⚙️ Settings")
uploaded_file = st.sidebar.file_uploader("Upload a video", type=["mp4", "avi", "mov", "wmv", "flv", "mkv", "webm", "mpeg"])
min_area = st.sidebar.slider("Minimum Object Area (px)", 100, 5000, 500, 100)
bg_method = st.sidebar.selectbox("Background Subtraction Method", ["MOG2", "KNN"])
show_mask = st.sidebar.checkbox("Show Foreground Mask")

# Main title
st.title("🎥 Object Detection App")
st.markdown("""This app uses **OpenCV** for real-time video object detection.
            Developed by: 'Ahmed Nigm'""")

if uploaded_file is not None:
    # Save uploaded file temporarily
    tfile = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    tfile.write(uploaded_file.read())
    
    cap = cv2.VideoCapture(tfile.name)
    
    if not cap.isOpened():
        st.error("⚠️ Could not open video file.")
    else:
        # Video details
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        st.sidebar.markdown(f"**Video Info:**\n- Resolution: {width}x{height}\n- FPS: {fps}\n- Frames: {total_frames}")
        
        # Choose background subtractor
        if bg_method == "MOG2":
            back_sub = cv2.createBackgroundSubtractorMOG2()
        else:
            back_sub = cv2.createBackgroundSubtractorKNN()
        
        # Placeholders
        video_placeholder = st.empty()
        progress = st.progress(0)
        status = st.empty()
        
        frame_count = 0
        detected_objects = 0
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            fg_mask = back_sub.apply(frame)
            contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for cnt in contours:
                if cv2.contourArea(cnt) > min_area:
                    x, y, w, h = cv2.boundingRect(cnt)
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                    detected_objects += 1
            
            frame_rgb = convert_color(frame)
            if show_mask:
                mask_rgb = cv2.cvtColor(fg_mask, cv2.COLOR_GRAY2RGB)
                combined = np.hstack((frame_rgb, mask_rgb))
                video_placeholder.image(combined, channels="RGB")
            else:
                video_placeholder.image(frame_rgb, channels="RGB")
            
            frame_count += 1
            progress.progress(frame_count / total_frames)
            status.text(f"Processing frame {frame_count}/{total_frames}...")
            
            time.sleep(0.01)  # smoother playback
        
        cap.release()
        cv2.destroyAllWindows()
        
        st.success("✅ Video processing complete!")
        st.write(f"**Total Objects Detected:** {detected_objects}")
        
        # Option to download processed video (extra: can add writer)
        if os.path.exists(tfile.name):
            with open(tfile.name, "rb") as f:
                st.download_button("⬇️ Download Original Video", f, file_name="uploaded_video.mp4")
