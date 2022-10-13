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

# -H "head: value" -H "head2: value2"
# ["head: value", "head2: value2"]

PORT = 80

def sendHTTPRequest(HOST, HTTP_METHOD, PATH = "/", QUERY_PARAMS = "", HEADERS = [], BODY_DATA = None, VERBOSE = False):
    # does it socket close if receive is used in a different function?
    # - Yes, closes at end of receiveHTTPResponse
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as TCPSocket:
        TCPSocket.connect((HOST, PORT))

        request = prepareRequest(HOST, HTTP_METHOD, PATH, QUERY_PARAMS, HEADERS, BODY_DATA)    
        TCPSocket.sendall(request)

        receiveHTTPResponse(TCPSocket, VERBOSE)


def prepareRequest(HOST, HTTP_METHOD, PATH, QUERY_PARAMS, HEADERS, BODY_DATA):
    request = ''
    
    request += HTTP_METHOD + " " + PATH + QUERY_PARAMS + " HTTP/1.1\r\n"
    request += "Host: " + HOST + "\r\n"

    for HEADER in HEADERS:
        request += HEADER + "\r\n"

    if BODY_DATA is not None:
        # For body data, need content length header: Double check it once

        request += "Content-Length: " + len(BODY_DATA) + "\r\n"
        request += "\r\n"
        request += "{" + BODY_DATA + "}"
        request += "\r\n"

    request += "\r\n"
    return request.encode()


def receiveHTTPResponse(TCPSocket, VERBOSE):
    response = ''

    # while True:
    data = TCPSocket.recv(10240)
        # if not data:
            # break    
    response += data.decode()
    print(response)

    # Need to seperate the response body from resposne headers so
    # What to display if VERBOSE is on?
    # what if response is empty?