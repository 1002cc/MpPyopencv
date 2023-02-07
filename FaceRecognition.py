"""
#识别人脸

"""
import cv2
import cv2.face
import mediapipe as mp


class FaceRecognition:
    def __init__(self, faceclassifier="xml/haarcascade_frontalface_alt2.xml", myreconginr="xml/MyFacePCAModel.xml"):
        self.recoginer = cv2.face.EigenFaceRecognizer_create()
        self.recoginer.read(myreconginr)
        self.face_cascade = cv2.CascadeClassifier(faceclassifier)

        self.facmesh = mp.solutions.face_mesh
        self.face = self.facmesh.FaceMesh(static_image_mode=True, min_tracking_confidence=0.6,
                                          min_detection_confidence=0.6)
        self.draw = mp.solutions.drawing_utils

        mpFacedatection = mp.solutions.face_detection
        self.facedatation = mpFacedatection.FaceDetection()

    def facecomparison(self, frame, displayresizeimg=False):
        grayimg = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(grayimg, 1.2, 5)
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
            faceimg = grayimg[y:y + h, x:x + w]
            resized = cv2.resize(faceimg, (200, 200), interpolation=cv2.INTER_AREA)
            if displayresizeimg:
                cv2.imshow('frame1', resized)
            label, confidence = self.recoginer.predict(resized)
            print(label, confidence)
        return frame

    def fece3dmediapipe(self, frame):
        RGBimg = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face.process(RGBimg)
        if results.multi_face_landmarks:
            for i in results.multi_face_landmarks:
                self.draw.draw_landmarks(frame, i, self.facmesh.FACEMESH_CONTOURS,
                                         landmark_drawing_spec=self.draw.DrawingSpec(circle_radius=1))
        return frame

    def facedatemediapipe(self, frame):
        RGBimg = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.facedatation.process(RGBimg)
        if results.detections:
            for id, detection in enumerate(results.detections):
                # self.draw.draw_detection(frame, detection)
                bboxC = detection.location_data.relative_bounding_box
                ih, iw, ic = frame.shape
                bbox = int(bboxC.xmin * iw), int(bboxC.ymin * ih), \
                    int(bboxC.width * iw), int(bboxC.height * ih)
                cv2.rectangle(frame, bbox, (255, 255, 255), 2)
                cv2.putText(frame, f'{int(detection.score[0] * 100)}%', (bbox[0], bbox[1] - 20), cv2.FONT_HERSHEY_PLAIN,
                            3, (255, 255, 255), 2)
        return frame
