from email.header import Header
import socket


class HTTPLibrary:

    def __init__(self):
        self.PORT = 80
        
    '''
    Description: Send a HTTP request via a TCP socket

    Method Parameters
        HOST: The host to send the request to. Should not include the protocol, only the domain names
        HTTP METHOD
        PATH: String
        QUERY_PARAMS: String
        VERBOSE: Boolean
        BODY_DATA
        HEADERS: An array of strings formatted as 'k:v'. Example: ['Content-Length: 17', 'User-Agent: Concordia-HTTP/1.0']
    '''
    def sendHTTPRequest(self, HOST, HTTP_METHOD, PATH = "/", HEADERS = [], BODY_DATA = None, VERBOSE = False, OUTPUT_FILE = None):
            # re-directional url parse to domain?
            if PATH == "":
                PATH = "/"
            
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as TCPSocket:
                
                TCPSocket.connect((HOST, self.PORT))

                request = self.__prepareRequest(HOST, HTTP_METHOD, PATH, HEADERS, BODY_DATA)    
                TCPSocket.sendall(request)
                responseHeader, responseBody = self.__receiveResponse(TCPSocket)

                if (self.__responseHeaderContainsRedirection(responseHeader)):
                    redirectionDomain = self.__findRedirectionDomain(responseHeader)

                    if redirectionDomain == "":
                        print("Received 302 response code but didn't find the redirection URL")
                        return 

                    self.sendHTTPRequestself(redirectionDomain, HTTP_METHOD, PATH, HEADERS, BODY_DATA, VERBOSE, OUTPUT_FILE)

                else:
                    if OUTPUT_FILE is not None:
                        file = open(OUTPUT_FILE, "w")
                        file.write(responseBody)
                        file.close()
                    
                    if VERBOSE:
                        print(responseHeader)
                    
                    if OUTPUT_FILE is None:
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

        while True:
            data = socket.recv(BUFFER_SIZE)
            response += data
            if len(data) < BUFFER_SIZE: break
        
        response = response.decode('utf-8')

        # Add check if responseBody does not exists
        responseHeader, responseBody = response.split('\r\n\r\n', 1)


        return responseHeader, responseBody


    def __responseHeaderContainsRedirection(self, responseHeaderString):
        HEADERS = responseHeaderString.split('\r\n')
        return '302' in HEADERS[0]


    def __findRedirectionDomain(self, responseHeaderString):
        HEADERS = responseHeaderString.split('\r\n')

        for HEADER in HEADERS:
            if 'location' in HEADER.lower():
                key, value = HEADER.split(':')
                return value.strip()
        
        return ""