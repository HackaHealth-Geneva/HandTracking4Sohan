
import time
import serial
from pynput.keyboard import Key,KeyCode, Controller

c = 0
keyboard = Controller()

ard = serial.Serial(port ="COM4", baudrate ="9600");


while(True):

        data = ard.readline()
        c = data[0]
        print(c)
        
        if c == 50:
            keyboard.press(Key.up)
        if c== 52: 
            keyboard.press(Key.right)
        if c==56:
            keyboard.press(Key.down)
        if c==49:
            keyboard.press(Key.left)
        if c==54:
            keyboard.press(Key.enter)
        if c==57:
             break; #leave  KeyboardController
        


      
      
    
