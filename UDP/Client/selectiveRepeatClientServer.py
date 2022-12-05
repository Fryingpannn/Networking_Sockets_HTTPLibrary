'''
Selective Repeat Receiver Class

This class is responsible for receiving packets from the sender and sending back ACKs to the sender.
'''
from threading import Lock, Thread
from collections import OrderedDict
import heapq
from packet import Packet
import time
from typing import List, Tuple, OrderedDict
from packetType import PacketType
import socket
import ipaddress

# Types
SeqNumber = int
PacketStore = OrderedDict[SeqNumber, Packet]
BufferHeap = List[Tuple[SeqNumber, Packet]]

'''
Function 1: process_packet
- Checks if packet type is Data + seq number is in window (if not, ignore packet)
- If packet is in window, check if packet is already ACKed (if so, ignore packet)
- If packet is not ACKed
    - Track this packet as ACK'ed in server dictionary
    - store packet in buffer heap and send ACK back to sender with same seq number

Function 2: process_window
- While TRUE:
    - If buffer heap is empty or top of buffer heap is not the next expected seq number (== leftmost window index):
        - time.sleep(1)
    - Else:
        - Pop top of buffer heap and send it to upper layer to process payload
        - Increase window

IGNORE THIS FOR NOW
Note: normally, I think the total number of packets an original packet has been separated into must also be sent from the client. Otherwise,
      it isn't possible to know when to stop and reconstruct the entire packet before processing it. Thus, this total packet value we currently
      use is 1. If a packet is split into 3 packets, the total packet value will be 3.
      This refers to the variables 'self.packet_count' in this class, and 'total_packet_count' in the UDPRequest class.
'''
class SRReceiver:
    
    def __init__(self, socket, append_packet_payload, HOST, PORT, router: Tuple[str,str]=('127.0.0.1','3000'), window_size=1, VERBOSE=False, seq_nb=2147483648):
        self.LOCK = Lock()
        self.packets: PacketStore = OrderedDict()
        self.window_size = window_size
        self.MAX_SEQ_NB = seq_nb
        # left and right index of window (r is exclusive)
        self.l, self.r = 0, self.window_size
        # router
        self.router: Tuple[str,str] = router
        # destination host and port
        self.HOST = HOST
        self.PORT = PORT
        self.socket = socket
        # Function from parent class to send packet payload to upper layer
        self.append_packet_payload = append_packet_payload
        # Buffer heap
        self.buffer: BufferHeap = []
        self.VERBOSE = VERBOSE
        self.packet_count = 0
        self.loop = True
    
    '''
    Function 1: process_packet
    - Checks if packet type is Data + seq number is in window (if not, ignore packet)
    - If packet is in window, check if packet is already ACKed (if so, ignore packet) -> edit: no need to check if acked
    - If packet is not ACKed
        - Track this packet as ACK'ed in server dictionary
        - store packet in buffer heap and send ACK back to sender with same seq number
    '''
    def process_packet(self, packet: Packet):
        # Check if packet is in window and have not been received already (duplicate)
        #if packet.seq_num < self.l or packet.seq_num >= self.r or packet.seq_num in self.packets:
            #return
        if packet.seq_num in self.packets:
            return

        # Store packet in buffer heap and mark as received
        with self.LOCK:
            self.packets[packet.seq_num] = packet
            heapq.heappush(self.buffer, (packet.seq_num, packet))
            # ACK
            ack_packet = Packet(packet_type = PacketType.ACK.value,
                            seq_num = packet.seq_num,
                            peer_ip_addr = ipaddress.ip_address(socket.gethostbyname(self.HOST)),
                            peer_port = self.PORT,
                            payload = "")
            # Send ACK
            self.socket.sendto(ack_packet.to_bytes(), self.router)
        if self.VERBOSE: print("ACK sent for seq#:", packet.seq_num)
    
    def start(self):
        # Start the process_window function on a separate thread
        window_thread = Thread(target=self.__process_window)
        window_thread.start()
        return window_thread

    '''
    Function 2 (New thread): process_window
    - While TRUE:
        - If buffer heap is empty or top of buffer heap is not the next expected seq number (== leftmost window index):
            - time.sleep(1)
        - Else:
            - Pop top of buffer heap and send it to upper layer to process payload
            - Increase window
    '''
    def __process_window(self):
        while self.loop:
            if not self.buffer or self.buffer[0][0] != self.l:
                time.sleep(1)
                continue

            # Pop packet from buffer heap
            with self.LOCK:
                _, packet = heapq.heappop(self.buffer)
                # Send packet payload to upper layer
                self.append_packet_payload(packet)
                self.packet_count += 1
                # Increase window
                self.l += 1
                self.r += 1 
    
    '''
    Function 3: reset_sequence
    - This function is called when the HTTPServerLibrary has finished processing the request and sending back the response.
      This function will reset the sequence number to 0, reset the window pointers l and r, and clear the buffer heap.
    '''
    def stop(self):
        self.next_seq_nb = 0
        self.l, self.r = 0, self.window_size
        self.buffer = []
        self.packets = OrderedDict()
        self.loop = False
    
    def get_packet_count(self):
        return self.packet_count