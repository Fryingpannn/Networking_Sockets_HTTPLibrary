import socket

HOST = "www.httpbin.org"
request = b'''GET /status/418 HTTP/1.1\r\nHost: httpbin.org\r\n\r\n'''

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((HOST, 80))
sock.sendall(request)
response = sock.recv(10000)
sock.close()
print('Data: '+response.decode())

'''
    1) Establish a TCP connection using the URL domain name
'''