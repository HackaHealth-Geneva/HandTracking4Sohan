#import mouse
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

import win32gui
import ctypes
import math
import time

from ctypes import c_long, POINTER, sizeof, c_int
from ctypes.wintypes import DWORD

from PIL import Image,ImageTk
from tkinter import *
from tkinter import font
import pyautogui

import subprocess
import pyttsx3
from gtts import gTTS

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

# LIST CMD 
OPTIONS = {'Je ne veux plus communiquer','Je veux communiquer'}


class CameraInterface(Tk):
    def __init__(self,config_file, arduino_queue):
        # READ CONFIG FILE
        self.config_file = config_file
        self.config = configparser.ConfigParser()
        self.config.read(self.config_file)
        
        self.lowerBound = np.array([29, 86, 6])
        self.upperBound = np.array([64, 255, 255])

        self.root = Tk()
        self.root.geometry('500x650+10+10')
        self.root.bind('<Escape>', lambda e: self.root.quit())
        self.root.title('HandTracking4Sohan')
        self.root.resizable(1,1)
        self.root.configure(background="Sky Blue")

        # Change Icon top left 
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
        
        # Interface 
        self.lmain = Label(self.root)
        # self.red = Button(self.root, text="red", command=self.detectRed,font=("Helvetica", 11,'bold'),state='disabled',bg='gray72')
        # self.green = Button(self.root, text="green", command=self.detectGreen,font=("Helvetica", 11,'bold'),state='disabled',bg='gray72')
        # self.blue = Button(self.root, text="blue", command=self.detectBlue,font=("Helvetica", 11,'bold'),state='disabled',bg='gray72')
        self.camera_pic = PhotoImage(file=".\Picture_Button\camera_pic.png")
        self.sensor_pic = PhotoImage(file=".\Picture_Button\sensor_pic.png")
        self.LabelController = Label(self.root, text="Controller",font=("Helvetica", 13,'bold'),justify=CENTER,bg='Sky Blue')
        f = font.Font(self.LabelController, self.LabelController.cget("font"))
        f.configure(underline = True)
        self.LabelController.configure(font=f)
        self.mouseCheckbox = Checkbutton(self.root, text=" Mouse", variable=self.varMouse,font=("Helvetica", 11), 
        	command=self.mouseMovement,background="Sky Blue",state='normal',image =self.camera_pic, compound='left')
        self.KeysCheckbox = Checkbutton(self.root, text="Sensor", variable=self.varKeys,font=("Helvetica", 11), 
        	command=self.keyMovement,background="Sky Blue",image =self.sensor_pic, compound='left',state='disabled')
        self.LabelApp= Label(self.root, text="Applications",font=("Helvetica", 13,'bold'),justify=CENTER,bg='Sky Blue')
        f = font.Font(self.LabelApp, self.LabelApp.cget("font"))
        f.configure(underline = True)
        self.LabelApp.configure(font=f)

        self.loadimage1 = PhotoImage(file=".\Picture_Button\jouer.png")
        self.gameButton = Button(self.root, image=self.loadimage1,command=self.launch_grid,background="Sky Blue")  # REMEMBER TO CHANGE
        self.gameButton["border"] = "0"

        self.loadimage2 = PhotoImage(file=".\Picture_Button\parler_start.png")
        self.grid3Button = Button(self.root, image=self.loadimage2,command=self.launch_grid,background="Sky Blue")  # REMEMBER TO CHANGE
        self.grid3Button["border"] = "0"

        self.lmain.grid(row=0, column=0, columnspan=4,padx=50,pady=20)
        # self.red.grid(row=1, column=0, sticky='nesw',padx=10,pady=1)
        # self.green.grid(row=2, column=0, sticky='nesw',padx=10,pady=1)
        # self.blue.grid(row=3, column=0, sticky='nesw',padx=10,pady=1)
        self.LabelController.grid(row=1, column=0, columnspan=4,sticky='nesw',pady=10)
        self.KeysCheckbox.grid(row=2, column=0,columnspan=2,  sticky='nesw')
        self.mouseCheckbox.grid(row=2, column=2,columnspan=2,  sticky='nesw')
        self.LabelApp.grid(row=3, column=0, columnspan=4,sticky='nesw',pady=10)
        self.gameButton.grid(row=4,column=0,columnspan=2,sticky='nesw',padx=10,pady=20)
        self.grid3Button.grid(row=4,column=2,columnspan=2,sticky='nesw',pady=20)
        
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


        # # Capacitive Buttons: 
        self.listValues_capacitive_sensor = ['4','1024','16','64','2','256','512','0']
        self.buttons = [
                         [int(self.cam_x/3),int(self.cam_y/4),'4',None], # 0 - TRIGGER_HAND/Hand-Tracking
                         [self.cam_x-int(self.cam_x/3),int(self.cam_y/4),'1024',None], # 0 - TRIGGER_HAND/Hand-Tracking
                         [int(self.cam_x/2),self.cam_y-self.coord_y,'16','down'],        # 1 - DOWN
                         [self.coord_x,int(self.cam_y/2),'64','left'],        # 2 - LEFT
                         [int(self.cam_x/2),int(self.cam_y/2),'2','Z'],        # 3 - CENTER/Z
                         [self.cam_x-self.coord_x,int(self.cam_y/2),'256','right'], # 4 - RIGHT
                         [int(self.cam_x/2),self.coord_y,'512','up']# 5 - UP
                         ]
                         # 6 - DEFAULT
        self.current_button_selected = None

        # SOUND FEEDBACK
        self.engine=pyttsx3.init('sapi5')
        voices=self.engine.getProperty('voices')
        self.engine.setProperty('voice','voices[0].id')

        # mixer.init()
        # self.sound_path = r'.\Sound'
        # if not os.path.exists(self.sound_path):
        #     self.loading_sound_on_computer(OPTIONS)
        
        
        # Initialization for Mouse Controller
        self.set_cursor_pos_func = ctypes.windll.user32.SetCursorPos
        self.send_input_func = ctypes.windll.user32.SendInput
        self.last_click = time.clock()


        # threading
        self.arduino_queue = arduino_queue

        self.show_frame()


    def speak(self,text):
        self.engine.say(text)
        time.sleep(0.5)
        print('say something')

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

    def launch_grid(self):
        try: 
            #os.startfile(self.path_grid3)
            self.shell_process = subprocess.Popen([self.path_grid3],shell=True) 
        except Exception as e:
            print(e)
            print('Cannot launch Grid3')
    def close_grid(self):
        try: 
            win32gui.EnumWindows(self.enum_callback, toplist)
            grid3 = [(hwnd, title) for hwnd, title in winlist if title.startswith('Grid 3')]
            print(grid3)
            subprocess.call(["taskkill","/F","/IM",grid3[0][1]])
        except Exception as e:
            print(e)
            print('Cannot close Grid3')
        
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
            if self.current_button_selected != 'Z':
                    print('release key: ' + self.current_button_selected)
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
                #pyautogui.hotkey('ctrl', 'c')
            elif not self.use_cam:
                self.varMouse.set(True)
                self.use_cam = True
                self.varKeys.set(False)
                time.sleep(0.5)
                print("Activate Hand Tracking")
                #pyautogui.hotkey('ctrl', 'c')

        # Launch Interface
        if data == self.buttons[1][2]:
            if not self.gridIsOpen:
                self.speak("Je veux communiquer")
                self.launch_grid()
                self.gridIsOpen = True
                # mixer.music.load(os.path.join(self.sound_path,'Je veux communiquer.mp3'))
                # mixer.music.play()
                print("Tentative to open Grid")
            else:
                self.speak("Je ne veux plus communiquer")
                self.close_grid()
                # mixer.music.load(os.path.join(self.sound_path,'Je ne veux plus communiquer.mp3'))
                # mixer.music.play()
                
                self.gridIsOpen = False
                print("Tentative to close Grid")
    
    def loading_sound_on_computer(self,OPTIONS):
        engine = pyttsx3.init(driverName='sapi5')
        print("*** Creating Sound folder ****")
        folderData = ".\Sound"
        if not os.path.exists(folderData):
            os.makedirs(folderData)
        for i,opt in enumerate(OPTIONS):
            print(opt)
            theText = opt
            tts = gTTS(text=theText, lang='en')
            tts.save(os.path.join(folderData,theText + ".mp3"))
        print("File saved!")
    
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
                print('Click')
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
    
    def calculate_dist(self,p1,p2):
        if p1 is not None and p2 is not None:
            return math.sqrt((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2)
        else:
            return None

    def show_frame(self):
            # TOUCH DETECTION
            self.t = time.clock()
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
                    # frame = self.create_triangle(frame,iButton)

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
                # Check if mouse is in Grid3 = if yes allow click otherwise no
                win32gui.EnumWindows(self.enum_callback, toplist)
                grid3 = [(hwnd, title) for hwnd, title in winlist if title.startswith('Grid 3')]
                if grid3 and self.mouseLoc[0] is not None: 
                    grid3 = grid3[0]
                    (left, top, right, bottom) = win32gui.GetWindowRect(grid3[0])
                    isInGrid3Boolean = (left<self.mouseLoc[0]<right and top<self.mouseLoc[1]<bottom)
                else:
                    isInGrid3Boolean = False
                #print(isInGrid3Boolean)

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
                    self.mouseLoc = ( (center_x * self.screen_x / self.cam_x), center_y * self.screen_y / self.cam_y)
                if self.varMouse.get() and conts:
                    self.control_cursor_mvt(self.mouseLoc,isInGrid3Boolean)
                    self.current_mouse_location = self.mouseLoc

            # OUTPUT VISUALIZATION
            imgPIL = PIL.Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=imgPIL)
            self.lmain.imgtk = imgtk
            self.lmain.configure(image=imgtk)
            self.lmain.after(self.refresh_rate,self.show_frame)


def get_arduino_data(ard_queue, ser):
    while ser:
        new_data = ser.readline().decode().rstrip()
        ard_queue.put(new_data)
        time.sleep(0.5)

if __name__ == "__main__":

    toplist = []
    winlist = []
    #width, height= pyautogui.size()
    #win32gui.MoveWindow(grid3[0], 0, 0, width,height, False)
    config_file = r".\config.ini"

    arduino_queue = queue.Queue()
    camInt = CameraInterface(config_file, arduino_queue)
    arduino_thread = threading.Thread(target=get_arduino_data, args=(arduino_queue, camInt.ser ), daemon=True, name="arduino_thread").start()
    camInt.root.mainloop()
    # mixer.quit()
    # Ensure when closing that all keys are release!
    for i,key_ in enumerate(['left','right','up','down']):
        print(i,key_)
        pyautogui.keyUp(key_)
        
        
