import sys
import os
import tkinter as tk
from tkinter import *
from tkinter.scrolledtext import ScrolledText
from PIL import ImageTk, Image
import time
import threading
import multiprocessing
import math
import enum
from random import *

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure

# Dia-Bot specific imports
import DataCollection
import DataDisplay
import DataProcessing
import Alerts
from Alerts import Alert
from Alerts import AlertDataType
from Alerts import AlertMetric
from Alerts import AlertRange
from Alerts import AlertTracker
from Alerts import AlertsTop
from Threads import DiaThread
from Threads import DiaProcess

piConnected = True
try:
    import PiInterface
except Exception as e:
    piConnected = False
    print(f"Error importing PiInterface: {e}")

# Debugging function - run a function and report how long it takes
def elapsedTime(func, *args):
    startTime = time.time_ns()
    #try:
    #    func(*args)
    #except:
    func()
    elapsedTimeNs = time.time_ns() - startTime
    print("ElapsedTime (" + str(func.__name__) + ") = " + str(elapsedTimeNs / 1_000_000) + " ms")


class DiaBotGUI():

    def __init__(self, *args, **kwargs):
        # Initialize necessary variables
        self.cameraOn = False
        self.pid = os.getpid()
        self.top = tk.Tk()
        self.top.title('Dia-Bot')
        self.speed = IntVar()
        self.zoom = IntVar()

        # Threading control
        self.visualsRefreshTime = 2 # Number of seconds between visuals refresh
        self.programRunning = True
        self.collectData = True
        #self.uiMutex = threading.Lock()
        self.uiMutex = multiprocessing.Lock()
        self.startTime = time.time_ns()

        # Define GUI frames
        #   Primary sections
        self.controlFrame = tk.Frame(self.top, width=450, height=900)#, bg='orange')
        self.dataFrame = tk.Frame(self.top, width=1120, height=270)#, bg='blue')
        self.videoFrame = tk.Frame(self.top, width=1120, height=630)#, bg='red')
        #   Individual Control Frames
        self.movementControls = tk.Frame(self.controlFrame, width=450, height=280)#, bg='blue')
        self.cameraControls = tk.Frame(self.controlFrame, width=450, height=280)
        self.alertControls = tk.Frame(self.controlFrame, width=450, height=450)


        # Create queues
        self.processingQueue = multiprocessing.Queue()
        self.soundLevelAlertIOQueue = multiprocessing.Queue()
        self.vibrationAlertIOQueue = multiprocessing.Queue()
        #self.positionAlertIOQueue = multiprocessing.Queue()
        self.tempAlertIOQueue = multiprocessing.Queue()
        #self.alertIOqueues = [self.soundLevelAlertIOQueue, self.vibrationAlertIOQueue, self.positionAlertIOQueue, self.tempAlertIOQueue]
        self.alertIOqueues = [self.soundLevelAlertIOQueue, self.vibrationAlertIOQueue, self.tempAlertIOQueue]


        # Data collection (Must be created in constructor to guaranteee use in Alerts)
        self.soundLevelSamplingRate = 100
        self.soundLevelFields, self.soundLevelDataQueue, self.soundLevelVisualQueue, self.soundLevelCollection = DiaBotGUI.createDataFields(
            DataCollection.SoundLevelCollection, "Sound Level", "dB", self.soundLevelSamplingRate, self.startTime)
        
        self.vibrationSamplingRate = 100
        self.vibrationFields, self.vibrationDataQueue, self.vibrationVisualQueue, self.vibrationCollection = DiaBotGUI.createDataFields(
            DataCollection.VibrationCollection, "Vibration", "m/s2", self.vibrationSamplingRate, self.startTime)
         
        self.temperatureSamplingRate = 1/5
        self.temperatureFields, self.temperatureDataQueue, self.temperatureVisualQueue, self.temperatureCollection = DiaBotGUI.createDataFields(
            DataCollection.TemperatureCollection, "Temperature", "°C", self.temperatureSamplingRate, self.startTime)
        
        # Position is handled differently! Still creates fields, but no extra processes
        self.positionSamplingRate = 10
        self.positionFields, self.positionDataQueue, self.positionVisualQueue, self.positionCollection = DiaBotGUI.createDataFields(
            DataCollection.PositionCollection, "Position", "m", self.positionSamplingRate, self.startTime)
         
        
        
        # Group of all the data classes
        self.dataFieldsClassList = [self.soundLevelFields, self.vibrationFields, self.positionFields, self.temperatureFields]



    # Closes relevant processes and stops GPIO
    def exit(self):
        self.camera.close()
        self.top.destroy
        quit()


    # -------------------------- GUI SETUP CODE --------------------------
    def setupGuiFrames(self):
        self.top.resizable(width=False, height=False)
        self.top.geometry("1920x1016")

        # Build the frames
        self.setupDataPane()
        self.setupControlsPane()
        self.setupVideoPane()
        
        # Place frames
        self.bindEvents()
        self.placeFrames()



    # ------------------ Controls Pane -----------------------

    # --- Callback functions ---
    def speedChanged(self, event):
        PiInterface.speed=self.speed.get()
    
    #def updateAlerts(self):
    #    for alert in self.alertsTop.alertTrackers:
    #        alert.confirmUpdates()

    # --- Controls pane setup function ---
    def setupControlsPane(self):
        # Controls top text
        self.controlsLabel = tk.Label(self.controlFrame, text="Controls", font="none 18 bold")#, bg="orange")
        self.controlsLabel.grid(row=1, column=1, columnspan=8)
        self.controlsLabel.config(anchor=CENTER)
        self.controlFrame.grid_rowconfigure(1, minsize=60)
        
        # Get images for menu icons
        self.importMenuImages()

        # Create individual controls panes
        self.setupMovementControls()
        self.setupCameraControls()
        self.setupAlertControls()
    
        

    # ----- Movement controls -----
    def setupMovementControls(self):
        self.movementControls.grid(row=2, column=1, rowspan=2, columnspan=10)
        Label(self.movementControls, text="Movement", anchor=CENTER, font="none 14 bold").grid(row=1, column=1, columnspan=9)

        # Speed slider
        tk.Label(self.movementControls, text="Speed", anchor=CENTER, font="bold").grid(row=2, column=2)
        self.speedScale = tk.Scale(self.movementControls, from_=100, to=0, orient=tk.VERTICAL, variable=self.speed, command=self.speedChanged, length=150, showvalue=1, sliderlength=20)
        self.speedScale.grid(row=3, column=2, rowspan=4)
        self.speedScale.set(50)

        # Directional buttons
        tk.Label(self.movementControls, text="Direction", anchor=CENTER, font="bold").grid(row=2, column=4, columnspan=3)
        self.setupMovementDirectionalButtons()
        
        # Stop and lock buttons
        tk.Label(self.movementControls, text="Mode", anchor=CENTER, font="bold").grid(row=2, column=9)
        tk.Button(self.movementControls, text="Stop", command=PiInterface.stopMovement, anchor=CENTER, fg="red", font="16").grid(row=3, column=9)
        tk.Button(self.movementControls, text="Lock", command=PiInterface.lock, anchor=CENTER, font="16").grid(row=5, column=9)
        
        self.movementControls.grid_columnconfigure(1, minsize=10)
        for i in range(2,10):
            self.movementControls.grid_columnconfigure(i, minsize=20)
            

    def importMenuImages(self):
        # Directional arrows
        self.arrowUp = ImageTk.PhotoImage(Image.open("Assets/Arrow-Up.jpg").resize((30, 30)))
        self.arrowUpW = ImageTk.PhotoImage(Image.open("Assets/Arrow-Up-W.jpg").resize((30, 30)))
        self.arrowUpLeft = ImageTk.PhotoImage(Image.open("Assets/Arrow-Up-Left.jpg").resize((30, 30)))
        self.arrowUpRight = ImageTk.PhotoImage(Image.open("Assets/Arrow-Up-Right.jpg").resize((30, 30)))
        self.arrowDown = ImageTk.PhotoImage(Image.open("Assets/Arrow-Down.jpg").resize((30, 30)))
        self.arrowDownS = ImageTk.PhotoImage(Image.open("Assets/Arrow-Down-S.jpg").resize((30, 30)))
        self.arrowDownLeft = ImageTk.PhotoImage(Image.open("Assets/Arrow-Down-Left.jpg").resize((30, 30)))
        self.arrowDownRight = ImageTk.PhotoImage(Image.open("Assets/Arrow-Down-Right.jpg").resize((30, 30)))
        self.arrowLeft = ImageTk.PhotoImage(Image.open("Assets/Arrow-Left.jpg").resize((30, 30)))
        self.arrowLeftA = ImageTk.PhotoImage(Image.open("Assets/Arrow-Left-A.jpg").resize((30, 30)))
        self.arrowRight = ImageTk.PhotoImage(Image.open("Assets/Arrow-Right.jpg").resize((30, 30)))
        self.arrowRightD = ImageTk.PhotoImage(Image.open("Assets/Arrow-Right-D.jpg").resize((30, 30)))
        # Other
        self.cameraIcon = ImageTk.PhotoImage(Image.open("Assets/Camera-Icon.jpg").resize((30, 30)))
        self.deleteIcon = ImageTk.PhotoImage(Image.open("Assets/Delete-Icon.jpg").resize((22, 22)))
        self.clearIcon = ImageTk.PhotoImage(Image.open("Assets/Clear-Icon.jpg").resize((22, 22)))



    # Directional buttons        
    def setupMovementDirectionalButtons(self):

        # Forward
        self.moveForwardButton = tk.Button(self.movementControls, image=self.arrowUpW, anchor=CENTER, font="16")
        self.moveForwardButton.bind("<ButtonPress>", PiInterface.moveForwardPress)
        self.moveForwardButton.bind("<ButtonRelease>", PiInterface.moveForwardRelease)
        self.moveForwardButton.grid(row=3, column=5)
        
        # Forward-Left
        self.moveForwardLeftButton = tk.Button(self.movementControls, image=self.arrowUpLeft, anchor=CENTER, font="16")
        self.moveForwardLeftButton.bind("<ButtonPress>", PiInterface.moveForwardLeftPress)
        self.moveForwardLeftButton.bind("<ButtonRelease>", PiInterface.moveForwardLeftRelease)
        self.moveForwardLeftButton.grid(row=3, column=4)
        
        # Forward-Right
        self.moveForwardRightButton = tk.Button(self.movementControls, image=self.arrowUpRight, anchor=CENTER, font="16")
        self.moveForwardRightButton.bind("<ButtonPress>", PiInterface.moveForwardRightPress)
        self.moveForwardRightButton.bind("<ButtonRelease>", PiInterface.moveForwardRightRelease)
        self.moveForwardRightButton.grid(row=3, column=6)
        
        # Backward
        self.moveBackwardButton = tk.Button(self.movementControls, image=self.arrowDownS, anchor=CENTER, font="16")
        self.moveBackwardButton.bind("<ButtonPress>", PiInterface.moveBackwardPress)
        self.moveBackwardButton.bind("<ButtonRelease>", PiInterface.moveBackwardRelease)
        self.moveBackwardButton.grid(row=5, column=5)
        
        # Backward-Left
        self.moveBackwardLeftButton = tk.Button(self.movementControls, image=self.arrowDownLeft, anchor=CENTER, font="16")
        self.moveBackwardLeftButton.bind("<ButtonPress>", PiInterface.moveBackwardLeftPress)
        self.moveBackwardLeftButton.bind("<ButtonRelease>", PiInterface.moveBackwardLeftRelease)
        self.moveBackwardLeftButton.grid(row=5, column=4)
        
        # Backward-Right
        self.moveBackwardRightButton = tk.Button(self.movementControls, image=self.arrowDownRight, anchor=CENTER, font="16")
        self.moveBackwardRightButton.bind("<ButtonPress>", PiInterface.moveBackwardRightPress)
        self.moveBackwardRightButton.bind("<ButtonRelease>", PiInterface.moveBackwardRightRelease)
        self.moveBackwardRightButton.grid(row=5, column=6)
        
        # Left
        self.moveLeftButton = tk.Button(self.movementControls, image=self.arrowLeftA, anchor=CENTER, font="16")
        self.moveLeftButton.bind("<ButtonPress>", PiInterface.moveLeftPress)
        self.moveLeftButton.bind("<ButtonRelease>", PiInterface.moveLeftRelease)
        self.moveLeftButton.grid(row=4, column=4)
        
        # Right
        self.moveRightButton = tk.Button(self.movementControls, image=self.arrowRightD, anchor=CENTER, font="16")
        self.moveRightButton.bind("<ButtonPress>", PiInterface.moveRightPress)
        self.moveRightButton.bind("<ButtonRelease>", PiInterface.moveRightRelease)
        self.moveRightButton.grid(row=4, column=6)

        # Keyboard Buttons
        self.top.bind("<KeyPress-w>", PiInterface.moveForwardPress)
        self.top.bind("<KeyRelease-w>", PiInterface.moveForwardRelease)
        self.top.bind("<KeyPress-s>", PiInterface.moveBackwardPress)
        self.top.bind("<KeyRelease-s>", PiInterface.moveBackwardRelease)
        self.top.bind("<KeyPress-a>", PiInterface.moveLeftPress)
        self.top.bind("<KeyRelease-a>", PiInterface.moveLeftRelease)
        self.top.bind("<KeyPress-d>", PiInterface.moveRightPress)
        self.top.bind("<KeyRelease-d>", PiInterface.moveRightRelease)

    # ----- Camera Controls -----
    def setupCameraControls(self):
        self.cameraControls.grid(row=5, column=1, rowspan=1, columnspan=10)
        tk.Label(self.cameraControls, text="Camera", anchor=CENTER, font="none 14 bold").grid(row=1, column=1, columnspan=9)
        
        # Directional buttons
        tk.Label(self.cameraControls, text="Angle", anchor=CENTER, font="bold").grid(row=2, column=2, columnspan=3)
        tk.Button(self.cameraControls, image=self.arrowUp, command=PiInterface.cameraUp, anchor=CENTER, font="16").grid(row=3, column=3)
        tk.Button(self.cameraControls, image=self.arrowDown, command=PiInterface.cameraDown, anchor=CENTER, font="16").grid(row=5, column=3)
        tk.Button(self.cameraControls, image=self.arrowLeft, command=PiInterface.cameraLeft, anchor=CENTER, font="16").grid(row=4, column=2)
        tk.Button(self.cameraControls, image=self.arrowRight, command=PiInterface.cameraRight, anchor=CENTER, font="16").grid(row=4, column=4)
        tk.Button(self.cameraControls, image=self.cameraIcon, command=takePhoto, anchor=CENTER, font="16").grid(row=4, column=3)
        
        # Stop and lock buttons
        tk.Label(self.cameraControls, text="Light", anchor=CENTER, font="bold").grid(row=2, column=6)
        tk.Button(self.cameraControls, text="On", command=PiInterface.ledOn, anchor=CENTER, font="16").grid(row=4, column=6)
        tk.Button(self.cameraControls, text="Off", command=PiInterface.ledOff, anchor=CENTER, font="16").grid(row=5, column=6)
        
        # Zoom slider
        tk.Label(self.cameraControls, text="Zoom", anchor=CENTER, font="bold").grid(row=2, column=8)
        self.zoomScale = tk.Scale(self.cameraControls, from_=100, to=0, orient=tk.VERTICAL, variable=self.zoom, length=150, showvalue=0, sliderlength=20)
        self.zoomScale.grid(row=3, column=8, rowspan=4)
        self.zoomScale.set(50)
        
        self.cameraControls.grid_columnconfigure(1, minsize=10)
        for i in range(2,10):
            self.cameraControls.grid_columnconfigure(i, minsize=20)

    # TK button function to capture and save image
    def takePhoto():
        dtFormat = "{:%Y%m%d-%H%M%S}"
        timeString = dtFormat.format(datetime.now())
        fileName = f"img-{timeString}.jpg"
        path = os.path.join(self.photosPath, fileName)
        PiInterface.captureImage(path)

    # ----- Alert Controls -----
    def setupAlertControls(self):
        self.alertControls.grid(row=7, column=1, rowspan=1, columnspan=10)
        tk.Label(self.alertControls, text="Alert Trackers", anchor=CENTER, font="none 14 bold").grid(row=1, column=1, columnspan=9)
        
        # Extra TK frame to display just the alert trackers
        self.alertTrackersFrame = tk.Frame(self.alertControls, width=400)

        # Create each alert instance and add frames to the UI
        self.alertsTop = AlertsTop(self.alertControls, self.alertTrackersFrame, self.processingQueue, self.alertIOqueues, self.deleteIcon, self.clearIcon, self.alertsText, PiInterface.captureImage)

        self.vibrationAlertTracker = AlertTracker(self.alertsTop, self.alertTrackersFrame,   "Vibration",   AlertDataType.Vibration,   AlertRange.Above,   AlertMetric.Average, self.vibrationAlertIOQueue, self.deleteIcon, self.clearIcon)
        self.temperatureAlertTracker = AlertTracker(self.alertsTop, self.alertTrackersFrame, "Temperature", AlertDataType.Temperature, AlertRange.Between, AlertMetric.Average, self.tempAlertIOQueue, self.deleteIcon, self.clearIcon)
        
        self.alertsTop.addTracker(self.vibrationAlertTracker)
        self.alertsTop.addTracker(self.temperatureAlertTracker)

        self.alertTrackersFrame.grid(row=2, column=1, columnspan=12)
        
        # Press this button to confirm and lock in Alert changes
        self.confirmButton = tk.Button(self.alertControls, text="Confirm", command=self.alertsTop.updateAlerts)#, state=DISABLED) #TODO: enable/disable the button for updates
        self.confirmButton.grid(row=3, column=8, columnspan=2)
        
        # Add frame to add new trackers
        self.newAlertsFrame = self.alertsTop.buildNewTrackerFrame(self.alertControls)
        self.newAlertsFrame.grid(row=4, column=1, columnspan=11)
        
        self.alertControls.grid_columnconfigure(1, minsize=10)
        for i in range(2,10):
            self.alertControls.grid_columnconfigure(i, minsize=20)
        for i in range(2, 5):
            self.alertControls.grid_rowconfigure(i, minsize=30)



    def toggleData(self):
        #global collectData
        print(f"Width: {self.top.winfo_width()}, Height: {self.top.winfo_height()}")
        self.collectData = not self.collectData
        # TODO: send collect data message to queues
        print(f"Setting colletData to {self.collectData}")

    # ------------------ Data Pane -----------------------

    # Main method to setup data pane with each data category
    def setupDataPane(self):
        tk.Label(self.dataFrame, text="Data", font="none 18 bold").grid(row=1, column=1, columnspan=50)
        #tk.Button(self.dataFrame, text="Toggle Data", command=self.toggleData).grid(row=1, column=2)

        # Individual Frames
        self.soundLevelFrame = tk.Frame(self.dataFrame, width=350, height=350)#, bg="red")
        self.vibrationFrame = tk.Frame(self.dataFrame, width=350, height=350)#, bg="yellow")
        self.temperatureFrame = tk.Frame(self.dataFrame, width=350, height=350)#, bg="orange")
        self.positionFrame = tk.Frame(self.dataFrame, width=350, height=350)#, bg="green")
        self.alertsDisplayFrame = tk.Frame(self.dataFrame, width=350, height=350)
        self.dataFrames = [self.soundLevelFrame, self.vibrationFrame, self.temperatureFrame, self.positionFrame]
        #self.units = ["dB", "m/s2", "°C", "m"]
        
        
        # Sound Level
        self.soundLevelDisplayClass = DataDisplay.DataDisplay(self.soundLevelFields, self.soundLevelFrame, self.soundLevelVisualQueue)
        self.soundLevelDisplayClass.tkAddDataPane()
        self.soundLevelFrame.grid(row=2, column=1, padx=10)

        # Vibration
        self.vibrationDisplayClass = DataDisplay.DataDisplay(self.vibrationFields, self.vibrationFrame, self.vibrationVisualQueue)
        self.vibrationDisplayClass.tkAddDataPane()
        self.vibrationFrame.grid(row=2, column=2, padx=10)

        # Temperature
        self.tempDisplayClass = DataDisplay.TemperatureDisplay(self.temperatureFields, self.temperatureFrame, self.temperatureVisualQueue)
        self.tempDisplayClass.tkAddDataPane()
        self.temperatureFrame.grid(row=2, column=3, padx=10)
        
        # Position
        self.positionDisplayClass = DataDisplay.PositionDisplay(self.positionFields, self.positionFrame, self.positionVisualQueue)
        self.positionDisplayClass.tkAddDataPane()
        self.positionFrame.grid(row=2, column=4, padx=10)


        # Alerts scrolled text
        self.alertsDisplayLabel = tk.Label(self.alertsDisplayFrame, text="Alerts", font="none 12 bold")
        self.alertsDisplayLabel.pack()#grid(row=1, column=1)
        self.alertsText = ScrolledText(self.alertsDisplayFrame, width=65, height=9, font = "none 14")
        #self.alertsText.insert(INSERT, "New text woooooohoo!")
        self.alertsText.pack()#(row=1, column=1)
        self.alertsDisplayFrame.grid(row=2, column=5, padx=10)


    def createDataFields(CollectionType, name, units, samplingRate, startTime): # TODO: REMOVE VISUALQ FROM COLLECTION
        dataQueue = multiprocessing.Queue()
        visualQueue = multiprocessing.Queue()
        #collection = CollectionType(name, units, samplingRate, startTime, dataQueue)
        if CollectionType == DataCollection.TemperatureCollection:
            collection = CollectionType(name, units, samplingRate, startTime, dataQueue, visualQueue)
        else:
            collection = CollectionType(name, units, samplingRate, startTime, dataQueue)
        fields = DataCollection.DataFields(name, units, samplingRate, startTime, collection.alertDataType)
        return (fields, dataQueue, visualQueue, collection)



    # ------------------ Video Pane -----------------------

    # --- Callback functions ---

    def setupVideoPane(self):
        self.testImg = ImageTk.PhotoImage(Image.open("Assets/Video-Frame.jpg").resize((1380, 715)))
        self.imgLabel = Label(self.videoFrame, image=self.testImg)
        self.imgLabel.grid(row=1, column=1)

    # -------------- Put it all together ---------------
    def placeFrames(self):
        # Place the frames
        self.controlFrame.place(relx=0.01, rely=0.01, anchor=tk.NW)
        self.dataFrame.place(relx=0.3, rely=0.01, anchor=tk.NW)
        self.videoFrame.place(x=450, y=300, anchor=tk.NW)


    # ---------- Threading functions ----------
   
    def bindEvents(self):
        self.top.bind("<<visualsEvent>>", self.updateVisualsWrapper)
        self.top.bind("<<alertsEvent>>", self.updateAlertsHandler)

    # --- Update Visuals Handlers ---

    # Sends update visuals event to TK
    def generateEvent(self, eventString, *args):
        if self.programRunning:
            try:
                self.top.event_generate(eventString)
            except Exception as e:
                print(f"Unable to update visuals! Error in event_generate: {e}")
    
    # Wrapper function around the handler for updating the visuals
    def updateVisualsWrapper(self, event):
        #elapsedTime(self.updateVisualsHandler)
        self.updateVisualsHandler()
    
    # Any data visual which requires manual update (new graphs use animations to update automatically)
    def updateVisualsHandler(self):
        # Only temperature view needs updating 
        self.tempDisplayClass.updateVisual()
        self.positionDisplayClass.updateVisual()
   
    # --- Update Alerts Handlers ---
    def updateAlertsHandler(self, event):
        try:
            self.alertsTop.distributeProcessedData((self.positionDisplayClass.curX, self.positionDisplayClass.curY, self.positionDisplayClass.curZ))
        except Exception as e:
            print(f"Exception thrown in update alerts: {e}")
        

    # ----- Main method for GUI - Starts extra threads and processes and other programs ----
    def startProgram(self):
        # Create GUI
        self.setupGuiFrames()

        # Create and add processes and threads
        useProcesses = True
        shutdownRespQueue = multiprocessing.Queue()

        # ----- Create other processes and threads -----
        # GUI updating threads
        visualThread = DiaThread("visualThread", False, self.startTime, shutdownRespQueue, 1/self.visualsRefreshTime, self.generateEvent, "<<visualsEvent>>") # TODO: increase refresh rate once multiprocessing works
        alertThread = DiaThread("alertThread", False, self.startTime, shutdownRespQueue, 1/2, self.generateEvent, "<<alertsEvent>>")

        # Data collection threads (separate processes)
        soundCollectionProcess = DiaThread("soundCollectionProcess", useProcesses, self.startTime, shutdownRespQueue, self.soundLevelSamplingRate, self.soundLevelCollection.readAndSendData) # TODO: remove collection objects
        vibrationCollectionProcess = DiaThread("vibrationCollectionProcess", useProcesses, self.startTime, shutdownRespQueue,  self.vibrationSamplingRate, self.vibrationCollection.readAndSendData)
        temperatureCollectionProcess = DiaThread("temperatureCollectionProcess", useProcesses, self.startTime, shutdownRespQueue, self.temperatureSamplingRate, self.temperatureCollection.readAndSendData)
        
        threads = [visualThread, alertThread, soundCollectionProcess, vibrationCollectionProcess, temperatureCollectionProcess]

        # Parent processes for data processing
        soundLevelShutdownInitQueue = multiprocessing.Queue()
        soundLevelProcess = DiaProcess(self.soundLevelFields, soundLevelShutdownInitQueue, shutdownRespQueue, DataProcessing.SoundLevelProcessing, 
                                       False, self.soundLevelDataQueue, self.soundLevelVisualQueue, self.processingQueue, self.soundLevelAlertIOQueue)

        vibrationShutdownInitQueue = multiprocessing.Queue()
        vibrationProcess = DiaProcess(self.vibrationFields, vibrationShutdownInitQueue, shutdownRespQueue, DataProcessing.VibrationProcessing, 
                                       False, self.vibrationDataQueue, self.vibrationVisualQueue, self.processingQueue, self.vibrationAlertIOQueue, self.positionVisualQueue)

        tempShutdownInitQueue = multiprocessing.Queue()
        temperatureProcess = DiaProcess(self.temperatureFields, tempShutdownInitQueue, shutdownRespQueue, DataProcessing.TemperatureProcessing, 
                                       False, self.temperatureDataQueue, self.temperatureVisualQueue, self.processingQueue, self.tempAlertIOQueue)
        
        parentProcesses = [soundLevelProcess, vibrationProcess, temperatureProcess]

       
        for process in parentProcesses:
            process.startProcess()

        for t in threads:
            t.startThread()
        self.programRunning = True # Used in updateVisuals()

        # Start camera preview
        try:
            PiInterface.start_camera()
            self.cameraOn = True
        except Exception as e:
            print(f"Error starting camera: {e}")
            self.cameraOn = False
            
        #totalTimeNs = time.time_ns() - startTime
        #print("Start thread time: " + str((totalTimeNs/1_000_000)) + " ms")

        try:
            PiInterface.motorGpioSetup()
        except Exception as e:
            print(f"Error setting up motor GPIO: {e}")

        # Add folder for photos
        self.rootPath = os.path.dirname(__file__)
        self.photosPath = os.path.join(self.rootPath, "Photos")
        if not os.path.exists(self.photosPath):
            print(f"Photos path does not exist - creating: {self.photosPath}")
            os.mkdir(self.photosPath)
        
        # ----- Blocking call: Begin TK mainloop -----
        print("-------- BEGINING TK MAINLOOP --------")
        self.top.mainloop()
        self.programRunning = False
        print("-------- TK MAINLOOP ENDED: ENDING WORKER THREADS --------")
        
        # After UI closed: cleanup!
        
        # Send signals to end all threads and processes
        # Shutdown extra processes properly
        for process in parentProcesses: # DiaProcess
            process.beginShutdown()

        threadRunningCount = 0
        for t in threads:
            threadRunningCount += 1
            t.endThread()

        if self.cameraOn:
            PiInterface.stop_camera()

        
        # Try to join all processes after completion
        print(f"Joining parent processes...") # DiaProcess
        for process in parentProcesses:
            print(f"Joining parent process {process.name} (alive = {process.is_alive()})...")
            process.joinProcess(1)
            print(f"...parent process {process.name} attempted join. (alive = {process.is_alive()})")


        # Collect signals for ending threads and join 
        DiaThread.waitForThreadsEnd(threads, shutdownRespQueue, "Main", self.pid, 20)
                  
        print(f"All threads ended in {self.pid}:Parent process! Joining...")
        DiaThread.joinAllThreads(threads)

        print("Thank you for using Dia-Bot")
        

def main():
    gui = DiaBotGUI()
    gui.startProgram()

if __name__ == "__main__":
    main()

