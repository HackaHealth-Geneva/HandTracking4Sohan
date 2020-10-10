# HandTracking4Sohan

## About Sohan

Sohan is 7 years-old. He is smiling, curious and sometimes can be mischievous. Although not able to speak, Sohan likes to connect with his environment and exchange with the people around him using pictograms and technological devices. With these tools, Sohan is able to have nice conversations with others and will sometimes make you laugh with his jokes. 

## Challenges 

To be able to communicate, these technological devices require a high motor effort such as moving the hand to select a pictogram or pressing buttons to make a selection on the computer. Because of this, the capacity of Sohan to communicate with us is largely impaired. In this project, the goal would be to design a controller that would allow him to communicate through his interface while requiring less physical effort from him. 

 ## Files 
 - ```requirements.txt``` : Necessary libraries to run the project. 
 - ```test.py``` : Main segmentation code, detects green in the webcam image and thresolds HSV values, then performs morphological operations to extract the contour of the detected green shape and using the contour fixes a bounding box and its center. Using the center, it extracts the x and y position coordinates of the green shape and maps it to the screen to move the mouse. 
 - ```CameraInterface.py``` : Creates an command interface to select red, blue and green shapes seen by the webcam. Also creates two checkboxes ```Mouse``` to allow pointer control with the webcam and ```Clic``` to allow the use to use the webcam with two green markers on the fingers and actually clic on the computer by pulling the two fingers closer together. 
 - ```Notes _ Ideas.docx``` : Ideas, notes and ressources for the challenge. 
 
 ## Launch
