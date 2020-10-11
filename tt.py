
# -*- coding: ASCII -*-
"""
Created on Sun Oct 11 02:17:02 2020

@author: donaca
"""

import serial
import keyboard
from pynput.keyboard import Key,KeyCode, Controller

keyboard = Controller()

ard = serial.Serial(port ="COM4", baudrate ="9600");

while(True):
    data = ard.readline()
    #data = data.split(" ")
    
    c = data[0]
    if c == 52:
      print(c)
      keyboard.press(Key.up)
      
      
    
