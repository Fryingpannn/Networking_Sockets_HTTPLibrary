import socket
from packet import Packet
from urllib.parse import urlparse

class HTTPLibrary:

    def __init__(self): 
        self.curr_seq_num = 0
        self.router_addr = 'localhost'
        self.router_port = 3000
        
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

            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as UDPSocket:
                
                # Implement 3 way handshake
                # UDPSocket.connect((HOST, PORT))

                requestData = self.__prepareRequest(HOST, HTTP_METHOD, PATH, HEADERS, BODY_DATA)    
                
                self.__convertToPacketsAndSendToServer(socket, requestData, HOST, PORT)
                
                # Receive response
                responseHeader, responseBody = self.__receiveResponse(UDPSocket)

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


    '''
        Internal Method 
        Description: Receives the response from the socket
        Return: responseHeader, responseBody

        Note: Splits the Header and Body using the '\r\n\r\n' delimiter
    '''
    def __receiveResponse(self, socket):
        BUFFER_SIZE = 1024
        response = b''

        '''Reads data in packets of length BUFFER_SIZE from the kernel buffer'''
        while True:
            packet = socket.recv(BUFFER_SIZE)
            response += packet
            if len(packet) < BUFFER_SIZE: break   # Last packet
        
        response = response.decode('utf-8')

        '''If responseBody does not exists'''
        if response.count('\r\n\r\n') < 1:
            return response, ""
        
        else:
            responseHeader, responseBody = response.split('\r\n\r\n', 1)
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


    def __convertToPacketsAndSendToServer(socket, requestData, server_ip, server_port):

        router_addr = 'localhost'
        router_port = 3005
        curr_seq_num = 0
        
        packet = Packet(packet_type=0,
                        seq_num = curr_seq_num,
                        peer_ip_addr = server_ip,
                        peer_port = server_port,
                        payload = requestData)

        socket.sendto(packet.to_bytes(), (router_addr, router_port))

        pass