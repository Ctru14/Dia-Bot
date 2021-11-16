import sys
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
                    print(f"shutdownInitQueue msg: {msg}")
                    if msg == "END_THREAD":
                        self.threadRunning = False
        self.threadEnded = True
        self.shutdownRespQueue.put(("THREAD_ENDED", self.name))
        print(f"Loop ended! {self.name}")
        
    def startThread(self):
        self.threadRunning = True
        self.thread.start()

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


# Parent process starts a new process which spawns child threads
class DiaProcess():

    def __init__(self, name, globalStartTime, shutdownInitQueue, shutdownRespQueue):
        self.name = name
        self.globalStartTime = globalStartTime
        self.externalShutdownInitQueue = shutdownInitQueue # External
        self.externalShutdownRespQueue = shutdownRespQueue # External
        self.internalShutdownInitQueue = multiprocessing.Queue()
        self.internalShutdownRespQueue = multiprocessing.Queue()
        self.threadsRunning = False
        self.threadsRunningCount = 0
        #self.threadsEnded = False
        self.childThreads = []

    # TODO: remove this method - all DiaThreads need to be added in the function that creates the thread
    def addChildThread(self, threadName, freqHz, function, loopFunction, *args):
        self.childThreads.append(DiaThread(threadName, False, self.globalStartTime, 0, freqHz, loopFunction, *args))

    def startThreads(self):
        self.threadsRunning = True
        for thread in self.childThreads:
            thread.startThread()
            self.threadsRunningCount = self.threadsRunningCount + 1

    def endThreads(self):
        # Send shutdown message by setting flag
        for thread in self.childThreads:
            thread.endThread()
        # Wait for threads to finish
        while self.threadsRunning:
            # Check thread ending queue
            if not self.shutdownInitQueue.empty():
                msg, name = shutdownInitQueue.get()
                if msg == "THREAD_ENDED":
                    self.threadRunningCount = self.threadRunningCount - 1
                    print(f"Shutdown message received from {name} - waiting on {self.threadRunningCount} more!")
            if self.threadRunningCount == 0:
                self.threadsRunning = False
            time.sleep(1)