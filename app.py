import cv2
import streamlit as st
import mediapipe as mp
import numpy as np

# ─────────────────────────────────────────────
# Streamlit Configuration
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="AI Gesture Controller",
    page_icon="🎨",
    layout="wide",
)

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands 
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(
    min_detection_confidence=0.8,
    min_tracking_confidence=0.7
)

# Initialize Session State
if 'char_x' not in st.session_state:
    st.session_state.char_x = 400
if 'char_y' not in st.session_state:
    st.session_state.char_y = 300
if 'run_camera' not in st.session_state:
    st.session_state.run_camera = False
if 'draw_points' not in st.session_state:
    st.session_state.draw_points = []  # Stores drawing coordinates

# ─────────────────────────────────────────────
# User Interface (Sidebar & Controls)
# ─────────────────────────────────────────────
st.title("🕹️ AI Gesture Studio")
st.markdown("Select a mode below and use your hand gestures in front of the camera.")

# Mode Selection
mode = st.radio(
    "Select Control Mode:",
    ["Character Control (Joystick)", "Air Canvas (Drawing)"],
    horizontal=True
)

col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    if st.button("🚀 Start Camera", use_container_width=True):
        st.session_state.run_camera = True
with col2:
    if st.button("🛑 Stop Camera", use_container_width=True):
        st.session_state.run_camera = False
with col3:
    if st.button("🧹 Clear Canvas", use_container_width=True):
        st.session_state.draw_points = []

# Short instructions based on mode
if mode == "Character Control (Joystick)":
    st.info("💡 **How to use:** Point your index finger and move it Up, Down, Left, or Right.")
else:
    st.info("💡 **How to use:** Bring your index & middle fingers together to **DRAW**. Separate them to **STOP**.")

video_placeholder = st.empty()

# ─────────────────────────────────────────────
# Main Loop
# ─────────────────────────────────────────────
if st.session_state.run_camera:
    cap = cv2.VideoCapture(0)
    
    while st.session_state.run_camera:
        ret, frame = cap.read()
        if not ret:
            st.error("Camera not detected.")
            break

        frame = cv2.flip(frame, 1)  # Mirroring
        h, w, _ = frame.shape
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(frame_rgb)
        
        # Prepare a Dark Canvas on the right side
        char_canvas = np.zeros((h, 800, 3), dtype=np.uint8)
        char_canvas[:] = (25, 25, 25)  # Dark background color
        
        current_gesture = "STATIONARY"

        if results.multi_hand_landmarks:
            # Get the first detected hand
            hand_landmarks = results.multi_hand_landmarks[0]
            landmarks = hand_landmarks.landmark
            
            # Reference points (Index Finger & Middle Finger)
            index_tip = landmarks[mp_hands.HandLandmark.INDEX_FINGER_TIP]
            index_mcp = landmarks[mp_hands.HandLandmark.INDEX_FINGER_MCP]
            middle_tip = landmarks[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]

            # ---------------------------------------------------------
            # MODE 1: CHARACTER CONTROL
            # ---------------------------------------------------------
            if mode == "Character Control (Joystick)":
                dx = index_tip.x - index_mcp.x
                dy = index_tip.y - index_mcp.y
                threshold = 0.07 

                if abs(dx) > abs(dy):
                    if dx > threshold:
                        current_gesture = "RIGHT"
                        st.session_state.char_x += 20
                    elif dx < -threshold:
                        current_gesture = "LEFT"
                        st.session_state.char_x -= 20
                else:
                    if dy > threshold:
                        current_gesture = "DOWN"
                        st.session_state.char_y += 20
                    elif dy < -threshold:
                        current_gesture = "UP"
                        st.session_state.char_y -= 20
                
                # Keep character within boundaries
                st.session_state.char_x = max(30, min(800 - 30, st.session_state.char_x))
                st.session_state.char_y = max(30, min(h - 30, st.session_state.char_y))
                
                # Draw Character
                cv2.circle(char_canvas, (st.session_state.char_x, st.session_state.char_y), 25, (0, 255, 127), -1)
                cv2.circle(char_canvas, (st.session_state.char_x, st.session_state.char_y), 28, (255, 255, 255), 2)

            # ---------------------------------------------------------
            # MODE 2: AIR CANVAS (DRAWING)
            # ---------------------------------------------------------
            else:
                # Convert normalized coordinates to pixel (for 800px wide canvas)
                cx, cy = int(index_tip.x * 800), int(index_tip.y * h)
                
                # Calculate distance between index and middle finger (Euclidean distance)
                dist = np.sqrt((index_tip.x - middle_tip.x)**2 + (index_tip.y - middle_tip.y)**2)
                
                if dist < 0.05: # Fingers closed (Drawing Mode)
                    current_gesture = "DRAWING"
                    st.session_state.draw_points.append((cx, cy))
                else: # Fingers apart (Hover/Moving Mode)
                    current_gesture = "HOVERING"
                    st.session_state.draw_points.append(None) # "None" starts a new line segment

                # Draw all stored lines
                for i in range(1, len(st.session_state.draw_points)):
                    if st.session_state.draw_points[i-1] is not None and st.session_state.draw_points[i] is not None:
                        cv2.line(char_canvas, st.session_state.draw_points[i-1], 
                                 st.session_state.draw_points[i], (0, 200, 255), 6)
                
                # Draw cursor (small circle) at finger tip
                cv2.circle(char_canvas, (cx, cy), 10, (255, 255, 255), -1)

            # Draw hand landmarks on the camera feed
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

        # Add Text Info on Canvas
        cv2.putText(char_canvas, f"MODE: {mode}", (20, 40), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 2)
        cv2.putText(char_canvas, f"ACTION: {current_gesture}", (20, 75), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 127), 2)

        # Combine camera video and canvas side-by-side
        combined_output = np.hstack([frame, char_canvas])
        
        # Display in Streamlit
        video_placeholder.image(combined_output, channels="BGR", use_container_width=True)

    cap.release()
else:
    st.info("System is in Standby mode. Click 'Start Camera' to begin.")
