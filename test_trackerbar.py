import numpy as np
import cv2
import tkinter as tk
from pynput.mouse import Button, Controller
    
def segmentation(mirror=False):
    
    lowerBound = np.array([41,0,0])
    upperBound = np.array([79, 255, 255])
    
    font = cv2.FONT_HERSHEY_SIMPLEX
    
    # creating mouse controller
    mouse=Controller()
    
    # find screen size

    root = tk.Tk()
    sx = root.winfo_screenwidth()
    sy = root.winfo_screenheight()
    camx,camy = 340,220
    print(sx,sy)

    cv2.namedWindow("color_hsv",1)

    cam= cv2.VideoCapture(0)
    kernelOpen=np.ones((5,5))
    kernelClose=np.ones((20,20))

    font = cv2.FONT_HERSHEY_SIMPLEX

    def nothing():
        pass
    
    #set trackbar
    hh = 'hue high'
    hl = 'hue low'
    sh = 'saturation high'
    sl = 'saturation low'
    vh = 'value high'
    vl = 'value low'

    #set ranges
    cv2.createTrackbar(hh, "color_hsv", upperBound[0],179, nothing)
    cv2.createTrackbar(hl, "color_hsv", lowerBound[0],179, nothing)
    cv2.createTrackbar(sh, "color_hsv", upperBound[1],255, nothing)
    cv2.createTrackbar(sl, "color_hsv", lowerBound[1],255, nothing)
    cv2.createTrackbar(vh, "color_hsv", upperBound[2],255, nothing)
    cv2.createTrackbar(vl, "color_hsv", lowerBound[2],255, nothing)

    thv= 'th1'
    
    cv2.createTrackbar(thv, "color_hsv", 127,255, nothing)
    
    # initialization variable
    pauseMode = False 
    while True:
        
        ret, img=cam.read()
        img=cv2.resize(img,(340,220))
        
        if not pauseMode:
            #convert BGR to HSV
            imgHSV= cv2.cvtColor(img,cv2.COLOR_BGR2HSV)
            
            hul= cv2.getTrackbarPos(hl,"color_hsv")
            huh= cv2.getTrackbarPos(hh,"color_hsv")
            sal= cv2.getTrackbarPos(sl,"color_hsv")
            sah= cv2.getTrackbarPos(sh,"color_hsv")
            val= cv2.getTrackbarPos(vl,"color_hsv")
            vah= cv2.getTrackbarPos(vh,"color_hsv")
            thva= cv2.getTrackbarPos(thv,"color_hsv")
    
            hsvl = np.array([hul, sal, val], np.uint8)
            hsvh = np.array([huh, sah, vah], np.uint8)
    
            # create the Mask
            mask = cv2.inRange(imgHSV, hsvl, hsvh)
    
            res = cv2.bitwise_and(img, img, mask=mask)
            
            #morphology
            maskOpen=cv2.morphologyEx(mask,cv2.MORPH_OPEN,kernelOpen)
            maskClose=cv2.morphologyEx(maskOpen,cv2.MORPH_CLOSE,kernelClose)
        
            maskFinal=maskClose
            conts,h=cv2.findContours(maskFinal.copy(),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
            
            cv2.drawContours(img,conts,-1,(255,0,0),3)
            
            for i in range(len(conts)):
                x,y,w,h=cv2.boundingRect(conts[i])
                cv2.rectangle(img,(x,y),(x+w,y+h),(0,0,255), 2)
                # cv2.cv.PutText(cv2.cv.fromarray(img), str(i+1),(x,y+h),font,(0,255,255))
            
            # Moments to find the center of the object detection
            for c in conts:
                M = cv2.moments(c)
        
                if M["m00"] != 0:
                    cX = int(M["m10"] / M["m00"])
                    cY = int(M["m01"] / M["m00"])
                else:
                    cX, cY = 0, 0
                tempStr = str(cX) + ", " + str(cY)
                cv2.circle(img, (cX,cY),2,(0,0,255),2) #make a dot at the center of the object 
                mouseLoc = (sx - (cX * sx / camx), cY * sy / camy)
                mouse.position = mouseLoc
                #print the coordinates on the image
        
        # cv2.imshow("maskClose", maskClose)
        # cv2.imshow("maskOpen", maskOpen)
        # cv2.imshow("mask", mask)
        cv2.imshow("cam", img)
        
        if cv2.waitKey(1) == 27: 
            break  # esc to quit
    cv2.destroyAllWindows()


def main():
    segmentation(mirror=True)

if __name__ == '__main__':
    main()
