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


# EXTRA

# 2 things can happen now:
# - Either the SYN-ACK gets lost, in that case, the client timeouts and sends SYN again
# - ACK from client gets lost

# try: 
#     packet = self.queue.get(True, HANDSHAKE_CONNECTION_TIMEOUT)
    
#     # This means that SYN-ACK got lost and the client sent another SYN packet
#     if PacketType(packet.packet_type) == PacketType.SYN:
#         print("Received SYN again, restarting the handshake\n")
#         self.__handleHandshake()
#         return

#     self.handshakeCompleted = True
#     print("ACK received")
#     print("Handshake completed\n")
# except:
#     print("Did not receive ACK within timeout, resending the SYN-ACK\n")
#     self.__handleHandshake()