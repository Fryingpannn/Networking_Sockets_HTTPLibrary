import threading

class myThread (threading.Thread):
    def __init__(self, threadID):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.data = ""

    def pushData(self, newData):
        self.data += newData
        print("Received data: ", self.data)

# Create new threads
thread1 = myThread(1)
thread2 = myThread(2)

# Start new Threads
thread1.start()
thread2.start()

threadDict = {
    "1": thread1,
    "2": thread2
}

threadDict["1"].pushData("Hello ")
threadDict["1"].pushData("Smit ")
threadDict["2"].pushData("Hello ")
threadDict["1"].pushData("Desai ")
threadDict["2"].pushData("World ")

print ("Exiting Main Thread")