import socket
import threading
import ipaddress
from queue import Queue
from http.client import responses
from FileHandler import FileHandler
from packet import Packet
from packetType import PacketType
from selectiveRepeatServer import SRReceiver

'''
    PORT:       Integer     > Port to connect to
    DIRECTORY:  String      > Directory to use
    VERBOSE:    Boolean     > Print debugging information 
'''

class HTTPServerLibrary:

    def __init__(self): 
        # A dictonary that maps a thread to a unique client request
        self.threadMap = {}

    def startServer(self, PORT, DIRECTORY = "Data", VERBOSE = False):
        if not DIRECTORY: 
            DIRECTORY = "Data"

        if VERBOSE: print("[Verbose mode is on]\n")
       
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server_socket:
            server_socket.bind(('localhost', PORT))
            
            while True:
                # Note: sender will always be the router, so it is useless 
                data, sender = server_socket.recvfrom(1024)
                
                packet = Packet.from_bytes(data)
                sourceAddress = str(packet.peer_ip_addr) + ':' + str(packet.peer_port)
                total_packets = 1

                # Create a thread for this new connection
                if sourceAddress not in self.threadMap:
                    new_thread = UDPRequest(DIRECTORY, server_socket, packet.peer_ip_addr, packet.peer_port, total_packets, 1, VERBOSE)
                    self.threadMap[sourceAddress] = new_thread
                    new_thread.start()

                # Push data for this new connection
                self.threadMap[sourceAddress].queue.put(packet)


class UDPRequest(threading.Thread):
    def __init__(self, directory, connection_socket, clientIPAddress, clientPort, total_packets, window_size=1, verbose=False):
        threading.Thread.__init__(self)

        self.queue = Queue()
        self.fileHandler = FileHandler()
        self.curr_seq_num = 0
        self.router_addr = 'localhost'
        self.router_port = 3000

        self.verbose = verbose
        self.connection_socket = connection_socket
        self.clientIPAddress = clientIPAddress
        self.clientPort = clientPort

        self.requestPayload = ''
        self.fileHandler.setDefaultDirectory(directory)
        self.receiver = SRReceiver(self.connection_socket, self.append_packet_payload, self.clientIPAddress,\
                                     self.clientPort, (self.router_addr, self.router_port), window_size, VERBOSE=verbose)
        # Total number of packets segmented from original packet. Used to determine if all packets have been received
        # Ideally, this value should be sent from the client within the first packet.
        self.total_packets = total_packets

    def run(self):
        MAX_PAYLOAD_SIZE = 1013
        self.receiver.start()

        packet_count = 0
        while True:
            packet = self.queue.get()
            packetType = PacketType(packet.packet_type)

            if packetType == PacketType.SYN:
                self.__handleHandshake()

            elif packetType == PacketType.DATA:
                packet_count += 1
                # Selective repeat
                self.receiver.process_packet(packet)

                # Stay if current packet not processed/ACK'd yet
                while True: 
                    if self.receiver.get_packet_count() >= packet_count: break 

                # All packets received, break
                if self.has_no_more_packets(): break
                # Last packet
                #if len(self.requestPayload) < MAX_PAYLOAD_SIZE: break


        '''If requestBody does not exists'''
        if self.requestPayload.count('\r\n\r\n') < 1:
            responseHeader, responseBody = self.requestPayload, ""
        
        else:
            responseHeader, responseBody = self.requestPayload.split('\r\n\r\n', 1)
        

        self.__handleRequest(responseHeader, responseBody)
    
    def append_packet_payload(self, packet):
        self.requestPayload += packet.payload.decode("utf-8")
    
    def has_no_more_packets(self):
        return self.receiver.get_packet_count() == self.total_packets

    def __handleHandshake(self):
            # SYN
            print("SYN request received")
            
            # SYN-ACK
            print("Sending SYN-ACK...")
            packet = Packet(packet_type = PacketType.SYN.value,
                            seq_num = 0,
                            peer_ip_addr = ipaddress.ip_address(socket.gethostbyname(self.clientIPAddress)),
                            peer_port = self.clientPort,
                            payload = "")

            self.connection_socket.sendto(packet.to_bytes(), (self.router_addr, self.router_port))


    def __handleRequest(self, requestHeader, requestBody):
        if self.verbose:
            print('Request from: ', self.clientIPAddress, self.clientPort)
            print('Request Data: ', requestHeader.strip(), requestBody.strip())
            print('\n')

        # Mimicking slow response
        # time.sleep(10)

        filehandlerResponse = self.__processRequest(requestHeader, requestBody)
        response = self.__prepareResponse(filehandlerResponse)

        if self.verbose:
            print('Response Data: ', response)
            print('\n')
        
        self.__convertToPacketsAndSend(response, PacketType.DATA)


    '''
        Processes a incoming request.
        1) Parses the HTTPHeader and extracts the METHOD and PATH
        2) Call the respective fileHandler method depending on the METHOD and PATH
    '''
    def __processRequest(self, requestHeader, requestBody):

        HEADERS = requestHeader.split('\r\n')
        HTTP_META_INFORMATION = HEADERS[0].split(' ')

        METHOD = HTTP_META_INFORMATION[0].strip()
        PATH = HTTP_META_INFORMATION[1].strip()

        if METHOD != 'GET' and METHOD != 'POST':
            return {
                'statusCode': 405,
                'data': 'HTTP Method not supported: ' + METHOD
            }
        
        if METHOD == 'GET':
            if PATH == '/':
                return self.fileHandler.getNamesOfAllFiles()
            
            else:
                return self.fileHandler.getFileContent(PATH[1:])
        
        else:
            if PATH == '/':
                return {
                    'statusCode': 400,
                    'data': 'FileName is null'
                }
            
            else:
                return self.fileHandler.writeToFile(PATH[1:], requestBody)


    def __prepareResponse(self, RESPONSEDATA):

        STATUS_CODE = RESPONSEDATA.get('statusCode')
        HEADERS = RESPONSEDATA.get('headers', [])
        BODY = RESPONSEDATA.get('data', "")

        request = ''

        request += 'HTTP/1.0 '
        request += str(STATUS_CODE) + ' ' + responses[STATUS_CODE]
        
        for HEADER in HEADERS:
            request += '\r\n' + HEADER

        request += '\r\n\r\n'
        request += BODY

        request += '\r\n'

        return request.encode()


    '''
        Internal Method:
            Takes in the application level payload and transform it into a 1024 byte UDP datagram
            The first 11 bytes of the datagram are UDP headers
            The remaining 1013 bytes is for the application level payload
    '''
    def __convertToPacketsAndSend(self, requestData, packet_type):
        
        for chunk in self.__chunkstring(requestData, 1013):
            packet = Packet(packet_type = packet_type.value,
                            seq_num = self.curr_seq_num,
                            peer_ip_addr = ipaddress.ip_address(socket.gethostbyname(self.clientIPAddress)),
                            peer_port = self.clientPort,
                            payload = chunk)

            self.connection_socket.sendto(packet.to_bytes(), (self.router_addr, self.router_port))
            self.curr_seq_num += 1

        # Implement Selective Repeat with ACK and timeouts


    def __chunkstring(self, string, length):
        return (string[0+i:length+i] for i in range(0, len(string), length))