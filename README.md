# Dia-Bot Project Overview
Diagnostic Robot for Georgia Tech Interdisciplinary Capstone Design Fall 2021

Electrical & Software Team
* Connor Truono
* Catherine Kasper

Mechanical Team
* Hunter Present
* Andrew Galant
* Douglas Walker
* Jason Poitter

Full project reports and documentation can be found at the Operation Omega Team Website hosted by the Georgia Tech ECE Senior Design Course: <http://eceseniordesign2021fall.ece.gatech.edu/sd21f09/>

# Dia-bot Software Documentation


## Overview

**To Run the Program**
Testing with GUI: sudo python3 DiaBotGUI.py


**Controls:**
Suppress print statements
Suppress debugging functions
Tag what the function interfaces with


**Files Code**
* Alerts.py
* DataCollection.py
* DataDisplay.py
* DataProcessing.py
* DCMotor.py (Deprecated for other motor system)
* DiaBotGUI.py
* DualHBridge.py (Deprecated for other motor system)
* FileIO.py
* PiInterface.py
* Positioning.py
* robot_test.py (Note: all the functionality has been removed from this file and placed into others.)
* Threads.py

Pictures
* Assets/
*   Arrow-Down-Left.jpg
*   Arrow-Down-Right.jpg
*   Arrow-Down-S.jpg
*   Arrow-Down.jpg
*   Arrow-Left-A.jpg
*   Arrow-Left.jpg
*   Arrow-Right-D.jpg
*   Arrow-Right.jpg
*   Arrow-Up-Left.jpg
*   Arrow-Up-Right.jpg
*   Arrow-Up-W.jpg
*   Arrow-Up.jpg
*   Camera-Icon.jpg
*   Clear-Icon.jpg
*   Delete-Icon.jpg
*   Video-Frame.jpg

**Pin Connections**
| Item | Component Pin | Pi Pin |
| ------------- |:-------------:| :-----:|
| LED | Long Lead | 11 |
| DualHBridge | PWM (in) | 12 |
| DualHBridge | Motor A (in 1) | 15 |
| DualHBridge | Motor A (in 2) | 16 |
| DualHBridge | PWM (in) | 19 |
| DualHBridge | Motor B (in 1) | 21 |
| DualHBridge | Motor B (in 2) | 22 |
| DualHBridge | Motor Enable | 18 |
| Camera | N/a | camera port |

## Alerts.py

Imports: sys, tkinter, time, threading, math, random, enum 

Classes Used: DataCollection

## DataCollection.py

Description: Contains the DataCollection class which has 4 subclasses: SoundLevelCollection, VibrationCollection, PositionCollection, and TemperatureCollection

### DataCollection Class

variables: 
* name
* units
* samplingRate
* globalStartTime
* t (list of times)
* data (list of data)

DataCollection( name, units, samplingRate, globalStartTime)
* Initializes the DataCollection instance with the a name, units of data to be collected, sampling rate and data collection start time
* Creates two Lists data for a collection of the data and t for time stamp that correlates to the data value

addData(t, data) - helper function
* Adds the data value data which was taken at time t
* Mutex locks the lists 

readAndAddData(*args)
* calculates t
* reads the data value
* calls readData(t, data)

### SoundLevelCollection Class

Description: subclass of DataCollection

SoundLevelCollection(name, units, samplingRate, globalStartTime)
* Initializes the SoundLevelCollection instance using the super's function

readData()  _@toBeFilledIn_


### VibrationCollection Class

Description: subclass of DataCollection

VibrationCollection(name, units, samplingRate, globalStartTime)
* Initializes the VibrationCollection instance using the super's function

readData()  _@toBeFilledIn_

### PositionCollection Class

Description: subclass of DataCollection

PositionCollection(name, units, samplingRate, globalStartTime)
* Initializes the PositionCollection instance using the super's function

readData()  _@toBeFilledIn_

### TemperatureCollection Class

Description: subclass of DataCollection

TemperatureCollection(name, units, samplingRate, globalStartTime)
* Initializes the TemperatureCollection instance using the super's function

readData()  _@toBeFilledIn_

## DataProcessing.py

Imports: sys, tkinter, time, PIL, threading, multiprocesssing, math, random, matplotlib

Classes Used: DataCollection

### Data processing

variables:
* tkTop
* dataCollection
* dataMutex
* globalUImutex
* 


## DCMotor.py
## DiaBotGUI.py
## DualHBridge.py
## PiInterface.py

(move)
Variables 
* top Tk
* led
* camera
* speed
* zoom
* gpioMode
* pi
* motors

Threading Variables
* graphRefreshTime
* programRunning
* collectData
* startTime

Functions
* exit
* elapsedTime #debugging
* totalElapsedTime
* setSpeed
* moveForwardPress()
* moveForwardRightPress()
* moveForwardLeftPress()
* moveBackwardPress()
* moveBackwardRightPress()
* moveBackwardLeftPress()
* moveRightPress()
* moveLeftPress()
* moveRelease()
* stopMovement()
* ledOn()
* ledOff()


## Threads.py


# UI Page Layout


