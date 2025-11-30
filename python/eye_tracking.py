import cv2
import dlib
import numpy as np
import serial
import time
import pyttsx3
import threading

# Initialize serial communication with Arduino
ser = serial.Serial('COM4', 9600, timeout=1)
time.sleep(2)  # Allow connection to establish

# Initialize pyttsx3 for voice announcements
engine = pyttsx3.init()
announce_lock = threading.Lock()  # Lock to prevent overlapping speech

# Load dlib face detector and shape predictor
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(r"D:\python\shape_predictor_68_face_landmarks.dat")

# Start video capture
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FPS, 30)  # Try to maintain a higher FPS

# Variables
last_command = ""
eye_threshold = 0.25  # Adjust threshold for better accuracy
moving = False
eye_closed_start_time = None
last_obstacle_state = None  # Track last obstacle warning state

# Function to compute Eye Aspect Ratio (EAR) for detecting closed eyes
def eye_aspect_ratio(eye):
    A = np.linalg.norm(eye[1] - eye[5])
    B = np.linalg.norm(eye[2] - eye[4])
    C = np.linalg.norm(eye[0] - eye[3])
    return (A + B) / (2.0 * C)

# Function for voice alerts (Non-repetitive)
def announce(text):
    with announce_lock:
        engine.say(text)
        engine.runAndWait()

# Function to get distance from Arduino
def detect_obstacle():
    ser.write(b'G')  # Request distance
    time.sleep(0.05)  # Small delay for response
    
    if ser.in_waiting > 0:
        try:
            distance = float(ser.readline().decode().strip())
            return distance
        except ValueError:
            return 1000  # If reading fails, assume no obstacle
    return 1000

# Function to determine pupil position
def detect_pupil_position(frame, eye_points, gray):
    h, w = gray.shape
    
    # Get eye region coordinates
    x_coords = [point[0] for point in eye_points]
    y_coords = [point[1] for point in eye_points]
    x1, x2 = min(x_coords), max(x_coords)  # Min X coordinate
    y1, y2 = min(y_coords), max(y_coords)  # Max Y coordinate
    
    eye_frame = gray[y1:y2, x1:x2]
    if eye_frame.size == 0:
        return "CENTER"  # Avoid error if empty region
    
    # Resize eye frame for better processing
    eye_frame = cv2.resize(eye_frame, (200, 100), interpolation=cv2.INTER_CUBIC)
    
    # Use adaptive thresholding for better results
    thresh = cv2.adaptiveThreshold(eye_frame, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                    cv2.THRESH_BINARY_INV, 11, 2)
    
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if contours:
        max_contour = max(contours, key=cv2.contourArea)
        M = cv2.moments(max_contour)
        if M["m00"] != 0:
            cx = int(M["m10"] / M["m00"])
            
            # Draw pupil position for debugging
            cv2.circle(eye_frame, (cx, 50), 5, (0, 0, 255), -1)
            
            if cx < (width * 0.3):
                return "LEFT"
            elif cx > (width * 0.7):
                return "RIGHT"
    
    return "CENTER"

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to capture frame")
        break
    
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY).astype(np.uint8)
    
    faces = detector(gray)
    
    for face in faces:
        landmarks = predictor(gray, face)
        
        # Extract eye landmarks
        left_eye = np.array([(landmarks.part(i).x, landmarks.part(i).y) for i in range(36, 42)])
        right_eye = np.array([(landmarks.part(i).x, landmarks.part(i).y) for i in range(42, 48)])
        
        # Calculate EAR for both eyes
        left_ear = eye_aspect_ratio(left_eye)
        right_ear = eye_aspect_ratio(right_eye)
        
        ear = (left_ear + right_ear) / 2.0
        
        # Detect gaze direction (LEFT, CENTER, RIGHT)
        gaze_direction = detect_pupil_position(frame, left_eye, gray)
        
        # Control logic with start/stop timer
        if ear < eye_threshold:
            if eye_closed_start_time is None:
                eye_closed_start_time = time.time()  # Start the timer
            
            elapsed_time = time.time() - eye_closed_start_time
            if elapsed_time >= 1.5:  # Start the wheelchair
                if not moving:
                    ser.write(b'F')
                    last_command = 'F'
                    moving = True
                    announce("Starting the wheelchair")
                    eye_closed_start_time = None  # Reset timer
                else:
                    ser.write(b'S')  # Stop wheelchair
                    last_command = 'S'
                    moving = False
                    announce("Stopping the wheelchair")
        else:
            ser.write(b'F')
            last_command = 'F'
            moving = True
            announce("Starting the wheelchair")
            eye_closed_start_time = None  # Reset timer if eyes open before 1.5 sec
        
        # Send movement commands based on gaze direction if moving
        if moving:
            if gaze_direction == "LEFT" and last_command != 'L':
                ser.write(b'L')
                last_command = 'L'
                announce("Turning Left")
            elif gaze_direction == "RIGHT" and last_command != 'R':
                ser.write(b'R')
                last_command = 'R'
                announce("Turning Right")
            elif gaze_direction == "CENTER" and last_command != 'F':
                ser.write(b'F')
                last_command = 'F'
                announce("Moving Forward")
        
        # --- Debugging Visuals ---
        for point in left_eye:
            cv2.circle(frame, tuple(point), 1, (0, 255, 0), -1)
        for point in right_eye:
            cv2.circle(frame, tuple(point), 1, (0, 255, 0), -1)
        
        # Display Gaze Direction
        cv2.putText(frame, f"Gaze: {gaze_direction}", (50, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        
        # Display Eye Status
        eye_status = "Eyes Open" if ear > eye_threshold else "Eyes Closed"
        cv2.putText(frame, eye_status, (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                    (0, 0, 255) if ear < eye_threshold else (0, 255, 0), 2)
    
    # Check for obstacles
    distance = detect_obstacle()
    
    if distance < 20 and last_obstacle_state != "STOP":
        announce("Stopping the wheelchair.")
        ser.write(b'S')
        moving = False
        last_obstacle_state = "STOP"
    elif 20 <= distance <= 50 and last_obstacle_state != "WARNING":
        announce("Obstacle ahead.")
        last_obstacle_state = "WARNING"
    elif distance > 50 and last_obstacle_state != "CLEAR":
        last_obstacle_state = "CLEAR"
    
    cv2.imshow("Eye-Controlled Wheelchair", frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
ser.close()
