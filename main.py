# used for the camera
import cv2
import mediapipe as mp
import time
from playsound import playsound
import pygame

# Variables for timing
both_eyes_closed_start_time = None
alert_threshold = 1  # Time in seconds to detect if they fell asleep.

pygame.mixer.init()

def play_alarm():
    pygame.mixer.music.load("C:/Users/j_jaj/OneDrive/Desktop/iLert/alarm.mp3")
    pygame.mixer.music.play()
    
# Initialize Camera and Mediapipe
cam = cv2.VideoCapture(0)
face_mesh = mp.solutions.face_mesh.FaceMesh(refine_landmarks=True)

while True:
    _, frame = cam.read()
    frame = cv2.flip(frame, 1)  # Flip frame vertically because the camera is flipped
    frame_h, frame_w, _ = frame.shape
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    output = face_mesh.process(rgb_frame)

    landmark_points = output.multi_face_landmarks
    both_eyes_closed = False  # Reset eye state

    if landmark_points:
        landmarks = landmark_points[0].landmark

        # Left eye landmarks
        left_eye = [landmarks[145], landmarks[159]]
        left_eye_ratio = left_eye[0].y - left_eye[1].y

        # Right eye landmarks
        right_eye = [landmarks[374], landmarks[386]]
        right_eye_ratio = right_eye[0].y - right_eye[1].y

        # Draw landmarks for both eyes
        for landmark in left_eye + right_eye:
            x = int(landmark.x * frame_w)
            y = int(landmark.y * frame_h)
            cv2.circle(frame, (x, y), 3, (0, 255, 255))  # Yellow for eyes

        # Check if both eyes are closed
        left_eye_closed = left_eye_ratio < 0.015  # keep it 0.0015. Most accurate landmarks for left eye are not perfect.
        right_eye_closed = right_eye_ratio < 0.004  

        if left_eye_closed and right_eye_closed:
            both_eyes_closed = True

        # Timing logic for detecting if user fell asleep
        if both_eyes_closed:
            if both_eyes_closed_start_time is None:
                both_eyes_closed_start_time = time.time()  # Start timer
            elif time.time() - both_eyes_closed_start_time >= alert_threshold:
                print("ALERT: USER FELL ASLEEP!")
                cv2.putText(frame, "WAKE UP!", (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                play_alarm()
                both_eyes_closed_start_time = None  # Reset to avoid spamming alerts
        else:
            both_eyes_closed_start_time = None  # Reset if eyes are open

    # Display writing
    
    cv2.imshow('Sight Line', frame)

    # Exit loop on pressing 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    time.sleep(0.05)  # found the camera being very choppy so I added this to deal with the fps.
cam.release()
cv2.destroyAllWindows()

