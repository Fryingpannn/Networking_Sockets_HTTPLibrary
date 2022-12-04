'''
Selective Repeat Program
- Run this on seperate thread
- The final packet will be sent here
- This acts as "link layer" but uses UDP function to send. (Selective repeat is a link layer protocol)
'''
from threading import Lock, Thread
from collections import OrderedDict
from packet import Packet
import time
from typing import List, Tuple, OrderedDict

# Types
ACKType = str
SentType = str
StartTime = int
SeqNumber = int
PacketStore = OrderedDict[SeqNumber, List[Packet | ACKType | SentType | StartTime]]

# Selective Repeat Sender
'''
There are three main functions.

1. store_and_send_packets
- Used by outer class to store packets in SRSender's packet store. This stores a list of packets and gives each of them a
  sequence number in order. Then calls to start the process_window function on a separate thread.

2. process_window
- This function iterates over the defined window size of number of packets previously stored and sends them to the server.
  It loops back on this window to check if the first element of that window has been ACKed, if so, it moves the window
  forward until the all packets have been ACKed. In this class, we use a dictionary to keep track of which packets have
  been ACKed, as well as their sent status, and time when sent. Using this, we resend packets that timeout, and avoid
  resending packets that have been ACked already.

3. ACK_received
- This function ACKs a specific packet by setting the ACK value in the packet store to 'ACK'. This is called by the HTTP library.
'''
class SRSender:
    def __init__(self, socket, destination: Tuple[str,str]=('127.0.0.1','3000'), timeout=3.0, seq_nb=2147483648, window_size=1):
        self.LOCK = Lock()
        # max should be 2^(m-1), m being # of bits in header for seq nb
        self.MAX_SEQ_NB = seq_nb
        # {
        #   seq nb :[
        #               packet, 
        #               0 or 1 depending on ACK or unACK,
        #               0 or 1 depending on not sent or sent,
        #               time the packet was sent, 0 by default
        #           ]    
        # }
        # dictionary modify actions need to be self.LOCKed to be thread safe
        self.packets: PacketStore = OrderedDict()
        self.window_size = window_size
        # left and right index of window (r is exclusive)
        self.l, self.r = 0, self.window_size
        self.next_seq_nb = 0
        self.destination: Tuple[str,str] = destination
        self.timeout = timeout
        self.socket = socket
    
    # This function should be called after the socket has been opened
    def __start(self):
        # Start the process_window function on a separate thread
        window_thread = Thread(target=self.__process_window)
        window_thread.start()
        return window_thread
        
    # The "__convertToPacketsAndSend" function should call this function and send in the packet to be delivered.
    # This will store the packet in the sequence window and processed by the 'process_window' function.
    def store_and_send_packets(self, new_packets: List[Packet], set_window_size=1):
        # get next packet from transport/network layer
        self.MAX_SEQ_NB = len(new_packets)
        for i in range(self.MAX_SEQ_NB):
            self.packets[self.next_seq_nb] = [new_packets[i], 0, 0, 0]
            self.next_seq_nb += 1

        self.window_size = set_window_size
        self.l, self.r = 0, self.window_size
        
        # Start sending packets
        return self.__start()

    # This function needs to be run on a separate thread continuously as it takes care
    # of the sequence window.
    def __process_window(self):
        # Q: When to stop? Maybe constructor needs to input total number of packets that will be sent
        #    since current max sequence nb is so large. When all done, return all the packets in the dictionary.
        while True:
            # If no packets yet
            if self.next_seq_nb == 0:
                time.sleep(1)
                continue
            
            # If seq window is finished.
            if self.r >= self.MAX_SEQ_NB:
                # Here it means all packets have at least been sent once.
                # Check if all packets have been ACKed, if so quit function
                with self.LOCK:
                    if all([self.packets[i][1] for i in range(self.MAX_SEQ_NB)]):
                        return True
            else:
                # If oldest packet ACKed, advance window
                if self.packets[self.l][1] == 1:
                    self.l += 1
                    self.r += 1

            # For every unACKed and not sent packet in window,
            # asynchronously send packet
            for i in range(self.l, self.r):
                packet = self.packets.get(i, None)
                if packet is None: break

                with self.LOCK:
                    # If packet is ACKed already
                    if packet[1] == 1: continue

                    # If packet sent, but timed out
                    if packet[2] == 1 and time.time() > (packet[3] + self.timeout):
                        # Set packet to unsent and reset timeout
                        packet[2] = 0
                        packet[3] = 0
                    # If packet unsent, send it
                    if packet[2] == 0:
                        # Start timeout timer for this packet and indicate sent
                        self.packets[i][2] = 1
                        self.packets[i][3] = time.time()
                        self.socket.sendto(packet[0].to_bytes(), self.destination)
    
    # Function to ACK packet with seq nb (client and server should have same seq nb for same packet)
    def ACK_received(self, packet: Packet):
        with self.LOCK:
            self.packets[packet.seq_num] = [packet, 1, 1, 0]
