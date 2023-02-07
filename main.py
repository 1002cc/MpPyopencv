import cv2
import time

import HandRecognition  # 手部识别
import FaceRecognition  # 脸部识别
import PoseRecognition  # 肢体检测
import VirtualMouseControl
import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QDesktopWidget
from PyQt5.QtGui import *
from opencvfh import Ui_MainWindow
from PyQt5.QtCore import QTimer


class PyQtMainEntry(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.cap = cv2.VideoCapture(0)
        self.is_camera_opened = False
        # 功能标志位
        # 计算帧率
        self.pTime = 0
        # 显示
        self.DISPLAY = True
        # 手部识别
        self.HAND = False
        # 音量控制
        self.VALUE = False
        # 脸部识别
        self.FACE = False
        # 脸部识别标志位
        self.FACEFLAG = 0
        # 肢体识别
        self.POSE = False
        # 显示帧率
        self.DISFPS = False
        # 虚拟识别控制
        self.VMFLAG = False
        # 创建手部识别对象
        self.detector = HandRecognition.HandRecognition(detectionCon=0.7)
        # 创建脸部识别对象
        self.facemodel = FaceRecognition.FaceRecognition()
        # 创建肢体检测对象
        self.posemodel = PoseRecognition.PoseRecognition()
        # 创建手部控制鼠标对象
        self.control = VirtualMouseControl.VirtualMouseControl()
        # 定时器：30ms捕获一帧
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._queryFrame)
        self._timer.setInterval(30)

    def colseprogram(self):
        exit()

    def controlcamera(self):
        self.is_camera_opened = ~self.is_camera_opened
        if self.is_camera_opened:
            self.cameraButton.setText("关闭摄像头")
            self._timer.start()
        else:
            self.cameraButton.setText("打开摄像头")
            self._timer.stop()

    def setdis(self):
        if self.DISPLAY:
            self.DISPLAY = False
        else:
            self.DISPLAY = True

    def disface(self):
        if self.FACE:
            self.FACE = False
        else:
            self.FACE = True
        self.FACEFLAG += 1

    def dishand(self):
        if self.HAND:
            self.HAND = False
        else:
            self.HAND = True

    def dispose(self):
        if self.POSE:
            self.POSE = False
        else:
            self.POSE = True

    def controlvalue(self):
        if self.VALUE:
            self.VALUE = False
        else:
            self.VALUE = True

    def disfps(self):
        if self.DISFPS:
            self.DISFPS = False
        else:
            self.DISFPS = True

    def VirtualMouseControl_Clicked(self):
        if self.VMFLAG:
            self.VMFLAG = False
        else:
            self.VMFLAG = True

    def _queryFrame(self):
        ret, frame = self.cap.read()

        if self.HAND or self.VALUE:
            # 手部识别接口
            frame = self.detector.findHands(frame, True)
        if self.VALUE:
            # 手势控制音量接口
            frame = self.detector.gesturecontrol(frame)
        if self.FACE:
            if self.FACEFLAG % 3 == 0:
                # 脸部识别接口
                frame = self.facemodel.facecomparison(frame)
            elif self.FACEFLAG % 3 == 1:
                # 脸部3d接口
                frame = self.facemodel.fece3dmediapipe(frame)
            elif self.FACEFLAG % 3 == 2:
                # 脸部数据接口
                frame = self.facemodel.facedatemediapipe(frame)
        if self.POSE:
            # 肢体检测接口
            frame = self.posemodel.posemodel(frame)
        if self.VMFLAG:
            # 手势控制接口
            frame = self.control.vmousecontrol(frame)
        if self.DISFPS:
            # 计算帧率
            cTime = time.time()
            print(cTime)
            fps = 1 / (cTime - self.pTime)
            self.pTime = cTime
            cv2.putText(frame, str(int(fps)), (10, 70),
                        cv2.FONT_HERSHEY_PLAIN, 3, (255, 255, 255), 3)
        if self.DISPLAY:
            # 翻转图像
            frame = cv2.flip(frame, 1)
            img = QImage(frame.data, frame.shape[1], frame.shape[0], 3 * frame.shape[1],
                         QImage.Format.Format_BGR888)
            pixmap = QPixmap.fromImage(img)
            self.imglabel.setPixmap(pixmap)
        if cv2.waitKey(1) == 27:
            self.capture.release()
            cv2.destroyAllWindows()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon('icon/favicon.ico'))  # 设置窗体图标
    window = PyQtMainEntry()
    window.show()
    sys.exit(app.exec_())
