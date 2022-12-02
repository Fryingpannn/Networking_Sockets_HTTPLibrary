import socket
import threading
import ipaddress
from http.client import responses
from FileHandler import FileHandler
from packet import Packet
from packetType import PacketType

'''
    PORT:       Integer     > Port to connect to
    DIRECTORY:  String      > Directory to use
    VERBOSE:    Boolean     > Print debugging information 
'''

class HTTPServerLibrary:

    def __init__(self): 
        self.threadMap = {}

    def startServer(self, PORT, DIRECTORY = "Data", VERBOSE = False):

        if not DIRECTORY: 
            DIRECTORY = "Data"
       
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server_socket:
            server_socket.bind(('localhost', PORT))
            
            while True:
                data, sender = server_socket.recvfrom(1024)
                
                packet = Packet.from_bytes(data)
                sourceAddress = str(packet.peer_ip_addr) + ':' + str(packet.peer_port)

                if sourceAddress not in self.threadMap:
                    new_thread = UDPRequest(DIRECTORY, server_socket, packet.peer_ip_addr, packet.peer_port, VERBOSE)
                    self.threadMap[sourceAddress] = new_thread
                    new_thread.start()

                self.threadMap[sourceAddress].receiveRequest(packet.payload)


class UDPRequest(threading.Thread):
    def __init__(self, directory, connection_socket, peer_ip_addr, peer_port, verbose):
        threading.Thread.__init__(self)

        self.fileHandler = FileHandler()
        self.senders = {}
        self.curr_seq_num = 0
        self.router_addr = 'localhost'
        self.router_port = 3000

        self.verbose = verbose
        self.connection_socket = connection_socket
        self.clientIPAddress = peer_ip_addr
        self.clientPort = peer_port

        self.requestPayload = ''
        self.fileHandler.setDefaultDirectory(directory)

    def receiveRequest(self, payload):
        MAX_PAYLOAD_SIZE = 1013
        self.requestPayload += payload.decode("utf-8")
        
        # Implement Selective Repeat with ACK and buffering
        # close the thread

        # Means more packets are incoming
        if len(self.requestPayload) == MAX_PAYLOAD_SIZE:
            return

        '''If responseBody does not exists'''
        if self.requestPayload.count('\r\n\r\n') < 1:
            responseHeader, responseBody = self.requestPayload, ""
        
        else:
            responseHeader, responseBody = self.requestPayload.split('\r\n\r\n', 1)
        

        self.__handleRequest(responseHeader, responseBody)



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



    # '''
    #     Processes a incoming request.
    #     1) Parses the HTTPHeader and extracts the METHOD and PATH
    #     2) Call the respective fileHandler method depending on the METHOD and PATH
    # '''
    # def __processRequest(self, requestHeader, requestBody):

    #     HEADERS = requestHeader.split('\r\n')
    #     HTTP_META_INFORMATION = HEADERS[0].split(' ')

    #     METHOD = HTTP_META_INFORMATION[0].strip()
    #     PATH = HTTP_META_INFORMATION[1].strip()

    #     filehandlerResponse = None

    #     if METHOD != 'GET' and METHOD != 'POST':
    #         filehandlerResponse = {
    #             'statusCode': 405,
    #             'data': 'HTTP Method not supported: ' + METHOD
    #         }
        
    #     if METHOD == 'GET':
    #         if PATH == '/':
    #             filehandlerResponse = self.fileHandler.getNamesOfAllFiles()
            
    #         else:
    #             filehandlerResponse = self.fileHandler.getFileContent(PATH[1:])
        
    #     else:
    #         if PATH == '/':
    #             filehandlerResponse = {
    #                 'statusCode': 400,
    #                 'data': 'FileName is null'
    #             }
            
    #         else:
    #             filehandlerResponse = self.fileHandler.writeToFile(PATH[1:], requestBody)


    #     self.__prepareResponse(filehandlerResponse)








    # def __handleClient(self, conn, data, sender, VERBOSE=False):
    #     requestHeader, requestBody, client_port, packet_type = self.__receiveResponse(conn, data, sender, VERBOSE)

    #     if VERBOSE: print('Request from: ', sender)

    #     # Mimicking slow response
    #     # time.sleep(10)

    #     filehandlerResponse = self.__processRequest(requestHeader, requestBody)
    #     response = self.__prepareResponse(filehandlerResponse)

    #     if VERBOSE:
    #         print('Response Data: ', response)
    #         print('\n')

    #     self.__convertToPacketsAndSend(conn, response, PacketType.DATA, sender, client_port)

    # def __receiveResponse(self, conn, data, sender, VERBOSE=False):
    #     BUFFER_SIZE = 1024
    #     response = b''

    #     '''Reads data in packets of length BUFFER_SIZE from the kernel buffer'''
    #     packet = 'None'
    #     try:
    #         packet = Packet.from_bytes(data)
    #         if VERBOSE:
    #             print("Router: ", sender)
    #             print("Packet: ", packet)
    #             print("Payload: ", packet.payload.decode("utf-8"))

    #     except Exception as e:
    #         print("Error: ", e)
        
    #     response = packet.payload.decode("utf-8")

    #     '''If responseBody does not exists'''
    #     if response.count('\r\n\r\n') < 1:
    #         return response, ""
        
    #     else:
    #         responseHeader, responseBody = response.split('\r\n\r\n', 1)
    #         return responseHeader, responseBody, packet.peer_port, packet.packet_type


    # '''
    #     Processes a incoming request.
    #     1) Parses the HTTPHeader and extracts the METHOD and PATH
    #     2) Call the respective fileHandler method depending on the METHOD and PATH
    # '''
    # def __processRequest(self, requestHeader, requestBody):

    #     HEADERS = requestHeader.split('\r\n')
    #     HTTP_META_INFORMATION = HEADERS[0].split(' ')

    #     METHOD = HTTP_META_INFORMATION[0].strip()
    #     PATH = HTTP_META_INFORMATION[1].strip()

    #     if METHOD != 'GET' and METHOD != 'POST':
    #         return {
    #             'statusCode': 405,
    #             'data': 'HTTP Method not supported: ' + METHOD
    #         }
        
    #     if METHOD == 'GET':
    #         if PATH == '/':
    #             return self.fileHandler.getNamesOfAllFiles()
            
    #         else:
    #             return self.fileHandler.getFileContent(PATH[1:])
        
    #     else:
    #         if PATH == '/':
    #             return {
    #                 'statusCode': 400,
    #                 'data': 'FileName is null'
    #             }
            
    #         else:
    #             return self.fileHandler.writeToFile(PATH[1:], requestBody)


    # def __prepareResponse(self, RESPONSEDATA):

    #     STATUS_CODE = RESPONSEDATA.get('statusCode')
    #     HEADERS = RESPONSEDATA.get('headers', [])
    #     BODY = RESPONSEDATA.get('data', "")

    #     request = ''

    #     request += 'HTTP/1.0 '
    #     request += str(STATUS_CODE) + ' ' + responses[STATUS_CODE]
        
    #     for HEADER in HEADERS:
    #         request += '\r\n' + HEADER

    #     request += '\r\n\r\n'
    #     request += BODY

    #     request += '\r\n'

    #     return request.encode()

    # '''
    #     Internal Method:
    #         Takes in the application level payload and transform it into a 1024 byte UDP datagram
    #         The first 11 bytes of the datagram are UDP headers
    #         The remaining 1013 bytes is for the application level payload
    # '''
    # def __convertToPacketsAndSend(self, socket, requestData, packet_type, client_ip, client_port):
        
    #     for chunk in self.__chunkstring(requestData, 1013):
    #         packet = Packet(packet_type = packet_type.value,
    #                         seq_num = self.curr_seq_num,
    #                         peer_ip_addr = client_ip[0],
    #                         peer_port = client_port,
    #                         payload = chunk)

    #         socket.sendto(packet.to_bytes(), (self.router_addr, self.router_port))
    #         self.curr_seq_num += 1

    #     # Implement Selective Repeat with ACK and timeouts

    # def __chunkstring(self, string, length):
    #     return (string[0+i:length+i] for i in range(0, len(string), length))