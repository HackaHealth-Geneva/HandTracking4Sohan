import cv2
import numpy as np
import tkinter as tk
#from pynput.mouse import Button, Controller
import win32api
import pyautogui
import mouse
import time 
from time import sleep

lowerBound = np.array([29,86,6])
upperBound = np.array([64, 255, 255])

cam= cv2.VideoCapture(0)
kernelOpen=np.ones((5,5))
kernelClose=np.ones((20,20))

font = cv2.FONT_HERSHEY_SIMPLEX


# creating mouse controller
#mouse=Controller()



# find screen size

root = tk.Tk()
sx = root.winfo_screenwidth()
sy = root.winfo_screenheight()
camx,camy = 340,220
print(sx,sy)
# cv2.namedWindow("cam",cv2.WINDOW_NORMAL)
# initialization variablez
pauseMode = False 

mouse.right_click()

while True:
    ret, img=cam.read()
    img=cv2.resize(img,(340,220))
    
    if not pauseMode:
    #convert BGR to HSV
        imgHSV= cv2.cvtColor(img,cv2.COLOR_BGR2HSV)
        # create the Mask
        mask=cv2.inRange(imgHSV,lowerBound,upperBound)
        #morphology
        maskOpen=cv2.morphologyEx(mask,cv2.MORPH_OPEN,kernelOpen)
        maskClose=cv2.morphologyEx(maskOpen,cv2.MORPH_CLOSE,kernelClose)
    
        maskFinal=maskClose
        conts,h=cv2.findContours(maskFinal.copy(),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
            
        cv2.drawContours(img,conts,-1,(255,0,0),3)
        # for i in range(len(conts)):
        if conts: 
            x,y,w,h=cv2.boundingRect(conts[0])
            cv2.rectangle(img,(x,y),(x+w,y+h),(0,0,255), 2)
            x1,y1,w1,h1=cv2.boundingRect(conts[0])
            x1=int(x1+w1/2)
            y1=int(y1+h1/2)
            cv2.circle(img, (x1,y1),2,(0,0,255),2)
            #mouseLoc = (sx - (x1 * sx / camx), y1 * sy / camy)
            x =sx - (x1 * sx / camx)
            y =y1 * sy / camy
            
            mouse.move(int(x),int(y))
           
            
    
           
            
            # win32api.SetCursorPos((int(x),int(y)))
            # pyautogui.moveTo((int(x),int(y)))
            
            #mouse.position = mouseLoc
            # while mouse.position != mouseLoc:
               # pass
    
            
            # cv2.imshow("maskClose",maskClose)
            # cv2.imshow("maskOpen",maskOpen)
            # cv2.imshow("mask",mask)
    cv2.imshow("cam",img)
    
    key = cv2.waitKey(1) & 0xFF
   
    if key == ord("q"):
            break

    if key == ord('a'):
        mouse.right_click()
        time.sleep(1)
        # cv2.destroyAllWindows()
        # cv2.namedWindow("cam",cv2.WINDOW_NORMAL)
    cv2.waitKey(10)

cam.release()
cv2.destroyAllWindows()
