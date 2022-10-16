import socket

def run_server():    
    HOST = 'localhost'
    PORT = 8000

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as TCPSocket:
        TCPSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        TCPSocket.bind((HOST, PORT))
        TCPSocket.listen(1)

        print('Server running on: localhost:' + str(PORT))

        while True:    
            client_connection, client_address = TCPSocket.accept()
            
            requestHeader, requestBody = receiveRequest(client_connection)
            print(requestHeader, requestBody)

            response = 'HTTP/1.1 302 Found\r\nLocation: http://httpbin.org/status/418'
            client_connection.sendall(response.encode())
            client_connection.close()


def receiveRequest(socket):
    BUFFER_SIZE = 1024
    response = b''

    # Reads data in packets of length BUFFER_SIZE from the kernel buffer
    while True:
        packet = socket.recv(BUFFER_SIZE)
        response += packet
        if len(packet) < BUFFER_SIZE: break   # Last packet
    
    response = response.decode('utf-8')

    # If responseBody does not exists
    if response.count('\r\n\r\n') < 1:
        return response, ""
    
    else:
        responseHeader, responseBody = response.split('\r\n\r\n', 1)
        return responseHeader, responseBody


run_server()