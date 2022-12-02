import threading
import time
from queue import Queue


class myThread (threading.Thread):
    def __init__(self, threadID):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.queue = Queue()

    def run(self):
        while True:
            val = self.queue.get()
            print("ThreadID: ", threading.get_native_id(), " : " ,val)
            time.sleep(5)

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

threadDict["1"].queue.put("Hello ")
threadDict["1"].queue.put("Smit ")
threadDict["2"].queue.put("Hello ")
threadDict["1"].queue.put("Desai ")
threadDict["2"].queue.put("World ")
