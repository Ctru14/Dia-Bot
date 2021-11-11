import sys
import time
import math
import threading
import multiprocessing


class DiaThread():
    
    def __init__(self, name, useProcess, globalStartTime, shutdownQueue, freqHz, loopFunction, *args):
        self.threadsList = []
        self.globalStartTime = globalStartTime
        self.threadRunning = False
        self.threadEnded = False
        self.shutdownQueue = shutdownQueue
        self.endThreadQueue = multiprocessing.Queue()
        self.loopFreq = freqHz
        self.loopTIme = 1/freqHz
        self.name = name
        print(f"Create and add new loop thread: {loopFunction.__name__}")
        if useProcess:
            self.thread = multiprocessing.Process(target=self.loopAtFrequency, args=(freqHz, self.endThreadQueue, loopFunction, args))
        else:
            self.thread = threading.Thread(target=self.loopAtFrequency, args=(freqHz, self.endThreadQueue, loopFunction, args))
            

    # Wrapper to other functions which loops 
    def loopAtFrequency(self, freqHz, endThreadQueue, loopFunction, *args):
        print(f"Starting thread {self.name} with args {args} (len {len(args)}) at {freqHz} Hz")
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
            if not endThreadQueue.empty():
                msg = endThreadQueue.get()
                print(f"EndThreadQueue msg: {msg}")
                if msg == "END_THREAD":
                    self.threadRunning = False
                    break
        self.threadEnded = True
        self.shutdownQueue.put("THREAD_ENDED")
        print(f"Loop ended! {self.name}")
        
    def startThread(self):
        self.threadRunning = True
        self.thread.start()

    def endThread(self):
        print(f"Ending thread! {self.name}")
        self.threadRunning = False
        self.endThreadQueue.put("END_THREAD")
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
        return self.thread.terminate()
