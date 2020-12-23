# HandTracking4Sohan <img src="index.png" align="right" alt="drawing" width="250"/>

## Challenges 

Sohan is an 8 years old child that cannot speak. Thus, he needs to communicate to other people using devices such as a computer interface with eye tracking and pressing buttons. This communication was facilitated so far thanks to pictograms placed on the board in front of him and a computer with Grid3 software (https://thinksmartbox.com/product/grid-3/). This software provides a large vocabulary and numerous types of control (button, eye tracker,...)
However, most of the controllers proposed in Grid3 interfaces require a high motor effort. Because of this, his capacity of interaction with other people is largely impaired. In this project, the main goal is to design a controller that allows him to better communicate thanks to an efficient interface requiring less physical effort.  
Sohan has cognitive impairments that do not allow any control of his movements in general. Moreover, he cannot use fingers for pointing or typing or pressing buttons (no hand gestures). He can move only his left hand on the table. His head, very often, falls down on the left side of the body. This makes it very difficult to use eye-tracking devices to detect the gaze for leading the computer interface. 

## Brainstorming
List of the possible solutions: 
Eye-tracker to detect the motion of his eyes; 
Leap motion: a infrared camera to detect the motion of hands; 
Capacitive sensors that can detect the contact (position, direction etc.) with some surfaces  of his left hand; 
Hand tracking camera to detect the motion of his left hand via image processing and computer vision.   
Chosen solution
We decided to combine 2 solutions using capacitive sensors and hand tracking camera to give both discrete (keyboards) and continuous control (mouse). We discarded the eye-tracker and the leap motion because they are not able to accurately detect his eyes and hands motions for a long time due to his unsteady posture on the chair (issues with the calibration of the eyes or hands position link to the angle of the infrared camera - occlusion). Additionally, the leap motion presents a problem of reflection if put under a transparent table (the signal is not detected at all).   
Capacitive sensors and the hand-tracking camera present different advantages:
- Easily detect his hand motion even not accurate and precise on a specific point
- Not sensitive to his posture or body movement
- No calibration for the posture or the position of the body 
- Easily control the computer interface without any physical effort

The combination of the two solutions could even improve the precision of motor detection and decrease the physical effort, providing more precise and clear commands to use for better communication. 
Brief explanation on Solutions:
1. Capacitive sensors: four arrows are displaced on the table (commands), indicating the four directions (up, down, right, left) plus another bottom in the middle (ok --> enter). We used conductor material(copper, aluminum) for the arrows to detect changes in electrical conductance when the person passes the hand over commands. The capacitive sensors are connected to an Arduino Uno that can process the signal to send to the computer interface allowing the navigation in Grid3 software. 

2. Hand-tracking camera: the camera of the computer can detect the hand motion by sensors placed on the thumb and eventually on the index. The hand movement can be translated in the cursor position. Two methods can be used in the interface (HSV filter with a green patch on the hand, hand pose estimation). 


 ## Files 
 - ```requirements.txt``` : Necessary libraries to run the project. 
- ```CameraInterface.py``` : Interface to run 

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
