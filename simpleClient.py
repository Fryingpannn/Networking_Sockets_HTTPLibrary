import HTTPLibrary

def Example():
    HOST = "httpbin.org"
    HTTP_METHOD = "GET"
    PATH = "/status/418"
    QUERY_PARAMS = ""
    HEADERS = []
    BODY_DATA = None
    VERBOSE = False

    HTTPLibrary.sendHTTPRequest(HOST, HTTP_METHOD, PATH, QUERY_PARAMS, HEADERS, BODY_DATA, VERBOSE)

def Get_With_Query_Params():
    HOST = "httpbin.org"
    HTTP_METHOD = "GET"
    PATH = "/get?course=networking&assignment=1"
    QUERY_PARAMS = ""
    HEADERS = []
    BODY_DATA = None
    VERBOSE = False

    HTTPLibrary.sendHTTPRequest(HOST, HTTP_METHOD, PATH, QUERY_PARAMS, HEADERS, BODY_DATA, VERBOSE)

def Post_With_Inline_Data():
    HOST = "httpbin.org"
    HTTP_METHOD = "POST"
    PATH = "/post"
    QUERY_PARAMS = ""
    HEADERS = ["Content-Type:application/json"]
    BODY_DATA = '{"Assignment": 1}'
    VERBOSE = False

    HTTPLibrary.sendHTTPRequest(HOST, HTTP_METHOD, PATH, QUERY_PARAMS, HEADERS, BODY_DATA, VERBOSE)


Example()
Get_With_Query_Params()
Post_With_Inline_Data()