Here is a professional `README.md` file for your project, structured to be clear and informative for anyone viewing your repository.

---

# 🕹️ AI Gesture Studio

A real-time **Human-Machine Interface (HMI)** project built with Python, MediaPipe, and Streamlit. This application translates hand gestures into digital inputs, featuring two distinct modes: **Interactive Character Control** and **Air Canvas**.

## 🚀 Features
* **Character Control (Joystick Mode):** Use your index finger as a virtual joystick to navigate an object on the screen.
* **Air Canvas (Drawing Mode):** Perform "Air Drawing" by pinching your index and middle fingers together to draw in real-time.
* **Web-Based Interface:** Fully integrated with **Streamlit** for a seamless, browser-based control experience.
* **Computer Vision Powered:** Utilizes **MediaPipe Hands** for robust, low-latency gesture detection.

## 🛠️ Technical Stack
* **Python:** Core logic and processing.
* **OpenCV:** Image acquisition and real-time computer vision processing.
* **MediaPipe:** Hand landmark detection and tracking.
* **Streamlit:** Frontend web framework for dashboard visualization.
* **NumPy:** Matrix operations for frame manipulation and drawing logic.

## 📋 Objectives
1.  **Develop Real-Time Hand Tracking:** Integrate MediaPipe to accurately capture and process hand gestures for digital interaction.
2.  **Build a Streamlit Interface:** Create a responsive web-based platform to manage both *Air Canvas* drawing and object control functions.
3.  **Implement Gesture Logic:** Develop algorithms that translate fluid hand movements into precise inputs for creative and navigational tasks.

## 📦 How to Run

### Prerequisites
Ensure you have Python installed, then install the required dependencies:
```bash
pip install opencv-python streamlit mediapipe numpy
```

### Execution
1.  Clone this repository.
2.  Run the application using Streamlit:
```bash
streamlit run app.py
```
3.  Open the local URL provided in your terminal (usually `http://localhost:8501`).

## 💡 Usage Instructions
* **Start/Stop Camera:** Use the dashboard buttons to initialize the video feed.
* **Joystick Mode:** Point your index finger to move the character. The system maps your finger's position relative to the base joint to determine direction.
* **Air Canvas Mode:** Pinch your index and middle fingers to trigger the "Draw" state. Separate them to pause drawing.
* **Clear Canvas:** Use the "Clear Canvas" button to reset your workspace.

## 🤝 Project Context
This project is part of a series focusing on Edge AI and Computer Vision development. It serves as an exploration of practical, gesture-based control systems for robotics and creative automation.

---

*Developed by [Winzie]*
