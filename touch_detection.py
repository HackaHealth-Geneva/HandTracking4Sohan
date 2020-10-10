import time

import board
import busio
import adafruit_mpr121
from pynput.keyboard import Key, KeyCode, Controller

keyboard= Controller()
i2c=busio.I2C(board.SCL, board.SDA)
mpr121= adafruit_mpr121.MPR121(i2c)
start = 0 
end = 0
elapsed_time=0
first_start = 0
print_once = 1; 
start_direction=0
switched_on=False
# 0 is ok/enter, 1 up 2 right 3 down 4 left
active0=False
active1=False
active2=False
active3=False
active4=False

def activate_button(case):
    start_direction=0
    if mpr121[case].value:
     start_direction = time.monotonic()
     end_direction=0
     #print(case)


def disactivate_button(case):	  
    if mpr121[case].value==False:
     end_direction =time.monotonic()

       
while True:
#for the ok button

   # for button0
    if mpr121[0].value: 
      activate_button(0)
      if active0==False:
       start_time=time.monotonic()
      #if holdfor 3 seconds, presses enter
      if time.monotonic()-start_time>3:
       keyboard.press(Key.enter)
      active0=True
    if mpr121[0].value==False and active0==True:
       disactivate_button(0)
       keyboard.release(Key.enter)
       active0=False
       
    
    # for button1 (1 up 2 right 3 down 4 left)
    if mpr121[1].value: 
      activate_button(1)
      active1=True
      keyboard.press(Key.up)
    if mpr121[1].value==False and active1==True:
       disactivate_button(1)
       active1=False
       keyboard.release(Key.up)
   
    
    # for button2
    if mpr121[2].value: 
      activate_button(2)
      active2=True
      keyboard.press(Key.right)
    if mpr121[2].value==False and active2==True:
       disactivate_button(2)
       active2=False
       keyboard.release(Key.right)
      
    # for button3
    if mpr121[3].value: 
      activate_button(3)
      active3=True
      keyboard.press(Key.down)
    if mpr121[3].value==False and active3==True:
       disactivate_button(3)
       active3=False
       keyboard.release(Key.down)
       
    # for button4
    if mpr121[4].value: 
      activate_button(4)
      active4=True
      keyboard.press(Key.left)
    if mpr121[4].value==False and active4==True:
       disactivate_button(4)
       active4=False
       keyboard.release(Key.left)
