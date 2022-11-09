import socket
from FileHandler import FileHandler

'''
    PORT:       String      > Port to connect to
    DIRECTORY:  String      > Directory to use
    VERBOSE:    Boolean     > Print debugging information 
'''

class HTTPServerLibrary:
    def startServer(self, PORT, DIRECTORY = "Data", VERBOSE = False):

        fileHandler = FileHandler()
        fileHandler.setDefaultDirectory(DIRECTORY)

        #VERBOSE? 
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:

            server_socket.bind(('localhost', PORT))
            server_socket.listen(1)

            while True:    
                client_connection, client_address = server_socket.accept()
                requestHeader, requestBody = self.__receiveResponse(client_connection)

                filehandlerResponse = self.__processRequest(requestHeader, requestBody)

                
                response = 'HTTP/1.0 200 OK\n\nHello World'
                client_connection.sendall(response.encode())
                client_connection.close()


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


    def __processRequest(self, requestHeader, requestBody):
