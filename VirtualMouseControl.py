import time
import autopy
import cv2
import numpy as np
import HandTrackingModule as Htm
import pyautogui as pag


class VirtualMouseControl:
    def __init__(self):
        # 帧缩减
        self.frameR = 100
        self.detector = Htm.HandDetector(maxHands=1)
        self.plocX, self.plocY = 0, 0
        self.smoothening = 7
        # 鼠标控制范围
        self.wScr, self.hScr = pag.size()
        self.wCam, self.hCam = 640, 480
        self.clicktime = 0

    def vmousecontrol(self, img):
        # 手部识别 传入图像 参数2是否绘制关键点线条
        img = self.detector.findHands(img, False)
        # 获取手部的坐标数据
        lmList, bbox = self.detector.findPosition(img, draw=False)
        # 获取食指和中指的指尖坐标数据
        if len(lmList) != 0:
            # 1: 获取列表从1开始的数据
            # [1:]--获取从位置1开始后面的字符（默认首位是0）
            # [: -1]--删除位置为 - 1的字符（也就是获取从位置0带位置 - 1之间的字符）
            # [-1:]--获取位置 - 1的字符
            # [::-1]--从最后一个元素到第一个元素复制一遍。(也就是倒序)
            # [:]--相当于完整复制一份str
            x1, y1 = lmList[8][1:]
            # x2, y2 = lmList[12][1:]
            # 检查哪些手指向上
            fingers = self.detector.fingersUp()
            # print(fingers)

            cv2.rectangle(img, (self.frameR, self.frameR), (self.wCam - self.frameR, self.hCam - self.frameR),
                          (255, 0, 255), 2)
            # 仅食指：移动模式
            if fingers[1] == 1 and fingers[2] == 0:
                # 转换坐标
                x3 = np.interp(x1, (self.frameR, self.wCam - self.frameR), (0, self.wScr))
                y3 = np.interp(y1, (self.frameR, self.hCam - self.frameR), (0, self.hScr))
                # 6. 计算平滑值
                clocX = self.plocX + (x3 - self.plocX) / self.smoothening
                clocY = self.plocY + (y3 - self.plocY) / self.smoothening
                # 移动鼠标
                # pag.moveTo(self.wScr - clocX, clocY)
                autopy.mouse.move(self.wScr - clocX, clocY)
                cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
                self.plocX, self.plocY = clocX, clocY

            # 8 食指和中指都向上：单击模式
            if fingers[1] == 1 and fingers[2] == 1:
                # 查找手指之间的距离
                length, img, lineInfo = self.detector.findDistance(8, 12, img)
                print(length)
                # 如果距离较短，请单击鼠标
                if length < 30:
                    cv2.circle(img, (lineInfo[4], lineInfo[5]),
                               15, (0, 255, 0), cv2.FILLED)
                    # 实现防点击抖动
                    if self.clicktime % 8 == 0:
                        autopy.mouse.click()
                self.clicktime += 1

        return img


def main():
    # 屏幕参数设置
    wCam, hCam = 640, 480
    frameR = 100  # Frame Reduction
    smoothening = 7
    # 帧率
    pTime = 0
    # 坐标
    plocX, plocY = 0, 0
    # clocX, clocY = 0, 0
    # 打开摄像头
    cap = cv2.VideoCapture(0)
    # 查看和设置摄像机参数
    # print(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    # print(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    # cap.set(cv2.CAP_PROP_FRAME_WIDTH, wCam)
    # cap.set(cv2.CAP_PROP_FRAME_HEIGHT, hCam)

    # 创建手部识别参数
    detector = Htm.HandDetector(maxHands=1)
    control = VirtualMouseControl()
    # 鼠标控制范围
    wScr, hScr = autopy.screen.size()
    print(wScr, hScr)
    while True:
        # 获取图像信息
        success, img = cap.read()
        # 翻转图像
        # img = cv2.flip(img, 1)
        # 手部识别 传入图像 参数2是否绘制关键点线条
        img = control.vmousecontrol(img)
        # img = detector.findHands(img, False)
        # # 获取手部的坐标数据
        # lmList, bbox = detector.findPosition(img, draw=False)
        # # 获取食指和中指的指尖坐标数据
        # if len(lmList) != 0:
        #     # 1: 获取列表从1开始的数据
        #     # [1:]--获取从位置1开始后面的字符（默认首位是0）
        #     # [: -1]--删除位置为 - 1的字符（也就是获取从位置0带位置 - 1之间的字符）
        #     # [-1:]--获取位置 - 1的字符
        #     # [::-1]--从最后一个元素到第一个元素复制一遍。(也就是倒序)
        #     # [:]--相当于完整复制一份str
        #     x1, y1 = lmList[8][1:]
        #     # x2, y2 = lmList[12][1:]
        #     # 检查哪些手指向上
        #     fingers = detector.fingersUp()
        #     # print(fingers)
        #
        #     cv2.rectangle(img, (frameR, frameR), (wCam - frameR, hCam - frameR),
        #                   (255, 0, 255), 2)
        #     # 仅食指：移动模式
        #     if fingers[1] == 1 and fingers[2] == 0:
        #         # 转换坐标
        #         x3 = np.interp(x1, (frameR, wCam - frameR), (0, wScr))
        #         y3 = np.interp(y1, (frameR, hCam - frameR), (0, hScr))
        #         # 6. 计算平滑值
        #         clocX = plocX + (x3 - plocX) / smoothening
        #         clocY = plocY + (y3 - plocY) / smoothening
        #         # 移动鼠标
        #         autopy.mouse.move(wScr - clocX, clocY)
        #         cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
        #         plocX, plocY = clocX, clocY
        #
        #     # 8 食指和中指都向上：单击模式
        #     if fingers[1] == 1 and fingers[2] == 1:
        #         # 查找手指之间的距离
        #         length, img, lineInfo = detector.findDistance(8, 12, img)
        #         print(length)
        #         # 如果距离较短，请单击鼠标
        #         if length < 40:
        #             cv2.circle(img, (lineInfo[4], lineInfo[5]),
        #                        15, (0, 255, 0), cv2.FILLED)
        #             autopy.mouse.click()
        # 计算帧率
        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime
        # 显示帧率
        cv2.putText(img, str(int(fps)), (20, 50), cv2.FONT_HERSHEY_PLAIN, 3,
                    (255, 0, 0), 3)
        cv2.imshow("Image", img)
        # ESC退出并处理cap
        if 27 == cv2.waitKey(1):
            cap.release()
            cv2.destroyAllWindows()


if __name__ == "__main__":
    main()



