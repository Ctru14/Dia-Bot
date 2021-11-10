# Dia-Bot
Diagnostic Robot for Georgia Tech Interdisciplinary Capstone Design Fall 2021

Documentation for Dia-bot

Files
* robot_test.py
    * 
* DataCollection.py
    * 
* DCMotor.py
    * 
* DualHBridge.py


Pin Connections
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

Controls:
Suppress print statements
Suppress debugging functions
Tag what the function interfaces with


robot_test.py
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


