import cv2
import numpy as np
import tkinter as tk
from pynput.mouse import Button, Controller



def click(pinchFlag, conts):
    '''
    Performs a click based on the pinchFlag and use the image´s countours
    to define a new rectangle
    Args:
        pinchFlag Flag to controls the clicks
        conts Countours of the image
    Returns:
        mouseLoc Mouse coordinates location
        pinchFlag Flag to controls the clicks
    '''
    print("click!")
    x, y, w, h = cv2.boundingRect(conts[0])
    # drawing the rectangle
    cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
    cx = int(x + w / 2)
    cy = int(y + h / 2)
    cv2.circle(img, (cx, cy), int((w + h) / 4), (0, 0, 255), 2)

    if (pinchFlag == 0):  # perform only if pinch is off
        pinchFlag = 1  # setting pinch flag on
        mouse.press(Button.left)

    mouseLoc = (sx - (cx * sx / camx), cy * sy / camy)
    return mouseLoc, pinchFlag


# Define the color to track
lowerBound = np.array([29,86,6])
upperBound = np.array([64, 255, 255])

cam= cv2.VideoCapture(0)
kernelOpen=np.ones((5,5))
kernelClose=np.ones((20,20))

font = cv2.FONT_HERSHEY_SIMPLEX

mouse=Controller()

root = tk.Tk()
sx = root.winfo_screenwidth()
sy = root.winfo_screenheight()
camx,camy = 340,220
print(sx,sy)
pinchFlag = 0

while True:
    # Read every frame from the cam and normalize the image
    ret, img = cam.read()
    img = cv2.resize(img,(340,220))

    #convert BGR to HSV
    imgHSV= cv2.cvtColor(img,cv2.COLOR_BGR2HSV)
    # create the Mask
    mask=cv2.inRange(imgHSV,lowerBound,upperBound)

    # Morphology: Define the mask
    maskOpen = cv2.morphologyEx(mask,cv2.MORPH_OPEN,kernelOpen)
    maskClose = cv2.morphologyEx(maskOpen,cv2.MORPH_CLOSE,kernelClose)
    maskFinal = maskClose

    # Find the contours based on the mask
    conts,h = cv2.findContours(maskFinal.copy(),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
    n_objects = len(conts)

    cv2.drawContours(img, conts, -1, (255,0,0), 3)

    if conts:
        if n_objects == 1:
            mouseLoc, pinchFlag = click(pinchFlag, conts)

        else:
            mouse.release(Button.left)
            # Wrap in a rectangle every object that get into the camera ROV
            for obj in range(0, len(conts)):
                x, y, w, h = cv2.boundingRect(conts[obj])
                cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 2)

            x1, y1, w1, h1 = cv2.boundingRect(conts[0])
            x1 = int(x1 + w1 / 2)
            y1 = int(y1 + h1 / 2)

            # Draws a center for the main image to track
            cv2.circle(img, (x1, y1), 2, (0, 0, 255), 2)
            mouseLoc = (sx - (x1 * sx / camx), y1 * sy / camy)
            if (pinchFlag == 1):  # perform only if pinch is on
                pinchFlag = 0  # setting pinch flag off


        # Compute mouse location
        mouse.position = mouseLoc
    else:
        mouse.release(Button.left)


    # Release every frame
    cv2.imshow("cam",img)
    cv2.waitKey(10)

