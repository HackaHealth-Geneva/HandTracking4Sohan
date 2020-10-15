import mouse
import os
import time
import PIL
import cv2
import numpy as np
import threading
import configparser

import ast
import warnings
import serial
import serial.tools.list_ports



from PIL import Image,ImageTk
from tkinter import *

from os import path
from pynput.keyboard import Key,KeyCode, Controller
from pynput.mouse import Controller
from pynput.mouse import Button as mButton

# import unrar
# from unrar import rarfile
# from tt import KeyboardController


class CameraInterface:
    def __init__(self,config_file):

        # READ CONFIG FILE
        self.config_file = config_file
        self.config = configparser.ConfigParser()
        self.config.read(self.config_file)
        
        # self.lowerBound = np.array([29, 86, 6])
        # self.upperBound = np.array([64, 255, 255])

        self.lowerBound = np.array([53, 74, 160])
        self.upperBound = np.array([90, 147, 255])#h:53-90 s:74-147 v: 160-255
        self.root = Tk()
        self.root.bind('<Escape>', lambda e: self.root.quit())
        self.root.title('HandTracking4Sohan')
        self.root.configure(background="gray77")
        self.root.resizable(1,1)

        path_icon = os.path.join(r'.\Icon','HackaHealth_Logo_tkinter.ico')
        self.root.wm_iconbitmap(path_icon)

        # Config file
        # Window params
        self.cam_x = self.config.getint("window","camx")
        self.cam_y = self.config.getint("window","camy")
        self.refresh_rate = self.config.getint("window","refresh_rate")
        
        # Tracking params
        self.use_cam = self.config.getboolean("tracking_params","use_cam")
        kernel_o = self.config.getint("tracking_params","kernel_o")
        kernel_c = self.config.getint("tracking_params","kernel_c")
        cam_id = self.config.getint("camera","cam_id")

        self.kernelOpen = np.ones((kernel_o, kernel_o))
        self.kernelClose = np.ones((kernel_c, kernel_c))
        self.cam = cv2.VideoCapture(cam_id)
        # ret, self.img = self.cam.read()

        # Game params
        self.path_game = ast.literal_eval(self.config.get("game", "path_game")) 
        # if not os.path.exists(self.path_game):
        #     print("Unzipping the game")
        #     # specifying the zip file name 
        #     file_name = "buildfordemo2"
        #     rar = rarfile.RarFile(file_name)
        #     print(rar.namelist())

        #     rar.extractall()
        #     print('Extracting all the files now...') 
        #     print('Done!') 

        self.font = cv2.FONT_HERSHEY_SIMPLEX
        
        # Mouse Controller
        self.varMouse = IntVar()
        self.varClick = IntVar()
        self.mouse = Controller()

        # Capacitive sensor
        self.coord_x = 120
        self.coord_y = 60
        self.circle_radius = 10
        self.circle_color_arrow = (255, 0, 0)
        self.circle_color_switch = (0, 0, 255)
        self.circle_color_touch = (0, 255, 0)
        self.circle_thickness = -5

        # Interface 
        self.lmain = Label(self.root)


        self.red = Button(self.root, text="red", command=self.detectRed,state='disabled',bg='gray72')
        self.green = Button(self.root, text="green", command=self.detectGreen,state='disabled',bg='gray72')
        self.blue = Button(self.root, text="blue", command=self.detectBlue,state='disabled',bg='gray72')
        # self.rgbContainer = Label(self.root, text="test")
        self.mouseCheckbox = Checkbutton(self.root, text="Mouse Controller On/Off", variable=self.varMouse, command=self.mouseMovement,background="gray77")
        # self.clickCheckbox = Checkbutton(self.root, text="control with click?", variable=self.varClick, command=self.clickControl)
        self.gameButton = Button(self.root, text="Game Training", command=self.launchGame, bg="violet")

        # self.startCam = Button(self.root, text="start camera", command=self.startThread)

        self.lmain.grid(row=0, column=0, columnspan=2)
        self.red.grid(row=1, column=0, sticky='nesw',pady=1)
        self.green.grid(row=2, column=0, sticky='nesw',pady=1)
        self.blue.grid(row=3, column=0, sticky='nesw',pady=1)
        # self.rgbContainer.grid(row=1, column=1, rowspan=3, sticky='nesw')


        self.mouseCheckbox.grid(row=1, column=1,  sticky='nesw')
        # self.clickCheckbox.grid(row=2, column=1,  sticky='nesw')
        self.gameButton.grid(row=4, column=0, columnspan=2, sticky='nesw')
        # self.startCam.grid(row=4, column=0, columnspan=3)

        self.screen_x = self.root.winfo_screenwidth()
        self.screen_y = self.root.winfo_screenheight()

        # Initilization params
        self.mouseOn = False
        self.clickControlOn = False
        self.pinchFlag = False

        # Arduino Params
        self.ser = self.connect_to_arduino_if_exist()
        self.data = [50]

    def connect_to_arduino_if_exist(self):

        arduino_ports = [
            p.device
            for p in serial.tools.list_ports.comports()
            if 'Arduino' in p.description  # may need tweaking to match new arduinos
        ]
        try:
            if not arduino_ports:
                raise IOError("No Arduino found")
            if len(arduino_ports) > 1:
                warnings.warn('Multiple Arduinos found - using the first')
            ser = serial.Serial(port =arduino_ports[0], baudrate ="9600");
        except:
            print("Arduino is not connected")
            ser = []
        return ser

    def launchGame(self):
    
        self.mouseCheckbox.select()
        
        try: 
            #os.startfile('C:\\Users\\GPUser\\Documents\\HandTracking4Sohan-main\\buildfordemo\\buildfordemo\\Sohan_project.exe')
            # os.startfile(r'C:\Users\basti\git\HandTracking4Sohan\Sohan_project_Unity\Build\buildfordemo2\Sohan_project.exe')
            os.startfile(self.path_game)
        except Exception as e:
                print(e)
                print('Cannot launch game')
        
    def detectRed(self):
        self.lowerBound = np.array([170, 120, 150])
        self.upperBound = np.array([190, 255, 255])

    def detectGreen(self):
        self.lowerBound = np.array([29, 86, 6])
        self.upperBound = np.array([64, 255, 255])

    def detectBlue(self):
        self.lowerBound = np.array([110, 150, 100])
        self.upperBound = np.array([120, 255, 255])

    def startThread(self):
        threadPort = threading.Thread(target=self.readPort)
        threadPort.start()
    
    def readPort(self):
        if self.ser:
            self.data = self.ser.readline()
            print('data ' + str(self.data[0]))
    
    def doAction(self):
        print("do action")

    def mouseMovement(self):
        if self.varMouse.get():
            print("mouseOn")
            self.mouseOn = True
            self.use_cam = True
            self.red["state"] = "active"
            self.red['bg']="Red"
            self.green["state"] = "active"
            self.green['bg']="SpringGreen2"
            self.blue["state"] = "active"
            self.blue['bg']="Sky Blue"

            
        else:
            print("mouseOff")
            self.mouseOn = False
            self.use_cam = False
            self.red["state"] = "disabled"
            self.red['bg']="gray72"
            self.green["state"] = "disabled"
            self.green['bg']="gray72"
            self.blue["state"] = "disabled"
            self.blue['bg']="gray72"

            

    def selected(self):
        if self.varMouse.get():
            self.mouseCheckbox.deselect()
        else:
            self.mouseCheckbox.select()

    def clickControl(self):
        if self.varClick.get():
            print("click control on")
            self.clickControlOn = True
        else:
            print("click control off")
            self.clickControlOn = False


    def click(self, pinchFlag, conts):
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
        cv2.rectangle(self.img, (x, y), (x + w, y + h), (255, 0, 0), 2)
        cx = int(x + w / 2)
        cy = int(y + h / 2)
        cv2.circle(self.img, (cx, cy), int((w + h) / 4), (0, 0, 255), 2)

        if not pinchFlag:  # perform only if pinch is off
            pinchFlag = True  # setting pinch flag on
            mouse.click()
            # self.mouse.press(mButton.left)

        mouseLoc = (self.screen_x - (cx * self.screen_x / self.cam_x), cy * self.screen_y / self.cam_y)
        return mouseLoc, pinchFlag

    def show_frame(self):
        # read from port
        #if self.data[0] is 53:
        #    self.selected()

        if self.use_cam:
            ret, self.img = self.cam.read()
            # flipping for the selfie cam right now to keep same
            # self.img = cv2.flip(self.img, 1)
            self.img = cv2.resize(self.img, (self.cam_x, self.cam_y))

            # convert BGR to HSV
            frame = cv2.cvtColor(self.img, cv2.COLOR_RGB2BGR)
            imgHSV = cv2.cvtColor(self.img, cv2.COLOR_BGR2HSV)
        
            # create the Mask + morphology
            mask = cv2.inRange(imgHSV, self.lowerBound, self.upperBound)
            maskOpen = cv2.morphologyEx(mask, cv2.MORPH_OPEN, self.kernelOpen)
            maskClose = cv2.morphologyEx(maskOpen, cv2.MORPH_CLOSE, self.kernelClose)

            maskFinal = maskClose
            conts, h = cv2.findContours( maskFinal.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
            n_objects = len(conts)
            cv2.drawContours(frame, conts, -1, (255, 0, 0), 3)

            if conts:
                x, y, w, h = cv2.boundingRect(conts[0])
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
                x1, y1, w1, h1 = cv2.boundingRect(conts[0])
                x1 = int(x1 + w1 / 2)
                y1 = int(y1 + h1 / 2)
                cv2.circle(frame, (x1, y1), 2, (0, 0, 255), 2)

            if self.mouseOn and len(conts) == 1:   # CHANGE HERE and len(conts) == 1 

                if (self.pinchFlag):  # perform only if pinch is on
                    self.pinchFlag = False
                    # self.mouse.release(mButton.left)
                    mouse.release()

                # Compute mouse location
                mouseLoc = ( (x1 * self.screen_x / self.cam_x), y1 * self.screen_y / self.cam_y)
                mouse.move(mouseLoc[0],mouseLoc[1])

                # Check for clicks
                # If there is only one object, it means both finger
                # (objects) collided so a click take place
                #if n_objects == 1:
                #    print("click")
                #    mouseLoc, pinchFlag = self.click(self.pinchFlag, conts)
                #
                # self.mouse.position = mouseLoc

            # TO BE IMPLEMENTED
            if self.clickControlOn:
                print("click control on")

        else:

            frame = np.zeros((self.cam_y,self.cam_x,3), np.uint8)
            
            cv2.circle(frame, (int(self.cam_x/2),int(self.cam_y/2)), self.circle_radius, self.circle_color_arrow, self.circle_thickness)
            
            cv2.circle(frame, (self.coord_x,int(self.cam_y/2)), self.circle_radius, self.circle_color_arrow, self.circle_thickness)
            cv2.circle(frame, (self.cam_x-self.coord_x,int(self.cam_y/2)), self.circle_radius, self.circle_color_arrow, self.circle_thickness)

            cv2.circle(frame, (int(self.cam_x/2),self.coord_y), self.circle_radius, self.circle_color_arrow, self.circle_thickness)
            cv2.circle(frame, (int(self.cam_x/2),self.cam_y-self.coord_y), self.circle_radius, self.circle_color_arrow, self.circle_thickness)
            
            if not self.use_cam:
                cv2.circle(frame, (int(self.cam_x/4),int(self.cam_y/4)), self.circle_radius, self.circle_color_switch, self.circle_thickness)
            else:
                cv2.circle(frame, (int(self.cam_x/4),int(self.cam_y/4)), self.circle_radius, self.circle_color_touch, self.circle_thickness)

            
        # pt1 = (int(self.camx/2), int(self.camy/2))
        # pt2 = (int(self.camx/4), int(self.camy/4))
        # cv2.arrowedLine(self.img, pt1, pt2, (0,0,255), 25)
        # cv2.arrowedLine(self.img, pt2, pt1, (0,0,255), 25)
        
        
        # Show camera output
        imgPIL = PIL.Image.fromarray(frame)
        imgtk = ImageTk.PhotoImage(image=imgPIL)
        self.lmain.imgtk = imgtk
        self.lmain.configure(image=imgtk)
        self.lmain.after(self.refresh_rate, self.show_frame)


if __name__ == "__main__":

    config_file = r".\config.ini"
    print('Changing cursor appearance')
    camInt = CameraInterface(config_file)
    #camInt.startThread()
    camInt.show_frame()
    camInt.root.mainloop()

