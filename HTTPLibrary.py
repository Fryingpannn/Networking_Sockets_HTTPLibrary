import socket

'''
HOST
PATH
QUERY_PARAMS
VERBOSE
BODY_DATA - To need to look how to send the body data
HTTP METHOD
HEADERS (an array of strings "k:v")
'''

PORT = 8080

def sendHTTPRequest(HOST, HTTP_METHOD, PATH = "/", QUERY_PARAMS = "", HEADERS = None, BODY_DATA = None, VERBOSE = False):
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as TCPSocket:
        TCPSocket.connect((HOST, PORT))

        request = prepareRequest(HOST, HTTP_METHOD, PATH, QUERY_PARAMS, HEADERS, BODY_DATA)    
        TCPSocket.sendall(request)

        receiveHTTPResponse(TCPSocket, VERBOSE)


def prepareRequest(HOST, HTTP_METHOD, PATH, QUERY_PARAMS, HEADERS, BODY_DATA):
    request = ''
    
    request += HTTP_METHOD + " " + PATH + QUERY_PARAMS + " HTTP/1.1\r\n"
    request += "Host: " + HOST + "\r\n"


    # Convert it to binary
    return request

def receiveHTTPResponse(TCPSocket, VERBOSE):
    response = ''

    while True:
        data = TCPSocket.recv(1024)
        if not data:
            break
        
        response += data

    # Need to seperate the response body from resposne headers so
    # What to display if VERBOSE is on?
    response = response.decode('utf-8')