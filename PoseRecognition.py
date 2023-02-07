import cv2
import mediapipe as mp


class PoseRecognition:
    def __init__(self):
        self.mpPose = mp.solutions.pose
        self.pose = self.mpPose.Pose()
        self.draw = mp.solutions.drawing_utils

    def posemodel(self, frame):
        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.pose.process(img)
        if results.pose_landmarks:
            self.draw.draw_landmarks(frame, results.pose_landmarks, self.mpPose.POSE_CONNECTIONS)
            for id, lm in enumerate(results.pose_landmarks.landmark):
                        h, w, c = frame.shape
                        cx, cy = int(lm.x * w), int(lm.y * h)
                        print(id, cx, cy)
                        cv2.circle(frame, (cx, cy), 5, (255, 255, 0), cv2.FILLED)

        return frame