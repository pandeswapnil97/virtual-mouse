import cv2
import numpy as np
from pynput.mouse import Button, Controller
import pyautogui as pgui
import wx

mouse = Controller()

app = wx.App(False)
(sx, sy) = wx.GetDisplaySize()
(camx, camy) = (500, 500)

lowerBound = np.array([33, 80, 40])
upperBound = np.array([102, 255, 255])

# lowerBound = np.array([50, 100, 100])
# upperBound = np.array([70, 255, 255])

cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cam.set(3, camx)
cam.set(4, camy)

kernelOpen = np.ones((5, 5))
kernelClose = np.ones((20, 20))

mLocOld = np.array([0, 0])
mouseLoc = np.array([0, 0])
DampingFactor = 2     # should be > 1

pinchFlag = 0
openx, openy, openw, openh = (0, 0, 0, 0)
# mouseLoc = mLocOld + (target loc - mLocOld) / DampingFactor


while cam.isOpened():
    ret, img = cam.read()
    #print(type(img))
    # img = cv2.resize(img, (340, 220))

    # Convert BGR -> HSV
    imgHSV = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    # Create the mask
    mask = cv2.inRange(imgHSV, lowerBound, upperBound)
    # Morphology (Opening and Closing)
    maskOpen = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernelOpen)
    maskClose = cv2.morphologyEx(maskOpen, cv2.MORPH_OPEN, kernelClose)

    maskFinal = maskClose

    conts, hierarchy = cv2.findContours(maskFinal.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    # cv2.drawContours(img, conts, -1, (255, 0, 0), 3)
    # for i in range (len(conts)):
    #     x, y, w, h = cv2.boundingRect(conts[i])
    #     cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 2)
    #     cv2.putText(img, str(i+1), (x, y+h), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 255))
    if len(conts) == 2:
        if pinchFlag == 1:
            pinchFlag = 0
            mouse.release(Button.left)

        x1, y1, w1, h1 = cv2.boundingRect(conts[0])
        x2, y2, w2, h2 = cv2.boundingRect(conts[1])

        cv2.rectangle(img, (x1, y1), (x1 + w1, y1 + h1), (255, 0, 0), 2)
        cv2.rectangle(img, (x2, y2), (x2 + w2, y2 + h2), (255, 0, 0), 2)
        cx1 = x1+w1//2
        cy1 = y1+h1//2
        cx2 = x2+w2//2
        cy2 = y2+h2//2

        cx = (cx1 + cx2) // 2
        cy = (cy1 + cy2) // 2

        cv2.line(img, (cx1, cy1), (cx2, cy2), (255, 0, 0), 2)
        cv2.circle(img, (cx, cy), 2, (0, 0, 255), 2)
        mouseLoc = mLocOld + ((cx, cy) - mLocOld) / DampingFactor
        mouse.position = ((sx - (mouseLoc[0] * sx) // camx), (mouseLoc[1] * sy) // camy)
        while mouse.position != ((sx - (mouseLoc[0] * sx) // camx), (mouseLoc[1] * sy) // camy):
            pass
        mLocOld = mouseLoc
        openx, openy, openw, openh = cv2.boundingRect(np.array([[x1, y1], [x1 + w1, y1 + h1], [x2, y2],
                                                                [x2 + w2, y2 + h2]]))
        # cv2.rectangle(img, (openx, openy), (openx + openw, openy + openh), (255, 0, 0), 2)

    elif len(conts) == 1:
        x, y, w, h = cv2.boundingRect(conts[0])
        if pinchFlag == 0:
            if abs((x * h - openw * openh) * 100 // (w * h)) < 30:
                pinchFlag = 1
                #mouse.press(Button.left)
                pgui.doubleClick()
                openx, openy, openw, openh = (0, 0, 0, 0)
        else:
            cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
            cx = int(x+w//2)
            cy = int(y+h//2)
            cv2.circle(img, (cx, cy), (w + h)//4, (0, 0, 255), 2)
            mouseLoc = mLocOld + ((cx, cy) - mLocOld) / DampingFactor
            mouse.position = ((sx - (mouseLoc[0] * sx) // camx), (mouseLoc[1] * sy) // camy)
            while mouse.position != ((sx - (mouseLoc[0] * sx) // camx), (mouseLoc[1] * sy) // camy):
                pass
            mLocOld = mouseLoc
        cv2.imshow("maskClose", maskClose)
        cv2.imshow("maskOpen", maskOpen)
        cv2.imshow("mask", mask)
    cv2.imshow("Camera", img)
    cv2.waitKey(5)
    #if cv2.waitKey(0) == ord('q'):
    #    break
cam.release()
cv2.destroyAllWindows()
