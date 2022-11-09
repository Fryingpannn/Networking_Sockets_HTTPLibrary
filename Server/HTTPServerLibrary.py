import socket
from FileHandler import FileHandler

'''
    PORT:       Integer     > Port to connect to
    DIRECTORY:  String      > Directory to use
    VERBOSE:    Boolean     > Print debugging information 
'''

class HTTPServerLibrary:
    def startServer(PORT, DIRECTORY, VERBOSE):

        fileHandler = FileHandler()
        fileHandler.setDefaultDirectory(DIRECTORY)

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:

            server_socket.bind(('localhost', PORT))
            server_socket.listen(1)

            while True:    
                # Wait for client connections
                client_connection, client_address = server_socket.accept()

                # Get the client request
                request = client_connection.recv(1024).decode()
                print(request)

                # Send HTTP response
                response = 'HTTP/1.0 200 OK\n\nHello World'
                client_connection.sendall(response.encode())
                client_connection.close()