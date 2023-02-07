"""
#识别手部

"""
import cv2
import numpy as np
import mediapipe as mp
import math
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import autopy

# volume.GetMute()
# volume.GetMasterVolumeLevel()
wScr, hScr = autopy.screen.size()
wCam, hCam = 640, 480
frameR = 100  # Frame Reduction
smoothening = 7
#########################


class HandRecognition:
    def __init__(self, mode=False, maxHands=2, model_complexity=1, detectionCon=0.5, trackCon=0.5):
        self.mode = mode
        self.maxHands = maxHands
        self.modelcomplexity = model_complexity
        self.detectionCon = detectionCon
        self.trackCon = trackCon

        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(self.mode, self.maxHands, self.modelcomplexity,
                                        self.detectionCon, self.trackCon)
        self.mpDraw = mp.solutions.drawing_utils

        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(
            IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        self.volume = cast(interface, POINTER(IAudioEndpointVolume))
        volRange = self.volume.GetVolumeRange()
        self.minVol = volRange[0]
        self.maxVol = volRange[1]
        # print(self.minVol, self.maxVol)
        self.tipIds = [4, 8, 12, 16, 20]

    def findHands(self, frame, draw=True, drawcircle=False,dismodel=True):
        imgRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)
        if self.results.multi_hand_landmarks:
            for handLms in self.results.multi_hand_landmarks:
                if drawcircle:
                    for id, lm in enumerate(handLms.landmark):
                        h, w, c = frame.shape
                        cx, cy = int(lm.x * w), int(lm.y * h)
                        print(id, cx, cy)
                        if id % 4 == 0 and id != 0:
                            cv2.circle(frame, (cx, cy), 15,
                                       (255, 255, 0), cv2.FILLED)
                if draw:
                    self.mpDraw.draw_landmarks(
                        frame, handLms, self.mpHands.HAND_CONNECTIONS)
        return frame

    def findPosition(self, img, handNo=0, draw=True):
        lmList = []
        if self.results.multi_hand_landmarks:
            myHand = self.results.multi_hand_landmarks[handNo]
            for id, lm in enumerate(myHand.landmark):
                # print(id, lm)
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                # print(id, cx, cy)
                lmList.append([id, cx, cy])
                if draw:
                    cv2.circle(img, (cx, cy), 15, (255, 0, 255), cv2.FILLED)

        return lmList

    def findPositionandbox(self, img, handNo=0, draw=True):
        xList = []
        yList = []
        bbox = []
        self.lmList = []
        if self.results.multi_hand_landmarks:
            myHand = self.results.multi_hand_landmarks[handNo]
            for id, lm in enumerate(myHand.landmark):
                # print(id, lm)
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                xList.append(cx)
                yList.append(cy)
                # print(id, cx, cy)
                self.lmList.append([id, cx, cy])
                if draw:
                    cv2.circle(img, (cx, cy), 5, (255, 0, 255), cv2.FILLED)

            xmin, xmax = min(xList), max(xList)
            ymin, ymax = min(yList), max(yList)
            bbox = xmin, ymin, xmax, ymax

            if draw:
                cv2.rectangle(img, (xmin - 20, ymin - 20), (xmax + 20, ymax + 20),
                              (0, 255, 0), 2)

        return self.lmList, bbox

    def gesturecontrol(self, frame):
        lmList = self.findPosition(frame, draw=False)
        if len(lmList) != 0:
            # print(lmList[4], lmList[8])
            # 两个手指的坐标
            x1, y1 = lmList[4][1], lmList[4][2]
            x2, y2 = lmList[8][1], lmList[8][2]
            # 计算中间值
            cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

            # 两个手指的指尖
            cv2.circle(frame, (x1, y1), 10, (255, 255, 255), cv2.FILLED)
            cv2.circle(frame, (x2, y2), 10, (255, 255, 255), cv2.FILLED)
            # 连接两个手指画线
            cv2.line(frame, (x1, y1), (x2, y2), (255, 255, 255), 2)
            # 在线的中间画一个圆
            cv2.circle(frame, (cx, cy), 15, (255, 0, 255), cv2.FILLED)
            # 计算两个手指之间的长度
            length = math.hypot(x2 - x1, y2 - y1)
            print(length)

            vol = np.interp(length, [50, 300], [self.minVol, self.maxVol])
            volBar = np.interp(length, [50, 300], [400, 150])
            volPer = np.interp(length, [50, 300], [0, 100])
            print(int(length), vol)
            self.volume.SetMasterVolumeLevel(vol, None)

            # 如果长度小于100时
            if length < 100:
                cv2.circle(frame, (cx, cy), 15, (255, 255, 255), cv2.FILLED)

            cv2.rectangle(frame, (50, 150), (85, 400), (255, 255, 0), 2)
            cv2.rectangle(frame, (50, int(volBar)), (85, 400),
                          (255, 255, 0), cv2.FILLED)
            cv2.putText(frame, f'{int(volPer)} %', (40, 450), cv2.FONT_HERSHEY_COMPLEX,
                        1, (255, 0, 0), 3)
        return frame

    def fingersUp(self):
        fingers = []
        # Thumb
        if self.lmList[self.tipIds[0]][1] > self.lmList[self.tipIds[0] - 1][1]:
            fingers.append(1)
        else:
            fingers.append(0)

        # Fingers
        for id in range(1, 5):

            if self.lmList[self.tipIds[id]][2] < self.lmList[self.tipIds[id] - 2][2]:
                fingers.append(1)
            else:
                fingers.append(0)

        # totalFingers = fingers.count(1)

        return fingers

    def findDistance(self, p1, p2, img, draw=True, r=15, t=3):
        x1, y1 = self.lmList[p1][1:]
        x2, y2 = self.lmList[p2][1:]
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

        if draw:
            cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), t)
            cv2.circle(img, (x1, y1), r, (255, 0, 255), cv2.FILLED)
            cv2.circle(img, (x2, y2), r, (255, 0, 255), cv2.FILLED)
            cv2.circle(img, (cx, cy), r, (0, 0, 255), cv2.FILLED)
        length = math.hypot(x2 - x1, y2 - y1)

        return length, img, [x1, y1, x2, y2, cx, cy]

    def handaivirtualmouse(self, frame):
        lmList, box = self.findPositionandbox(frame, draw=False)
        if len(lmList) != 0:
            x1, y1 = lmList[8][1:]
            x2, y2 = lmList[12][1:]
        fingers = self.fingersUp()
        print(fingers)
        cv2.rectangle(frame, (frameR, frameR), (wCam - frameR, hCam - frameR),
                      (255, 0, 255), 2)
        if fingers[1] == 1 and fingers[2] == 0:
            # 5. Convert Coordinates
            x3 = np.interp(x1, (frameR, wCam - frameR), (0, wScr))
            y3 = np.interp(y1, (frameR, hCam - frameR), (0, hScr))
            # 6. Smoothen Values
            plocX, plocY = 0, 0
            clocX, clocY = 0, 0
            clocX = plocX + (x3 - plocX) / smoothening
            clocY = plocY + (y3 - plocY) / smoothening

            autopy.mouse.move(wScr - clocX, clocY)
            cv2.circle(frame, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
            plocX, plocY = clocX, clocY

            # 8. Both Index and middle fingers are up : Clicking Mode
        if fingers[1] == 1 and fingers[2] == 1:
            # 9. Find distance between fingers
            length, frame, lineInfo = self.findDistance(8, 12, frame)
            print(length)
            # 10. Click mouse if distance short
            if length < 40:
                cv2.circle(frame, (lineInfo[4], lineInfo[5]),
                           15, (0, 255, 0), cv2.FILLED)
                autopy.mouse.click()
        return frame
