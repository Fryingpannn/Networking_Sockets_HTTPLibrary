'''
Selective Repeat Program
- Run this on seperate thread
- The final packet will be sent here
- This acts as "link layer" but uses UDP function to send. (Selective repeat is a link layer protocol)
'''
import asyncio
from threading import Lock, Thread
from collections import OrderedDict
from packet import Packet
import time

# Selective Repeat Sender
class SRSender:
    def __init__(self, socket, destination=('127.0.0.1','3000'), timeout=2.0, seq_nb=2147483648, window_size=1):
        self.LOCK = Lock()
        # max should be 2^(m-1), m being # of bits in header for seq nb
        self.MAX_SEQ_NB = seq_nb
        # {
        #   seq nb : (packet, 
        #           0 or 1 depending on ACK or unACK,
        #           0 or 1 depending on not sent or sent,
        #           time the packet was sent, 0 by default
        # }
        # dictionary add actions need to be self.LOCKed to be thread safe
        self.packets = OrderedDict()
        self.window_size = window_size
        # left and right index of window (r is exclusive)
        self.l, self.r = 0, self.window_size
        self.next_seq_nb = 0
        self.destination = destination
        self.timeout = timeout
        self.socket = socket
    
    # This function should be called after the socket has been opened
    def start(self):
        # Start the process_window function on a separate thread
        window_thread = Thread(target=self.__process_window)
        window_thread.start()
        
    # The "__convertToPacketsAndSend" function should call this function and send in the packet to be delivered.
    # This will store the packet in the sequence window and processed by the 'process_window' function.
    def store_packet(self, new_packet: Packet):
        # get next packet from transport/network layer
        with self.LOCK:
            self.packets[self.next_seq_nb] = (new_packet, 0)
            self.next_seq_nb += 1

    # This function needs to be run on a separate thread continuously as it takes care
    # of the sequence window.
    def __process_window(self):
        # Q: When to stop? Maybe constructor needs to input total number of packets that will be sent
        #    since current max sequence nb is so large. When all done, return all the packets in the dictionary.
        while True:
            # If no packets yet or all packets have been sent
            if self.next_seq_nb == 0 or self.r > self.MAX_SEQ_NB:
                time.sleep(1)
                continue

            # If oldest packet ACKed, advance window
            if self.packets.get(self.l, None) is None: continue
            if self.packets[self.l][1] == 1:
                self.l += 1
                self.r += 1

            # For every unACKed and not sent packet in window,
            # asynchronously send packet
            for i in range(self.l, self.r):
                packet = self.packets.get(i, None)
                if packet is None: break
                # If packet is ACKed already
                if packet[1] == 1: continue

                # If packet sent, but timed out
                if packet[2] == 1 and time.time() > (packet[3] + self.window_timeout):
                    # Set packet to unsent and reset timeout
                    packet[2] = 0
                    packet[3] = 0
                # If packet unsent, send it
                if packet[2] == 0:
                    with self.LOCK:
                        # Start timeout timer for this packet
                        self.packets[self.next_seq_nb][3] = time.time()
                    self.socket.sendto(packet[0], self.destination)
                    # Ignore: elf.async_send(self.next_seq_nb, packet[0], self.destination)
    
    # Function to ACK packet with seq nb (client and server should have same seq nb for same packet)
    def ACK_received(self, packet: Packet):
        with self.LOCK:
            self.packets[packet.seq_nb] = (packet, 1, 1, 0)

    # Ignore:
    # Need to use asyncio library (or maybe just new thread)
    # https://docs.python.org/3/library/asyncio-runner.html#asyncio.run
    # def async_send(self, seq_nb, packet, destination):
    #     '''
    #     2 WAYS:
    #         1. open new socket with timeout (seconds in float)
    #         2. keep same socket, just put regular function timeout	
    #     '''
    #     with self.LOCK:
    #         # Store the starting time of this packet being sent
    #         self.packets[seq_nb][3] = time.time()
    #         self.socket.sendto(packet, destination)