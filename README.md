# Dia-Bot Project Overview
Diagnostic Robot for Georgia Tech Interdisciplinary Capstone Design Fall 2021

Mechanical Team: Hunter Present, Andrew Galant, Douglas Walker, & Jason Poitter
Electrical & Software Team: Connor Truono & Catherine Kasper

# Dia-bot Software Documentation
Other Mechanical and comprehensive electrical documentation can be found at [Operation Omega Team Website hosted by ece ssenior design] (eceseniordesign2021fall.ece.gatech.edu/sd21f09/ "Operation Omega Dia-Bot Team Website").

**To Run the Program**
Testing with GUI: python3 DiaBotGUI.py


**Controls:**
Suppress print statements
Suppress debugging functions
Tag what the function interfaces with


**Files Code**
* Alerts.py
* DataCollection.py
* DataProcessing.py
* DCMotor.py
* DiaBotGUI.py
* DualHBridge.py
* PiInterface.py
* robot_test.py
* Threads.py
Pictures
* frame.png
* vanderlandeTest.png

**Pin Connections**
Item	Component Pin	Pi Pin
LED	Long Lead	11
DualHBridge	PWM (in)	12
DualHBridge	Motor A (in 1)	15
DualHBridge	Motor A (in 2)	16
DualHBridge	PWM (in)	19
DualHBridge	Motor B (in 1)	21
DualHBridge	Motor B (in 2)	22
DualHBridge	Motor Enable	18
Camera	N/a pi camera	N/a


**robot_test.py**
Variables 
* top Tk
* led
* camera
* speed
* zoom
* gpioMode
* pi
* motors
Threading Variable
* graphRefreshTime
* programRunning
* collectData
* uiMutex
* startTime
Functions
* exit
* elapsedTime #debugging
* totalElapsedTime
* setSpeed
* moveForwardPress() #toBeFilledIn
* movedForwardRelease() #toBeFilledIn
* moveForwardRightPress() #toBeFilledIn
* moveForwardRightRelease() #toBeFilledIn
* moveForwardLeftPress() #toBeFilledIn
* moveForwardLeftRelease() #toBeFilledIn
* moveBackwardPress() #toBeFilledIn
* moveBackwardRelease() #toBeFilledIn
* moveBackwardRightPress() #toBeFilledIn
* moveBackwardRightRelease() #toBeFilledIn
* moveBackwardLeftPress() #toBeFilledIn
* moveBackwardLeftRelease() #toBeFilledIn
* moveRightPress() #toBeFilledIn
* moveRightRelease() #toBeFilledIn
* moveLeftPress() #toBeFilledIn
* moveLeftRelease() #toBeFilledIn
* stopMovement() #toBeFilledIn
* lock() #toBeFilledIn
* ledOn()


