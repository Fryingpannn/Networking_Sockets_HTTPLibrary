import socket
from http.client import responses
from FileHandler import FileHandler

'''
    PORT:       Integer     > Port to connect to
    DIRECTORY:  String      > Directory to use
    VERBOSE:    Boolean     > Print debugging information 
'''

class HTTPServerLibrary:

    def __init__(self): 
        self.fileHandler = FileHandler()

    def startServer(self, PORT, DIRECTORY = "Data", VERBOSE = False):

        if not DIRECTORY: DIRECTORY = "Data"
        self.fileHandler.setDefaultDirectory(DIRECTORY)

        #VERBOSE? 
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:

            server_socket.bind(('localhost', PORT))
            server_socket.listen(1)

            while True:    
                client_connection, client_address = server_socket.accept()
                
                requestHeader, requestBody = self.__receiveResponse(client_connection)
                filehandlerResponse = self.__processRequest(requestHeader, requestBody)
                response = self.__prepareResponse(filehandlerResponse['statusCode'], filehandlerResponse['data'])
                
                client_connection.sendall(response)
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


    '''
        Processes a incoming request.
        1) Parses the HTTPHeader and extracts the METHOD and PATH
        2) Call the respective fileHandler method depending on the METHOD and PATH
    '''
    #Things to check:
    # METHOD and PATH are parsed correctly
    # If the Path is empty, is it stored as '/' or '' in the HTTP Header
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


    # HTTP/1.0 200 OK\n\nHello World
    # Do we need any other headers?
    def __prepareResponse(self, STATUS_CODE, BODY):
        request = ''

        request += 'HTTP/1.0 '
        request += str(STATUS_CODE) + ' ' + responses[STATUS_CODE]

        request += '\r\n\r\n'
        request += BODY

        request += '\r\n'
        return request.encode()
