# HandTracking4Sohan <img src="index.png" align="right" alt="drawing" width="250"/>

## Challenges 

Sohan is 8 years old and even if he can't speak, he likes to communicate with the people around him by using pictograms and an eye-tracker detecting his gaze to select words on his computer and speak with people. 

To communicate, these technological devices require a high motor effort such as pressing on some button or concentrating his gaze on the computer screen for a long period of time. As a result, Sohan's ability to communicate with us is largely impaired. In this project, the goal was to design a controller that would allow him to communicate through his interface while requiring less physical effort from him. 

Sohan has cognitive impairments that do not allow him to control of his movements in general. Moreover he doesn't have the muscular strength to use a joystick or even to press keys on a keyboards or some buttons. He can only slide his left hand on the table and he has little control over his right hand. His head, very often, falls down on the left side of the body when he's tired. This makes very difficult to use eye-tracking device to detect the gaze to lead the computer interface. 

As the best way he has to communicate is through pictograms he points with the thumb on his left hand. So this is the best sensory input we can get from Sohan and we can use this as one of the inputs, so using simple computer vision techniques we can detect a color cue placed on his thumbs with a webcam and use the posiiton of the color cue to control a pointer on Sohan's computer. Also as a complement ot the mouse control we developped capacitive sensors to act as simple touch buttons to control the directional pad of the computer and navigate more easily on his interface and also activate the hand-tracking on a computer using the camera. 

 ## Files 
 - ```requirements.txt``` : Necessary libraries to run the project. 
 
  
 #### Webcam camera hand detection and pointer control
- ```CameraInterface.py``` : Creates an command interface to select red, blue and green shapes seen by the webcam. Also creates two checkboxes ```Mouse``` to allow pointer control with the webcam and ```Clic``` to allow the user to use the webcam with two green markers on the fingers and actually clic on the computer by pulling the two fingers closer together. 

<p align="center"><img src="Media/OpenCV.png" alt="drawing" width="600"/><p>
On the different windows we can see the masks generated as pixels labelled with 1. One is the opened version of the shape, another one is the closed shape and the difference of the two gives the contour of the original shape. 

 ## Launch
 
 ##### Webcam camera hand detection and pointer control
- Launch the grid software and ```CameraInterface.py```
- Focus on Python/Open-CV interface.

#### Demo
##### Hand Tracking & Control of Grid Interface
<p align="center"><img src="Media/Mouse_HandTracker.gif" width="450" height="250"/><img src="Media/Grip3_handtracker.gif" width="150" height="250"/><p align="center">

## Further improvements
...
