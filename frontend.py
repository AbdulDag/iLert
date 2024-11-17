import threading
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.camera import Camera
import cv2
import mediapipe as mp
import time
import pygame

# Initialize pygame mixer
pygame.mixer.init()

# Define the alarm function
def play_alarm():
    """Play the alarm sound."""
    pygame.mixer.music.load("C:/Users/j_jaj/OneDrive/Desktop/iLert/alarm.mp3")
    pygame.mixer.music.play()


class CameraWidget(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'

        # my widget for cam. it's kivy cam so will not have landmarks.
        self.camera_widget = Camera(resolution=(640, 480), play=False)
        self.add_widget(self.camera_widget)

        # button fro da cam
        self.button = Button(text="Click to Activate")
        self.button.bind(on_press=self.toggle_camera)
        self.add_widget(self.button)

        # Initialize Mediapipe and OpenCV variables
        self.face_mesh = mp.solutions.face_mesh.FaceMesh(refine_landmarks=True)
        self.running = False
        self.alert_triggered = False
        self.both_eyes_closed_start_time = None
        self.alert_threshold = 1  # Time in seconds to detect if eyes are closed.
        self.opencv_capture = None

    def toggle_camera(self, instance):
        """Toggle the camera functionality."""
        if self.running:
            self.stop_camera()
        else:
            self.start_camera()

    def start_camera(self):
        """Start the camera and detection functionality."""
        self.running = True
        self.camera_widget.play = True
        self.button.text = "Camera In Use"
        self.alert_triggered = False

        # Start OpenCV capture and detection seperately
        self.opencv_capture = cv2.VideoCapture(0)
        threading.Thread(target=self.run_detection, daemon=True).start()

    def run_detection(self):
        
        while self.running:
            ret, frame = self.opencv_capture.read()
            if not ret:
                continue

            try:
                # Flip the frame to give mirror effect
                frame = cv2.flip(frame, 1)

                # Process the frame with Mediapipe
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                output = self.face_mesh.process(rgb_frame)

                if output.multi_face_landmarks:
                    for face_landmarks in output.multi_face_landmarks:
                        landmarks = face_landmarks.landmark

                        # Left eye landmarks
                        left_eye = [landmarks[145], landmarks[159]]
                        left_eye_ratio = left_eye[0].y - left_eye[1].y

                        # Right eye landmarks
                        right_eye = [landmarks[374], landmarks[386]]
                        right_eye_ratio = right_eye[0].y - right_eye[1].y

                        # Eye closure detection
                        left_eye_closed = left_eye_ratio < 0.015
                        right_eye_closed = right_eye_ratio < 0.004

                        if left_eye_closed and right_eye_closed:
                            if self.both_eyes_closed_start_time is None:
                                self.both_eyes_closed_start_time = time.time()
                            elif time.time() - self.both_eyes_closed_start_time >= self.alert_threshold:
                                if not self.alert_triggered:  # Trigger alert if not already triggered
                                    self.button.text = "ALERT: USER FELL ASLEEP!"
                                    play_alarm()
                                    self.alert_triggered = True
                        else:
                            self.both_eyes_closed_start_time = None  # Reset if eyes are open
                            if self.alert_triggered:  # Reset after an alert
                                self.alert_triggered = False
                            self.button.text = "Camera In Use"

                time.sleep(0.03)  # Maintain ~30 FPS 
            except Exception as e:
                print(f"Detection error: {e}")

    def stop_camera(self):
        """Stop the camera."""
        self.running = False
        self.camera_widget.play = False
        self.button.text = "Click to Activate"
        if self.opencv_capture:
            self.opencv_capture.release()


class iLertApp(App):
    def build(self):
        return CameraWidget()


if __name__ == '__main__':
    iLertApp().run()
