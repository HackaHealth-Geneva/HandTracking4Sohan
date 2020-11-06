#import mouse
import os
import time
import PIL
import cv2
import numpy as np
import threading
import queue
from multiprocessing import Queue, Process
import configparser

import ast
import warnings
import serial
import serial.tools.list_ports


import ctypes
import math
import time

from ctypes import c_long, POINTER, sizeof, c_int
from ctypes.wintypes import DWORD

from PIL import Image,ImageTk
from tkinter import *
from PyQt5.QtCore import QThread, pyqtSignal,Qt,pyqtSlot
from os import path
from pynput.keyboard import Key,KeyCode, Controller,Listener
import pyautogui
#from pynput.mouse import Button as mButton

class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", c_long),
        ("dy", c_long),
        ("mouseData", DWORD),
        ("dwFlags", DWORD),
        ("time", DWORD),
        ("dwExtraInfo", POINTER(c_long)),
    ]

class INPUT(ctypes.Structure):
    _fields_ = [
        ("type", DWORD),
        ("mi", MOUSEINPUT),
    ]

# Define required native Win32 API constants
INPUT_MOUSE = 0
MOUSEEVENTF_MOVE     = 0x001
MOUSEEVENTF_LEFTDOWN = 0x002
MOUSEEVENTF_LEFTUP   = 0x004
        
class CameraInterface(Tk):
    def __init__(self,config_file):
        # READ CONFIG FILE
        self.config_file = config_file
        self.config = configparser.ConfigParser()
        self.config.read(self.config_file)
        
        self.lowerBound = np.array([29, 86, 6])
        self.upperBound = np.array([64, 255, 255])

        self.root = Tk()
        self.root.geometry('550x600+10+600')
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
        self.cam_id = self.config.getint("camera","cam_id")

        self.kernelOpen = np.ones((kernel_o, kernel_o))
        self.kernelClose = np.ones((kernel_c, kernel_c))
        self.cam = cv2.VideoCapture(self.cam_id)
        
        #Arduino Params
        self.ser  = self.connect_to_arduino_if_exist()
        self.data_ = None #None
        if self.ser:
             self.use_cam = False
            
        # Game params
        self.path_game = ast.literal_eval(self.config.get("game", "path_game")) 

        # Mouse Controller
        self.varMouse = IntVar()
        self.varClick = IntVar()
        self.thresholdDistance = 15

        # Interface 
        self.lmain = Label(self.root)
        self.red = Button(self.root, text="red", command=self.detectRed,state='disabled',bg='gray72')
        self.green = Button(self.root, text="green", command=self.detectGreen,state='disabled',bg='gray72')
        self.blue = Button(self.root, text="blue", command=self.detectBlue,state='disabled',bg='gray72')
        self.mouseCheckbox = Checkbutton(self.root, text="Mouse Controller On/Off", variable=self.varMouse, command=self.mouseMovement,background="gray77",state='normal')
        self.gameButton = Button(self.root, text="Game Training", command=self.launchGame, bg="violet")

        self.lmain.grid(row=0, column=0, columnspan=2)
        self.red.grid(row=1, column=0, sticky='nesw',pady=1)
        self.green.grid(row=2, column=0, sticky='nesw',pady=1)
        self.blue.grid(row=3, column=0, sticky='nesw',pady=1)
        # self.rgbContainer.grid(row=1, column=1, rowspan=3, sticky='nesw')

        self.mouseCheckbox.grid(row=1, column=1,  sticky='nesw')
        self.gameButton.grid(row=4, column=0, columnspan=2, sticky='nesw')
        # self.clickCheckbox.grid(row=2, column=1,  sticky='nesw')
        # self.startCam.grid(row=4, column=0, columnspan=3)

        self.screen_x = self.root.winfo_screenwidth()
        self.screen_y = self.root.winfo_screenheight()

        # Initilization params
        self.mouseOn = False
        self.clickControlOn = False
        self.pinchFlag = False
        self.justChanged = True
        self.pressedAlready = False

        # Capacitive sensor
        self.coord_x = 120
        self.coord_y = 60
        self.circle_radius = 10
        self.circle_color_arrow = (255, 0, 0)
        self.circle_color_switch = (0, 0, 255)
        self.circle_color_touch = (0, 255, 0)
        self.circle_thickness = -5
        self.time_not_changing = None
        
        # # Buttons: 
        # 0 - TRIGGER_HAND/Hand-Tracking
        # 1 - DOWN
        # 2 - LEFT
        # 3 - CENTER/Z
        # 4 - RIGHT
        # 5 - UP
        # 6 - DEFAULT
        self.listValues_capacitive_sensor = ['4','16','64','2','256','512','0']
        self.buttons = [
                         [int(self.cam_x/4),int(self.cam_y/4),'4',None],
                         [int(self.cam_x/2),self.cam_y-self.coord_y,'16','down'],
                         [self.coord_x,int(self.cam_y/2),'64','left'],
                         [int(self.cam_x/2),int(self.cam_y/2),'2','Z'],
                         [self.cam_x-self.coord_x,int(self.cam_y/2),'256','right'],
                         [int(self.cam_x/2),self.coord_y,'512','up']
                         ]
        
        self.set_cursor_pos_func = ctypes.windll.user32.SetCursorPos
        self.send_input_func = ctypes.windll.user32.SendInput
        self.last_click = time.clock()
        self.current_button_selected = None
        self.show_frame()

    def connect_to_arduino_if_exist(self):
        print("Connection to Arduino")
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
        print("Arduino is connected")
        return ser


    def launchGame(self):
        self.mouseCheckbox.select()
        try: 
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
    
    def press_keys2move(self,data):
        iSelectedButton = self.listValues_capacitive_sensor.index(data)
        # Releasing keys
        if self.current_button_selected is not None and self.current_button_selected != self.buttons[0][2]:
            try:
                print('release key: ' + self.current_button_selected)
                pyautogui.keyUp(self.current_button_selected) # continuous release
            except: 
                print("cannot release key, pleae check if any key is selected")
            
        
        # Pressing keys
        if data != self.listValues_capacitive_sensor[-1] and data != self.buttons[0][2]:
            print('press key: ' + self.buttons[iSelectedButton][3])
            if self.buttons[iSelectedButton][3] == 'Z':
                pyautogui.press(self.buttons[iSelectedButton][3]) # pressing
            else:
                pyautogui.keyDown(self.buttons[iSelectedButton][3]) # continuous pressing
            
        # Changing Controller
        if data == self.buttons[0][2]:
            print("Tentative to change")
            if self.use_cam: 
                self.varMouse.set(False)
                self.use_cam = False
                time.sleep(0.5)
                print("Deactivate Hand Tracking")
                #pyautogui.hotkey('ctrl', 'c')
            elif not self.use_cam:
                self.varMouse.set(True)
                self.use_cam = True
                time.sleep(0.5)
                print("Activate Hand Tracking")
                pyautogui.hotkey('ctrl', 'c')

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

    def control_cursor_mvt(self,mouseLoc):
        if self.varMouse.get():
            self.set_cursor_pos_func(int(mouseLoc[0]),int(mouseLoc[1]))
            if self.t - self.last_click > 0.3:
                # Every 0.3 seconds perform clicks
                last_click = self.t
                # To click I need to fill INPUT structure
                inp = INPUT()
                inp.type = INPUT_MOUSE
                inp.mi.dx = 0
                inp.mi.dy = 0
                inp.mi.mouseData = 0
                inp.mi.time = 0
                inp.mi.dwExtraInfo = None
                # Send mouse down input event
                inp.mi.dwFlags = MOUSEEVENTF_MOVE | MOUSEEVENTF_LEFTDOWN
                res = self.send_input_func(1, ctypes.pointer(inp), sizeof(INPUT))
                if res != 1:
                    ctypes.FormatError(ctypes.GetLastError())
                # Send mouse up input event
                inp.mi.dwFlags = MOUSEEVENTF_MOVE | MOUSEEVENTF_LEFTUP
                res = self.send_input_func(1, ctypes.pointer(inp), sizeof(INPUT))
                if res != 1:
                    ctypes.FormatError(ctypes.GetLastError())
    
    def control_cursor_mvt_one_click(self,mouseLoc):
        if self.varMouse.get():
            self.set_cursor_pos_func(int(mouseLoc[0]),int(mouseLoc[1]))

            # Check if cursor position doesn't change anymore = launch timer
            distance = self.calculate_dist(self.current_button_selected,mouseLoc)
            print(distance)

            if distance is None or distance > self.thresholdDistance:
                self.time_not_changing = self.t
            
            # Perform click if 3second on same position
            if self.t -self.time_not_changing > 3:
                print("Mouse Click")
                # To click I need to fill INPUT structure
                inp = INPUT()
                inp.type = INPUT_MOUSE
                inp.mi.dx = 0
                inp.mi.dy = 0
                inp.mi.mouseData = 0
                inp.mi.time = 0
                inp.mi.dwExtraInfo = None
                # Send mouse down input event
                inp.mi.dwFlags = MOUSEEVENTF_MOVE | MOUSEEVENTF_LEFTDOWN
                res = self.send_input_func(1, ctypes.pointer(inp), sizeof(INPUT))
                if res != 1:
                    ctypes.FormatError(ctypes.GetLastError())
                # Send mouse up input event
                inp.mi.dwFlags = MOUSEEVENTF_MOVE | MOUSEEVENTF_LEFTUP
                res = self.send_input_func(1, ctypes.pointer(inp), sizeof(INPUT))
                if res != 1:
                    ctypes.FormatError(ctypes.GetLastError())
    
    def calculate_dist(self,p1,p2):
        if p1 is not None and p2 is not None:
            return math.sqrt((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2)
        else:
            return None
    
    def show_frame(self):
            # TOUCH DETECTION
            self.t = time.clock()
            if self.ser:
                new_data = self.ser.readline().decode().rstrip()
                if new_data != self.data_:
                    self.buttonJustChanged = True
                    self.data_ = new_data
                    print(self.data_)
                    self.press_keys2move(self.data_)
                else:
                    self.buttonJustChanged = False
            
            if self.ser and not self.use_cam:
                frame = np.zeros((self.cam_y,self.cam_x,3), np.uint8)
                for iButton in range(len(self.buttons)):
                    cv2.circle(frame, (self.buttons[iButton][0],self.buttons[iButton][1]), self.circle_radius, self.circle_color_arrow, self.circle_thickness)
                    if self.data_ is not None and self.data_ == self.buttons[iButton][2]:
                        cv2.circle(frame, (self.buttons[iButton][0],self.buttons[iButton][1]), self.circle_radius, self.circle_color_touch, self.circle_thickness)
                        self.current_button_selected = self.buttons[iButton][3] 
                         
            # CAMERA HAND TRACKING
            elif self.use_cam:
                ret, self.img = self.cam.read()
                # flipping for the selfie cam right now to keep same
                self.img = cv2.flip(self.img, 1)
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
                # Drawing 
                cv2.drawContours(frame, conts, -1, (255, 0, 0), 3)
                if conts:
                    x, y, w, h = cv2.boundingRect(conts[0])
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
                    x1, y1, w1, h1 = cv2.boundingRect(conts[0])
                    center_x = int(x1 + w1 / 2)
                    center_y = int(y1 + h1 / 2)
                    cv2.circle(frame, (center_x, center_y), 2, (0, 0, 255), 2)
                    mouseLoc = ( (center_x * self.screen_x / self.cam_x), center_y * self.screen_y / self.cam_y)
                if self.varMouse.get() and conts:
                    self.control_cursor_mvt(mouseLoc)
                    self.current_button_selected = mouseLoc

            # OUTPUT VISUALIZATION
            imgPIL = PIL.Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=imgPIL)
            self.lmain.imgtk = imgtk
            self.lmain.configure(image=imgtk)
            self.lmain.after(self.refresh_rate,self.show_frame)


if __name__ == "__main__":

    config_file = r".\config.ini"
    camInt = CameraInterface(config_file)
    camInt.root.mainloop()
    # Ensure when closing that all keys are release!
    for i,key_ in enumerate(['left','right','up','down']):
        print(i,key_)
        pyautogui.keyUp(key_)

