import socket
import ipaddress
from urllib.parse import urlparse
from packet import Packet
from packetType import PacketType
from selectiveRepeat import SRSender
from selectiveRepeatClientServer import SRReceiver

class HTTPClientLibrary:

    def __init__(self): 
        self.curr_seq_num = 0
        self.router_addr = 'localhost'
        self.router_port = 3000
        self.sender = None
        self.sender_thread = None
        self.receiver = None
        self.response = ''
        
    '''
    Description: Send a HTTP request via a TCP socket

    Method Parameters
        HOST: The host to send the request to. Should not include the protocol, only the domain names
        HTTP_METHOD
        PATH: String
        HEADERS: An array of strings formatted as 'k:v'. Example: ['Content-Length: 17', 'User-Agent: Concordia-HTTP/1.0']
        BODY_DATA
        VERBOSE: Boolean
        OUTPUT_FILE
    '''
    def sendHTTPRequest(self, HOST, HTTP_METHOD, PATH = "/", HEADERS = [], BODY_DATA = None, VERBOSE = False, OUTPUT_FILE = None):
            if PATH == "":
                PATH = "/"
            
            '''Contains PORT number'''
            if HOST.count(":") == 1:
                HOST, PORT = HOST.split(":")
                PORT = int(PORT)
            else:
                PORT = 80

            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client_socket:
                # 3-way handshake
                self.__handshake(client_socket, HOST, PORT)

                # Selective repeat sender and receiver
                self.sender = SRSender(client_socket, (self.router_addr, self.router_port))
                self.receiver = SRReceiver(client_socket, self.append_packet_payload, HOST, PORT, \
                    (self.router_addr, self.router_port), 1, VERBOSE)

                requestData = self.__prepareRequest(HOST, HTTP_METHOD, PATH, HEADERS, BODY_DATA)    
                self.__convertToPacketsAndSend(client_socket, requestData, PacketType.DATA, HOST, PORT)
   
                # Receive response
                responseHeader, responseBody = self.__receiveResponse(client_socket)

                '''Check if the response is 302: redirect'''
                if (self.__responseHeaderContainsRedirection(responseHeader)):
                    redirectURL = self.__findRedirectURL(responseHeader)

                    if redirectURL == "":
                        print("Received 302 response code but didn't find the redirection URL")
                        return 

                    '''
                    The redirectURL will of form http://example.com:PORT/path
                    So need to parse out the Domain + Port and the Path + QueryParams
                    '''
                    parsedRedirectURL = urlparse(redirectURL)
                    self.sendHTTPRequest(parsedRedirectURL.netloc, HTTP_METHOD, parsedRedirectURL.path, HEADERS, BODY_DATA, VERBOSE, OUTPUT_FILE)

                else:
                    if VERBOSE:
                        print(responseHeader)

                    if OUTPUT_FILE is not None:
                        file = open(OUTPUT_FILE, "w")
                        file.write(responseBody)
                        file.close()
                    
                    else:
                        print(responseBody)

    '''
        Internal Method
        Description: Prepares the HTTP request data to sent from the socket
        Returns: String containing the requestHeader and requestBody encoded into bytes

        Note: 
                - Each line must be seperated by the '\r\n' delimiter
                - Body must be seperated by an extra '\r\n' delimiter
                - Body requires the Content-length Header
                - The request must end with an extra '\r\n' delimiter
    '''
    def __prepareRequest(self, HOST, HTTP_METHOD, PATH, HEADERS, BODY_DATA):
        request = ''
        
        request += HTTP_METHOD + " " + PATH + " HTTP/1.1\r\n"
        request += "Host: " + HOST + "\r\n"

        for HEADER in HEADERS:
            request += HEADER + "\r\n"

        if BODY_DATA is not None:
            request += "Content-Length: " + str(len(BODY_DATA)) + "\r\n"
            request += "\r\n"
            request += BODY_DATA + "\r\n"

        request += "\r\n"
        return request.encode()

    def append_packet_payload(self, packet):
        self.response += packet.payload.decode("utf-8")

    '''
        Internal Method 
        Description: Receives the response from the socket
        Return: responseHeader, responseBody

        Note: Splits the Header and Body using the '\r\n\r\n' delimiter
    '''
    def __receiveResponse(self, socket):
        BUFFER_SIZE = 1024
        PAYLOAD_SIZE = 1013
        receiver_thread = self.receiver.start()
        packet_count = 0

        '''Reads data in packets of length BUFFER_SIZE from the kernel buffer'''
        while True:
            byteData, sender = socket.recvfrom(BUFFER_SIZE)
            packet = Packet.from_bytes(byteData)

            # ACK packet
            if packet.packet_type == PacketType.ACK.value:
                self.sender.ACK_received(packet)
                print('ACK received')
                continue

            # Selective repeat: if packet type is DATA, send ACK
            if packet.packet_type == PacketType.DATA.value:
                self.receiver.process_packet(packet)
                packet_count += 1
                #print('Starting loop')           
                while True: 
                    if self.receiver.get_packet_count() >= packet_count: break 
            #print('Finished loop')
            #self.response += packet.payload
            if len(packet.payload) < PAYLOAD_SIZE:
                self.sender.stop()
                # self.receiver.stop()
                #self.sender_thread.join()
                # receiver_thread.join()
                break   # Last packet
        
        #self.response = self.response.decode('utf-8')

        '''If responseBody does not exists'''
        if self.response.count('\r\n\r\n') < 1:
            return self.response, ""
        
        else:
            responseHeader, responseBody = self.response.split('\r\n\r\n', 1)
            return responseHeader, responseBody


    def __responseHeaderContainsRedirection(self, responseHeaderString):
        HEADERS = responseHeaderString.split('\r\n')
        return '302' in HEADERS[0]


    def __findRedirectURL(self, responseHeaderString):
        HEADERS = responseHeaderString.split('\r\n')

        '''Find the Location header and get the redirect URL'''
        for HEADER in HEADERS:
            if 'location' in HEADER.lower():
                key, value = HEADER.split(':', 1)                
                return value.strip()
                
        return ""


    def __handshake(self, connection_socket, server_addr, server_port):
        HANDSHAKE_CONNECTION_TIMEOUT = 2.0  # In seconds

        print("Initiating handshake....")

        # SYN
        packet = Packet(packet_type = PacketType.SYN.value,
                        seq_num = 0,
                        peer_ip_addr = ipaddress.ip_address(socket.gethostbyname(server_addr)),
                        peer_port = server_port,
                        payload = "")
        
        connection_socket.sendto(packet.to_bytes(), (self.router_addr, self.router_port))
        print("SYN sent")

        # SYN-ACK
        try:
            # Set timeout, if not received within timeout, send hanshake again
            connection_socket.settimeout(HANDSHAKE_CONNECTION_TIMEOUT)
            byteData, sender = connection_socket.recvfrom(1024)
            packet = Packet.from_bytes(byteData)

            connection_socket.settimeout(None)
            print("SYN-ACK received")
        
        except socket.timeout:
            print("SYN-ACK timeout. Restarting handshake...")
            self.__handshake(connection_socket, server_addr, server_port)
            return


        # ACK
        packet = Packet(packet_type = PacketType.ACK.value,
                        seq_num = 0,
                        peer_ip_addr = ipaddress.ip_address(socket.gethostbyname(server_addr)),
                        peer_port = server_port,
                        payload = "")

        connection_socket.sendto(packet.to_bytes(), (self.router_addr, self.router_port))
        print("ACK sent")

        print("Handshake complete\n")


    '''
        Internal Method:
            Takes in the application level payload and transform it into a 1024 byte UDP datagram
            The first 11 bytes of the datagram are UDP headers
            The remaining 1013 bytes is for the application level payload
    '''
    def __convertToPacketsAndSend(self, connection_socket, requestData, packet_type, server_addr, server_port):
        
        packets = []
        for chunk in self.__chunkstring(requestData, 1013):
            packet = Packet(packet_type = packet_type.value,
                            seq_num = self.curr_seq_num,
                            peer_ip_addr = ipaddress.ip_address(socket.gethostbyname(server_addr)),
                            peer_port = server_port,
                            payload = chunk)

            packets.append(packet)
            # connection_socket.sendto(packet.to_bytes(), (self.router_addr, self.router_port))
            # self.curr_seq_num += 1
        
        self.sender_thread = self.sender.store_and_send_packets(packets)

    # Function to ACK server data packets
    def __sendACK(self, connection_socket, requestData, packet_type, server_addr, server_port):
        
        packets = []
        for chunk in self.__chunkstring(requestData, 1013):
            packet = Packet(packet_type = PacketType.ACK.value,
                            seq_num = self.curr_seq_num,
                            peer_ip_addr = ipaddress.ip_address(socket.gethostbyname(server_addr)),
                            peer_port = server_port,
                            payload = chunk)

            packets.append(packet)
            # connection_socket.sendto(packet.to_bytes(), (self.router_addr, self.router_port))
            self.curr_seq_num += 1
        
        self.receiver.process_packet(packet)

    def __chunkstring(self, string, length):
        return (string[0+i:length+i] for i in range(0, len(string), length))
