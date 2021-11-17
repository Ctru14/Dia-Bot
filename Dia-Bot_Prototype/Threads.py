import sys
import os
import time
import math
import threading
import multiprocessing


class DiaThread():
    
    def __init__(self, name, useProcess, globalStartTime, shutdownRespQueue, freqHz, loopFunction, *args):
        self.globalStartTime = globalStartTime
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
            self.thread = multiprocessing.Process(target=self.loopAtFrequency, args=(freqHz, self.shutdownInitQueue, loopFunction, args))
        else:
            self.thread = threading.Thread(target=self.loopAtFrequency, args=(freqHz, self.shutdownInitQueue, loopFunction, args))
            

    # Wrapper to other functions which loops 
    def loopAtFrequency(self, freqHz, shutdownInitQueue, loopFunction, *args):
        print(f"Starting thread {self.name} with args {args} (len {len(args)}) at {freqHz} Hz - {self.thread}")
        loopTime = 1/freqHz
        loopRuns = 0
        while self.threadRunning:
            loopRuns = loopRuns + 1
            #print(f"Running {loopFunction.__name__} for loop number {loopRuns}")
            loopStartTime = time.time()
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
        print(f"Loop ended! {self.name}")
        
    def startThread(self):
        self.threadRunning = True
        self.thread.start()

    # Sets flags, but NON-BLOCKING
    def endThread(self):
        print(f"Ending thread! {self.name}")
        self.threadRunning = False
        if self.useProcess:
            self.shutdownInitQueue.put("END_THREAD")
        #self.thread.join()
        #while not self.threadEnded:
        #    print(f"Waiting for thread {self.name} to end...")
        #    time.sleep(1)
        #ended = False
        #while not ended:
        #while endQueue.empty():
        #    print(f"Awaiting endQueue message for {self.name}...")
        #    time.sleep(1)

    def join(self, *args):
        return self.thread.join(*args)

    def is_alive(self):
        return self.thread.is_alive()

    def terminate(self):
        if self.useProcess:
            return self.thread.terminate()
        else:
            print(f"Error - Only processes can use terminate() - {self.name} uses threading")

    def waitForThreadsEnd(threads, shutdownRespQueue, name, pid):
        threadRunningCount = len(threads)
        while threadRunningCount > 0:
            # Check for thread ending messages every second
            if not shutdownRespQueue.empty():
                msg, name = shutdownRespQueue.get()
                if msg == "THREAD_ENDED":
                    threadRunningCount -= 1
                    print(f"Shutdown message received within {pid}:{name} - waiting on {threadRunningCount} more!")
                else:
                    print(f"UNEXPECTED MESSAGE IN SHUTDOWN RESPONSE QUEUE: {msg}")
            else:
                time.sleep(1)

    def joinAllThreads(threads):
        for t in threads:
            print(f"Joining {t.name}...")
            t.join(1)
            if t.is_alive():
                print(f"Thread {t.name} did not join...terminating")
                t.terminate()



# Parent process starts a new process which spawns child threads
class DiaProcess():

    def __init__(self, name, units, samplingRate, globalStartTime, shutdownInitQueue, shutdownRespQueue, ProcessingType, isPlotted, dataQueue, visualQueue, processingQueue):
        self.name = name
        self.externalShutdownInitQueue = shutdownInitQueue # External - Receive shutdown message from main process
        self.externalShutdownRespQueue = shutdownRespQueue # External - Confirm shutdown to main process
        self.process = multiprocessing.Process(target=DiaProcess.beginDataProcessing, args=(name, units, samplingRate, globalStartTime, ProcessingType, isPlotted, dataQueue, visualQueue, processingQueue, shutdownInitQueue))

    # Called from main process
    def startProcess(self):
        self.process.start()

    # Called from main process
    def beginShutdown(self):
        #print(f"Sending shutdown message to procuess {self.name}")
        self.externalShutdownInitQueue.put("END_PROCESS")


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
    def beginDataProcessing(name, units, samplingRate, startTime, ProcessingType, isPlotted, dataQueue, visualQueue, processingQueue, externalShutdownInitQueue):
        pid = os.getpid()
        threadRunningCount = 0
        internalShutdownRespQueue = multiprocessing.Queue()

        # Initialize DataProcessing class in new process context
        processing = ProcessingType(name, units, samplingRate, startTime, isPlotted, dataQueue, visualQueue, processingQueue)

        # Add child threads for data collection, visuals, and processing
        collectionThread = DiaThread(f"{name}CollectionThread", False, startTime, internalShutdownRespQueue, samplingRate, processing.getAndAddData)
        # TODO: visualThread = 
        # TODO: processingThread = 

        # Start worker threads
        threads = [collectionThread]
        for t in threads:
            t.startThread()
            threadRunningCount += 1
            print(f"Starting thread {t.name} in {pid}:{name}")

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

        print(f"Process {pid}:{name} completed.")