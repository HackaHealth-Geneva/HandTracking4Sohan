''' 
Project HandTracking4Sohan - developped during HackaHealth Hackathon 2020 
12/05/2020 Lausanne,Switzerland
Camera_Interface 
Contact: hackahealth.geneva@gmail.com, bastien.orset@epfl.ch
Autors: Bastien Orset (inlcudes your name if you contributed)
'''

import os
import time
import PIL
import cv2
import numpy as np
import threading
import queue
from queue import Empty
import configparser

import ast
import warnings
import serial
import serial.tools.list_ports

import win32gui,win32con,win32api
import ctypes
import math
import time

from ctypes import c_long, POINTER, sizeof, c_int
from ctypes.wintypes import DWORD

from PIL import Image,ImageTk
from tkinter import *
from tkinter import font
import pyautogui

import mediapipe as mp

'''
TO DO



'''

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

LIST_INDEX_TIP = [4,8,12,16,20]

class CameraInterface(Tk):
    def __init__(self,config_file, arduino_queue):
        # READ CONFIG FILE
        self.config_file = config_file
        self.config = configparser.ConfigParser()
        self.config.read(self.config_file)
        
        self.lowerBound = np.array([29, 86, 6])
        self.upperBound = np.array([64, 255, 255])

        self.root = Tk()
        self.root.geometry('500x660+10+10')
        self.root.bind('<Escape>', lambda e: self.root.quit())
        self.root.title('HandTracking4Sohan')
        self.root.resizable(1,1)
        self.root.configure(background="Sky Blue")
        self.root.wm_attributes("-topmost", 1)
        
        # Change Icon top left 
        path_icon = os.path.join(r'.\Icon','HackaHealth_Logo_tkinter.ico')
        self.root.wm_iconbitmap(path_icon)

        # Config file
        # Window params
        self.cam_x = self.config.getint("window","camx")
        self.cam_y = self.config.getint("window","camy")
        self.refresh_rate = self.config.getint("window","refresh_rate")
        self.close_cmd = self.config.getboolean("window","close_cmd")
        
        # Tracking params
        self.use_cam = self.config.getboolean("tracking_params","use_cam")
        kernel_o = self.config.getint("tracking_params","kernel_o")
        kernel_c = self.config.getint("tracking_params","kernel_c")
        
        # Camera
        self.cam_id = self.config.getint("camera","cam_id")
        cam_flip_x = self.config.getboolean("camera","cam_flip_x")
        cam_flip_y = self.config.getboolean("camera","cam_flip_y")

        # Mouse Controller options
        ctrl_flip_x = self.config.getboolean("mouseController","ctrl_flip_x")
        ctrl_flip_y = self.config.getboolean("mouseController","ctrl_flip_y")

        # Tracking Methods
        tracking_Color = self.config.getboolean("tracking_method","tracking_Color")
        tracking_DL = self.config.getboolean("tracking_method","tracking_DL")
        self.index_joints_2use_DL = self.config.getint("tracking_method","index_joints_2use_DL")

        # Initializations of kernel and cam
        self.kernelOpen = np.ones((kernel_o, kernel_o))
        self.kernelClose = np.ones((kernel_c, kernel_c))
        self.cam = cv2.VideoCapture(self.cam_id)
        
        # Path for game and grid interface
        self.path_game = ast.literal_eval(self.config.get("app", "path_game")) 
        self.path_grid3 = ast.literal_eval(self.config.get("app", "path_grid3")) 

        # Initialize variable for interface
        self.varMouse = IntVar()
        self.varKeys = IntVar()
        self.thresholdDistance = 15
        self.mouseLoc = (None,None)
        
        #Arduino Params
        self.ser  = self.connect_to_arduino_if_exist()
        self.data_ = None #None
        
        if self.ser:
            self.varMouse.set(False)
            self.varKeys.set(True)
            self.use_cam = False
            stateButtonKeys = 'normal'
        else:
            self.varKeys.set(False)
            self.use_cam = True
            stateButtonKeys = 'disabled'
        
        # Menu
        self.cam_do_flip_X = BooleanVar()
        self.cam_do_flip_X.set(cam_flip_x)
        self.cam_do_flip_Y = BooleanVar()
        self.cam_do_flip_Y.set(cam_flip_y)
        
        self.ctrl_do_flip_X = BooleanVar()
        self.ctrl_do_flip_X.set(ctrl_flip_x)
        self.ctrl_do_flip_Y = BooleanVar()
        self.ctrl_do_flip_Y.set(ctrl_flip_y)
        
        
        self.tracking_DL = BooleanVar()
        self.tracking_DL.set(tracking_DL)
        self.tracking_Color = BooleanVar()
        self.tracking_Color.set(tracking_Color)
        
        menubar = Menu(self.root)
        view_menu = Menu(menubar)
        view_menu.add_checkbutton(label="Flip X", onvalue=1, offvalue=0, variable=self.cam_do_flip_X)
        view_menu.add_checkbutton(label="Flip Y", onvalue=1, offvalue=0, variable=self.cam_do_flip_Y)
        
        ctrl_menu = Menu(menubar)
        ctrl_menu.add_checkbutton(label="Flip X", onvalue=1, offvalue=0, variable=self.tracking_DL)
        ctrl_menu.add_checkbutton(label="Flip Y", onvalue=1, offvalue=0, variable= not self.tracking_DL)
        
        tracking_menu = Menu(menubar)
        tracking_menu.add_checkbutton(label="Tracking DL", onvalue=1, offvalue=0, command=self.select_tracking_method1,variable=self.tracking_DL)
        tracking_menu.add_checkbutton(label="Tracking Color", onvalue=1, offvalue=0,command=self.select_tracking_method2,variable=self.tracking_Color)
        
        menubar.add_cascade(label='Camera', menu=view_menu)
        menubar.add_cascade(label='Mouse', menu=ctrl_menu)
        menubar.add_cascade(label='Tracking', menu=tracking_menu)
        self.root.config(menu=menubar)
        
        # Interface 
        self.lmain = Label(self.root)
        self.camera_pic = PhotoImage(file=".\Picture_Button\camera_pic.png")
        self.sensor_pic = PhotoImage(file=".\Picture_Button\sensor_pic.png")
        self.LabelController = Label(self.root, text="Controller",font=("Helvetica", 13,'bold'),justify=CENTER,bg='Sky Blue')
        f = font.Font(self.LabelController, self.LabelController.cget("font"))
        f.configure(underline = True)
        self.LabelController.configure(font=f)

        self.mouseCheckbox = Checkbutton(self.root, text=" Mouse", variable=self.varMouse,font=("Helvetica", 11), 
        	command=self.mouseMovement,background="Sky Blue",state='normal',image =self.camera_pic, compound='left')

        self.KeysCheckbox = Checkbutton(self.root, text="Sensor", variable=self.varKeys,font=("Helvetica", 11), 
        	command=self.keyMovement,background="Sky Blue",image =self.sensor_pic, compound='left',state=stateButtonKeys)

        self.LabelApp= Label(self.root, text="Applications",font=("Helvetica", 13,'bold'),justify=CENTER,bg='Sky Blue')
        f = font.Font(self.LabelApp, self.LabelApp.cget("font"))
        f.configure(underline = True)
        self.LabelApp.configure(font=f)

        self.loadimage1 = PhotoImage(file=".\Picture_Button\jouer.png")
        self.gameButton = Button(self.root, image=self.loadimage1,command=self.launchGame,background="Sky Blue")  # REMEMBER TO CHANGE
        self.gameButton["border"] = "0"

        self.lmain.grid(row=0, column=0, columnspan=4,padx=50,pady=20)
        self.LabelController.grid(row=1, column=0, columnspan=4,sticky='nesw',pady=10)
        self.KeysCheckbox.grid(row=2, column=0,columnspan=2,  sticky='nesw')
        self.mouseCheckbox.grid(row=2, column=2,columnspan=2,  sticky='nesw')
        self.LabelApp.grid(row=3, column=0, columnspan=4,sticky='nesw',pady=10)
        self.gameButton.grid(row=4,column=0,columnspan=4,sticky='nesw',padx=10,pady=20)

        # Screen size
        self.screen_x = self.root.winfo_screenwidth()
        self.screen_y = self.root.winfo_screenheight()

        # Initilization params
        self.justChanged = True
        self.gridIsOpen = False

        # Capacitive sensor - visualization
        self.coord_x = 120
        self.coord_y = 60
        self.circle_radius = 15
        self.circle_color_arrow = (255, 0, 0)
        self.circle_color_switch = (255, 0, 255)
        self.circle_color_touch = (0, 255, 0)
        self.circle_thickness = -5
        self.time_not_changing = None
        self.thickness_arrow = 9
        self.tipLength = 0.5
        self.val = 25


        # Capacitive Buttons: 
        # self.listValues_capacitive_sensor = ['4','1024','16','64','2','256','512','0']
        self.listValues_capacitive_sensor = ['4','16','64','2','256','512','0']
        
        self.buttons = [
                         [int(self.cam_x/5),int(self.cam_y/5),'4',None], # 0 - TRIGGER_HAND/Hand-Tracking
                         # [self.cam_x-int(self.cam_x/3),int(self.cam_y/4),'1024',None], # 0 - TRIGGER_HAND/Hand-Tracking
                         [int(self.cam_x/2),self.cam_y-self.coord_y,'16','down'],        # 1 - DOWN
                         [self.coord_x,int(self.cam_y/2),'64','left'],        # 2 - LEFT
                         [int(self.cam_x/2),int(self.cam_y/2),'2','Z'],        # 3 - CENTER/Z
                         [self.cam_x-self.coord_x,int(self.cam_y/2),'256','right'], # 4 - RIGHT
                         [int(self.cam_x/2),self.coord_y,'512','up']# 5 - UP
                         ]
                         # 6 - DEFAULT
        self.current_button_selected = None


        # Initialization for Mouse Controller
        self.set_cursor_pos_func = ctypes.windll.user32.SetCursorPos
        self.send_input_func = ctypes.windll.user32.SendInput
        self.last_click = time.clock()
        
        # Threading
        self.arduino_queue = arduino_queue
        
        # Hands Pose estimation parameters
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_hands = mp.solutions.hands
        self.hands_model = self.mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.5)
        self.hand_landmarks = None

        self.show_frame()

    def select_tracking_method1(self):
        if self.tracking_DL.get():
            self.tracking_Color.set(False)
        else:
            self.tracking_Color.set(True)
    
    def select_tracking_method2(self):
        if self.tracking_Color.get():
            self.tracking_DL.set(False)
        else:
            self.tracking_DL.set(True)


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
            print("Arduino is connected")
        except:
            print("Arduino is not connected")
            ser = []
        return ser

    def enum_callback(self,hwnd, results):
        winlist.append((hwnd, win32gui.GetWindowText(hwnd)))
    
    def launchGame(self):
        self.mouseCheckbox.select()
        try: 
            os.startfile(self.path_game)
        except Exception as e:
                print(e)
                print('Cannot launch game')
        
    def press_keys2move(self,data):
        iSelectedButton = self.listValues_capacitive_sensor.index(data)
        # Releasing keys
        if self.current_button_selected is not None and self.current_button_selected != self.buttons[0][2]:
            if self.current_button_selected != 'Z':
                    print('release key: ' + self.current_button_selected)
                    # print(iSelectedButton)
                    pyautogui.keyUp(self.current_button_selected) # continuous release


        # Pressing keys
        if data != self.listValues_capacitive_sensor[-1] and data != self.buttons[0][2] and data != self.buttons[1][2]:
            print('press key: ' + self.buttons[iSelectedButton][3])
            if self.buttons[iSelectedButton][3] == 'Z':
                pyautogui.press(self.buttons[iSelectedButton][3]) # pressing
                time.sleep(0.5)
            else:
                pyautogui.keyDown(self.buttons[iSelectedButton][3]) # continuous pressing
                
        # Changing Controller
        if data == self.buttons[0][2]:
            print("Tentative to change")
            if self.use_cam: 
                self.varMouse.set(False)
                self.use_cam = False
                self.varKeys.set(True)
                time.sleep(0.5)
                print("Deactivate Hand Tracking")
            elif not self.use_cam:
                self.varMouse.set(True)
                self.use_cam = True
                self.varKeys.set(False)
                time.sleep(0.5)
                print("Activate Hand Tracking")

    def mouseMovement(self):
        if self.varMouse.get():
            print("Mouse Controller ON")
            self.use_cam = True
            self.varKeys.set(False)

        else:
            print("Mouse Controller OFF")
            if self.ser:
                self.varKeys.set(True)
                self.use_cam = False

    def keyMovement(self):
        if self.varKeys.get():
            print("Keys Controller ON")
            self.use_cam = False
            self.varMouse.set(False)
        else:
            print("Mouse Controller OFF")
            self.use_cam = True

            
    def selected(self):
        if self.varMouse.get():
            self.mouseCheckbox.deselect()
        else:
            self.mouseCheckbox.select()
        if self.varKeys.get():
            self.KeysCheckbox.deselect()
        else:
            self.KeysCheckbox.select()


    def control_cursor_mvt(self,mouseLoc,isInGrid3Boolean):
        self.set_cursor_pos_func(int(mouseLoc[0]),int(mouseLoc[1]))
        if self.t - self.last_click > 0.3:
            # Every 0.3 seconds perform clicks
            if isInGrid3Boolean:
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
            last_click = self.t
    
    def control_cursor_mvt_one_click(self,mouseLoc):
        self.set_cursor_pos_func(int(mouseLoc[0]),int(mouseLoc[1]))
        # Check if cursor position doesn't change anymore = launch timer
        distance = self.calculate_dist(self.current_mouse_location,mouseLoc)
        print(distance)

        if distance is None or distance > self.thresholdDistance:
            self.time_not_changing = self.t
        
        # Perform click if 3second on same position
        if self.t -self.time_not_changing > 3:
            print("Mouse Click")
            self.time_not_changing = self.t
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
    
    def show_frame(self):
            # TOUCH DETECTION
            self.t = time.clock()
            # self.root.wm_attributes("-topmost", 1)
            if self.ser:
                try:
                    new_data = self.arduino_queue.get_nowait()
                    if new_data != self.data_:
                        self.buttonJustChanged = True
                        self.data_ = new_data
                        print(self.data_)
                        try:
                            self.press_keys2move(self.data_)
                        except Exception as e:
                            print(e)
                            print('cannot press this key')
                    else:
                        self.buttonJustChanged = False
                except Empty:
                    pass

            if self.ser and not self.use_cam:
                frame = np.zeros((self.cam_y,self.cam_x,3), np.uint8)
                for iButton in range(len(self.buttons)):
                    if self.buttons[iButton][3] is not None and self.buttons[iButton][3] != 'Z':
                        if self.buttons[iButton][3] == 'left':
                            start_point = (self.buttons[iButton][0]+self.val, self.buttons[iButton][1]) 
                            end_point = (self.buttons[iButton][0]-self.val, self.buttons[iButton][1])
                        elif self.buttons[iButton][3] == 'right':
                            start_point = (self.buttons[iButton][0]-self.val, self.buttons[iButton][1]) 
                            end_point = (self.buttons[iButton][0]+self.val, self.buttons[iButton][1])
                        elif self.buttons[iButton][3] == 'down':
                            start_point = (self.buttons[iButton][0], self.buttons[iButton][1]-self.val) 
                            end_point = (self.buttons[iButton][0], self.buttons[iButton][1]+self.val)
                        elif self.buttons[iButton][3] == 'up':
                            start_point = (self.buttons[iButton][0], self.buttons[iButton][1]+self.val) 
                            end_point = (self.buttons[iButton][0], self.buttons[iButton][1]-self.val)
                        
                        if self.data_ is not None and self.data_ == self.buttons[iButton][2]:
                            cv2.arrowedLine(frame ,start_point, end_point, self.circle_color_touch, self.thickness_arrow,tipLength = self.tipLength)
                            self.current_button_selected = self.buttons[iButton][3] 
                        else:
                            cv2.arrowedLine(frame, start_point, end_point, self.circle_color_arrow, self.thickness_arrow,tipLength = self.tipLength)
                    else:
                        cv2.circle(frame, (self.buttons[iButton][0],self.buttons[iButton][1]), self.circle_radius, self.circle_color_arrow, self.circle_thickness)
                        if self.data_ is not None and self.data_ == self.buttons[iButton][2]:
                            cv2.circle(frame, (self.buttons[iButton][0],self.buttons[iButton][1]), self.circle_radius, self.circle_color_touch, self.circle_thickness)
                            self.current_button_selected = self.buttons[iButton][3] 
                         
            # CAMERA HAND TRACKING
            elif self.use_cam:
                conts = None
                # Check if mouse is in Grid3 = if yes allow click otherwise no
                win32gui.EnumWindows(self.enum_callback, toplist)
                grid3 = [(hwnd, title) for hwnd, title in winlist if title.startswith('Grid 3')]

                if grid3 and self.mouseLoc[0] is not None: 
                    print(grid3)
                    grid3 = grid3[0]
                    (left, top, right, bottom) = win32gui.GetWindowRect(grid3[0])
                    isInGrid3Boolean = (left<self.mouseLoc[0]<right and top<self.mouseLoc[1]<bottom)
                else:
                    isInGrid3Boolean = False

                # Image Processing
                ret, self.img = self.cam.read()
                # flipping for the selfie cam right now to keep same
                
                if self.cam_do_flip_X.get():
                   self.img = cv2.flip(self.img, 1)
                if self.cam_do_flip_Y.get():
                    self.img = cv2.flip(self.img, 0)

                self.img = cv2.resize(self.img, (self.cam_x, self.cam_y))
                if self.tracking_Color.get():
                    # convert BGR to HSV
                    frame = cv2.cvtColor(self.img, cv2.COLOR_RGB2BGR)
                    imgHSV = cv2.cvtColor(self.img, cv2.COLOR_BGR2HSV)
                    # create the Mask + morphology
                    mask = cv2.inRange(imgHSV, self.lowerBound, self.upperBound)
                    maskOpen = cv2.morphologyEx(mask, cv2.MORPH_OPEN, self.kernelOpen)
                    maskClose = cv2.morphologyEx(maskOpen, cv2.MORPH_CLOSE, self.kernelClose)
                    maskFinal = maskClose
                    im2, conts, hierarchy = cv2.findContours( maskFinal.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
                    # Drawing 
                    cv2.drawContours(frame, conts, -1, (255, 0, 0), 3)
                    if conts:
                        x, y, w, h = cv2.boundingRect(conts[0])
                        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
                        x1, y1, w1, h1 = cv2.boundingRect(conts[0])
                        center_x = int(x1 + w1 / 2)
                        center_y = int(y1 + h1 / 2)
                        cv2.circle(frame, (center_x, center_y), 2, (0, 0, 255), 2)
                
                if self.tracking_DL.get():
                    self.img.flags.writeable = False
                    results = self.hands_model.process(self.img)
                    # Draw the hand annotations on the image.
                    self.img.flags.writeable = True
                    frame = cv2.cvtColor(self.img, cv2.COLOR_RGB2BGR)
                    if results.multi_hand_landmarks:
                      for hand_landmarks in results.multi_hand_landmarks:
                        self.mp_drawing.draw_landmarks(
                            frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
                        image_rows, image_cols, _ = frame.shape
                        idx_to_coordinates = {}
                        for idx, landmark in enumerate(hand_landmarks.landmark):
                          if landmark.visibility < 0 or landmark.presence < 0:
                            continue
                          conts = self.mp_drawing._normalized_to_pixel_coordinates(landmark.x, landmark.y,
                                                                         image_cols, image_rows)
                          if idx == self.index_joints_2use_DL and conts:
                            cv2.circle(frame, conts, 10,(0,200,0), -1)
                            center_x,center_y = conts

                if self.varMouse.get() and conts:
                    if self.ctrl_do_flip_X.get():
                        center_x = self.cam_x - center_x
                    if self.ctrl_do_flip_Y.get():
                        center_y = self.cam_y - center_y
                        # Translate position into mouse
                        self.mouseLoc = ( (center_x * self.screen_x / self.cam_x), center_y * self.screen_y / self.cam_y)

                    self.control_cursor_mvt(self.mouseLoc,isInGrid3Boolean)
                    self.current_mouse_location = self.mouseLoc

            # OUTPUT VISUALIZATION
            imgPIL = PIL.Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=imgPIL)
            self.lmain.imgtk = imgtk
            self.lmain.configure(image=imgtk)
            self.lmain.after(self.refresh_rate,self.show_frame)

def get_arduino_data(ard_queue, ser):
    time.sleep(0.1)
    while ser:
        new_data = ser.readline().decode().rstrip()
        ard_queue.put(new_data)
        

if __name__ == "__main__":

    toplist = []
    winlist = []
    config_file = r".\config.ini"

    arduino_queue = queue.Queue()
    camInt = CameraInterface(config_file, arduino_queue)
    arduino_thread = threading.Thread(target=get_arduino_data, args=(arduino_queue, camInt.ser ), daemon=True, name="arduino_thread").start()
    camInt.root.mainloop()

    # Ensure when closing that all keys are release!
    for i,key_ in enumerate(['left','right','up','down']):
        print(i,key_)
        pyautogui.keyUp(key_)
        
        
