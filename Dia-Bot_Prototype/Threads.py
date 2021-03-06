import sys
import os
import time
import math
import threading
import multiprocessing
import FileIO


class DiaThread():
    
    def __init__(self, name, useProcess, startTime, shutdownRespQueue, freqHz, loopFunction, *args):
        self.startTime = startTime
        self.threadRunning = False
        self.threadEnded = False
        self.shutdownInitQueue = multiprocessing.Queue() # Process receives ending message on this queue
        self.shutdownRespQueue = shutdownRespQueue # Thread/process sends message to parent when completed 
        self.loopFreq = freqHz
        self.loopTIme = 1/freqHz
        self.name = name
        self.useProcess = useProcess
        print(f"Create and add new loop thread: {loopFunction.__name__}")
        if useProcess:
            self.thread = multiprocessing.Process(name=self.name, target=self.loopAtFrequency, args=(freqHz, self.shutdownInitQueue, loopFunction, args))
            self.thread.daemon = True
        else:
            self.thread = threading.Thread(name=self.name, target=self.loopAtFrequency, args=(freqHz, self.shutdownInitQueue, loopFunction, args))
            self.thread.daemon = True
            

    # Wrapper to other functions which loops 
    def loopAtFrequency(self, freqHz, shutdownInitQueue, loopFunction, *args):
        print(f"Starting thread {self.name} with args {args} (len {len(args)}) at {freqHz} Hz - {self.thread}")
        loopTime = 1/freqHz
        pid = os.getpid()
        while self.threadRunning:
            loopStartTime = time.time()
            #print(f"Calling loopFunction {loopFunction.__name__}: {args}")
            loopFunction(*args)
            loopEndTime = time.time()
            loopTimeTaken = loopEndTime - loopStartTime
            timeRemaining = loopTime - (loopTimeTaken)
            if timeRemaining > 0:
                time.sleep(timeRemaining)
            else:
                print(f"Thread {self.name} took longer to execute ({loopTimeTaken} s) than its given time({loopTime} s)! Assigning {loopTime}s sleep")
                time.sleep(loopTime)
            # For processes, check the shutdown queue for a stop message 
            # (threads keep self.threadRunning in the same context, so queues are unnecessary) 
            if self.useProcess:
                if not shutdownInitQueue.empty():
                    msg = shutdownInitQueue.get()
                    #print(f"shutdownInitQueue msg: {msg}")
                    if msg == "END_THREAD":
                        self.threadRunning = False
        self.threadEnded = True
        self.shutdownRespQueue.put(("THREAD_ENDED", self.name))
        print(f"Loop ended! {self.name} ({pid})")
        
    def startThread(self):
        self.threadRunning = True
        self.thread.start()

    # Sets thread ending flag, but NON-BLOCKING
    def endThread(self):
        print(f"Ending thread! {self.name}")
        self.threadRunning = False
        if self.useProcess:
            self.shutdownInitQueue.put("END_THREAD")

    def join(self, *args):
        return self.thread.join(*args)

    def is_alive(self):
        return self.thread.is_alive()

    def terminate(self):
        if self.useProcess:
            return self.thread.terminate()
        else:
            print(f"Error - Only processes can use terminate() - {self.name} uses threading")

    # BLOCKING call to ensure all threads end
    def waitForThreadsEnd(threads, shutdownRespQueue, name, pid, maxLoops = float('inf')):
        threadRunningCount = len(threads)
        loops = 0
        while threadRunningCount > 0 and loops < maxLoops:
            # Check for thread ending messages every second
            loops += 1
            if not shutdownRespQueue.empty():
                msg, name = shutdownRespQueue.get()
                if msg == "THREAD_ENDED":
                    threadRunningCount -= 1
                    print(f"Shutdown message received within {pid}:{name} - waiting on {threadRunningCount} more!")
                else:
                    print(f"UNEXPECTED MESSAGE IN SHUTDOWN RESPONSE QUEUE: {msg}")
            else:
                time.sleep(1)
                if loops >= maxLoops:
                    print(f"Max time hit in waitForThreadsEnd! ({maxLoops} loops)")

    def joinAllThreads(threads):
        for t in threads:
            print(f"Joining DiaThread {t.name}...")
            t.join(1)
            if t.is_alive():
                print(f"DiaThread {t.name} did not join...terminating")
                t.terminate()



# Parent process starts a new process which spawns child threads
class DiaProcess():

    def __init__(self, fields, shutdownInitQueue, shutdownRespQueue, ProcessingType, isPlotted, dataQueue, visualQueue, processingQueue, alertIOqueue, positionQueue=0, zeroPositionQueue=0, accCalibration=0):
        self.name = fields.name.replace(" ", "")
        self.externalShutdownInitQueue = shutdownInitQueue # External - Receive shutdown message from main process
        self.externalShutdownRespQueue = shutdownRespQueue # External - Confirm shutdown to main process
        self.process = multiprocessing.Process(target=DiaProcess.beginDataProcessing, args=(fields, ProcessingType, isPlotted, dataQueue, visualQueue, processingQueue, alertIOqueue, shutdownInitQueue, positionQueue, zeroPositionQueue, accCalibration))
        self.process.daemon = True

    # Called from main process
    def startProcess(self):
        self.process.start()

    # Called from main process
    def beginShutdown(self):
        #print(f"Sending shutdown message to procuess {self.name}")
        self.externalShutdownInitQueue.put("END_PROCESS")

    # Called from main process
    def joinProcess(self, *args):
        self.process.join(*args)

    # Called from main process
    def is_alive(self):
        return self.process.is_alive()

    # Called internally by process
    def waitForShutdownMessage(externalShutdownInitQueue, loopTime):
        endMessageReceived = False
        while not endMessageReceived:
            while externalShutdownInitQueue.empty():
                time.sleep(loopTime)
            msg = externalShutdownInitQueue.get()
            if msg == "END_PROCESS":
                endMessageReceived = True

    
    # -------- Function to initialize data processing processes --------
    #   ----- This will be run in the context of the new process! -----
    def beginDataProcessing(fields, ProcessingType, isPlotted, dataQueue, visualQueue, processingQueue, alertIOqueue, externalShutdownInitQueue, positionQueue, zeroPositionQueue, accCalibration):
        pid = os.getpid()
        threadRunningCount = 0
        internalShutdownRespQueue = multiprocessing.Queue()
        name = fields.name.replace(" ", "")

        # Initialize DataProcessing class in new process context
        if name == "Vibration": # Send position queue to vibration processing
            processing = ProcessingType(fields.alertDataType, name, fields.units, fields.samplingRate, fields.startTime, isPlotted, dataQueue, visualQueue, processingQueue, positionQueue, zeroPositionQueue, accCalibration)
        else:
            processing = ProcessingType(fields.alertDataType, name, fields.units, fields.samplingRate, fields.startTime, isPlotted, dataQueue, visualQueue, processingQueue)

        fileIO = FileIO.FileIO(fields, alertIOqueue, processing)

        # Add child threads for data collection, visuals, and processing
        collectionThread = DiaThread(f"{name}CollectionThread", False, fields.startTime, internalShutdownRespQueue, fields.samplingRate, processing.getAndAddData)
        processingThread = DiaThread(f"{name}ProcessingThread", False, fields.startTime, internalShutdownRespQueue, .4, processing.mainProcessing)
        alertIOthread = DiaThread(f"{name}AlertIOThread", False, fields.startTime, internalShutdownRespQueue, .1, fileIO.alertIO)

        # Start worker threads
        threads = [collectionThread, processingThread, alertIOthread]#, visualThread]
        for t in threads:
            t.startThread()
            threadRunningCount += 1
            print(f"Starting thread {t.name} in {name}:{pid}")

        # LOOP HERE DURING EXECUTION - Wait for shutdown message - check every 3 seconds
        DiaProcess.waitForShutdownMessage(externalShutdownInitQueue, 3)

        # End threads - Send signal, NON-BLOCKING
        for t in threads:
            t.endThread()
        
        # Collect Thread ending messages
        DiaThread.waitForThreadsEnd(threads, internalShutdownRespQueue, name, pid)

        # Threads ended - join me, and together, we will rule the galaxy...
        print(f"All threads ended in {name}:{pid} - joining...")

        DiaThread.joinAllThreads(threads)

        print(f"DiaProcess {name}:{pid} completed.")