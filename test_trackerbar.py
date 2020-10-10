import numpy as np
import cv2

def center(contours, frame):
    # calculate moments for each contour
    for c in contours:
        M = cv2.moments(c)

        if M["m00"] != 0:
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
        else:
            cX, cY = 0, 0
        tempStr = str(cX) + ", " + str(cY)
        cv2.circle(frame, (cX, cY), 1, (0, 0, 0), -1) #make a dot at the center of the object 
        cv2.putText(frame, tempStr, (cX - 25, cY - 25),cv2.FONT_HERSHEY_TRIPLEX, 0.4, (0, 0, 0), 1) 
        #print the coordinates on the image
    

def segmentation(mirror=False):
    
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
    mode = 'mode'

    #set ranges
    cv2.createTrackbar(hh, "color_hsv", 0,179, nothing)
    cv2.createTrackbar(hl, "color_hsv", 0,179, nothing)
    cv2.createTrackbar(sh, "color_hsv", 0,255, nothing)
    cv2.createTrackbar(sl, "color_hsv", 0,255, nothing)
    cv2.createTrackbar(vh, "color_hsv", 0,255, nothing)
    cv2.createTrackbar(vl, "color_hsv", 0,255, nothing)
    cv2.createTrackbar(mode, "color_hsv", 0,3, nothing)

    thv= 'th1'
    
    cv2.createTrackbar(thv, "color_hsv", 127,255, nothing)

    while True:
        
        ret, img=cam.read()
    
        #convert BGR to HSV
        imgHSV= cv2.cvtColor(img,cv2.COLOR_BGR2HSV)
        
        hul= cv2.getTrackbarPos(hl,"color_hsv")
        huh= cv2.getTrackbarPos(hh,"color_hsv")
        sal= cv2.getTrackbarPos(sl,"color_hsv")
        sah= cv2.getTrackbarPos(sh,"color_hsv")
        val= cv2.getTrackbarPos(vl,"color_hsv")
        vah= cv2.getTrackbarPos(vh,"color_hsv")
        thva= cv2.getTrackbarPos(thv,"color_hsv")

        modev= cv2.getTrackbarPos(mode,"color_hsv")

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
        
        # Moments to find the center of the objectdetected 
        for c in conts:
            M = cv2.moments(c)
    
            if M["m00"] != 0:
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
            else:
                cX, cY = 0, 0
            tempStr = str(cX) + ", " + str(cY)
            cv2.circle(img, (cX, cY), 1, (0, 0, 0), -1) #make a dot at the center of the object 
            cv2.putText(img, tempStr, (cX - 25, cY - 25),cv2.FONT_HERSHEY_TRIPLEX, 0.4, (0, 0, 0), 1) 
            #print the coordinates on the image
        
        cv2.imshow("maskClose", maskClose)
        cv2.imshow("maskOpen", maskOpen)
        cv2.imshow("mask", mask)
        cv2.imshow("cam", img)
        
        if cv2.waitKey(1) == 27: 
            break  # esc to quit
    cv2.destroyAllWindows()


def main():
    segmentation(mirror=True)

if __name__ == '__main__':
    main()
