from HTTPLibrary import HTTPLibrary

library = HTTPLibrary()

def Example():
    HOST = "httpbin.org"
    HTTP_METHOD = "GET"
    PATH = "/status/418"
    HEADERS = []
    BODY_DATA = None
    VERBOSE = True

    library.sendHTTPRequest(HOST, HTTP_METHOD, PATH, HEADERS, BODY_DATA, VERBOSE)

def Get_With_Query_Params():
    HOST = "httpbin.org"
    HTTP_METHOD = "GET"
    PATH = "/get?course=networking&assignment=1"
    HEADERS = []
    BODY_DATA = None
    VERBOSE = True

    library.sendHTTPRequest(HOST, HTTP_METHOD, PATH, HEADERS, BODY_DATA, VERBOSE)

def Post_With_Inline_Data():
    HOST = "httpbin.org"
    HTTP_METHOD = "POST"
    PATH = "/post"
    HEADERS = ["Content-Type:application/json"]
    BODY_DATA = '{"Assignment": 1}'
    VERBOSE = True

    library.sendHTTPRequest(HOST, HTTP_METHOD, PATH, HEADERS, BODY_DATA, VERBOSE)

'''Need to run redirectServer.py before testing this method'''
def Redirect():
    HOST = "localhost:8000"
    HTTP_METHOD = "GET"
    PATH = "/"
    HEADERS = []
    BODY_DATA = None
    VERBOSE = True

    library.sendHTTPRequest(HOST, HTTP_METHOD, PATH, HEADERS, BODY_DATA, VERBOSE)


# Example()
# Get_With_Query_Params()
# Post_With_Inline_Data()
Redirect()