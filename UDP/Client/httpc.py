# -*- coding: utf-8 -*-
'''
Parser for HTTP library

General
- Take in text input from cURL
- Convert to one string that can be input into HTTP library directly

Specifics
- Must check the command options. Not all should exist, also different for GET and POST
  (E.g.: GET shouldn't take 'd').

HTTP library receives parameters
- (HOST, HTTP_METHOD, PATH, HEADERS: str "k:v" , BODY_DATA, VERBOSE)

TESTING
- In this file's path, enter 'python3 httpc.py get -h hello:world -H ok:lol'
  in the terminal. It should print out the arguments stored.

REQUEST REFERENCE
- httpc (get|post) [-v] (-h "k:v")* [-d inline-data] [-f file] URL
'''
import argparse
from enum import Enum
from urllib.parse import urlparse
from HTTPClientLibrary import HTTPClientLibrary

# Enum for HTTP methods
class HTTPMethod(Enum):
    GET = 'GET'
    POST = 'POST'

class HTTPC:
    def __init__(self):
        # Contains params needed to send to HTTP library
        self.__parsed_args = None
        self.__parser = None
        self.__hostname = ''
        # The full path AFTER hostname (path + query params)
        self.__full_path = ''
        self.__data = ''
    
    # Parses and stores user inputs from CLI
    def store_inputs(self):
        # Get input parameters using argparse library
        self.__parser = argparse.ArgumentParser(add_help=False)
        # When storing arguments, can use parameters to perform extra parsing
        self.__parser.add_argument('-help', action='help', help='Show this help message and exit')
        self.__parser.add_argument('method', type=str.upper, help='HTTP Method to use.', 
                            choices=[method.name for method in HTTPMethod])
        self.__parser.add_argument('-v', dest='verbose', help='Verbose mode. Display more information for a given request.',
                            default=False, action='store_true')
        self.__parser.add_argument('-h', dest='headers', help='Add headers in format headerName:valueName one at a time.',
                            action='append', type=self.__validate_header, default=[])
        self.__parser.add_argument('-d', dest='data', help='Add inline data to your request. Only for "POST" method.\
                            Cannot be used with "-f".')
        self.__parser.add_argument('-f', dest='file', help='Add file path to read data from. Only for "POST" method.\
                            Cannot be used with "-d".')
        self.__parser.add_argument('url', help='Add URL of the target HTTP server. Enclose with single quotes if your URL\
                            contains ampersands (&).',type=self.__validate_URL)
        self.__parser.add_argument('-o', dest='output', help='Add path to a file to write the response to (must be writable).')

        # All arguments will be stored here
        self.__parsed_args = self.__parser.parse_args()
        self.__validate_data()
        #print('[User input data]: ', self.__parsed_args, '\n')
    
    # Validates input header should contain 1 occurence of ':'
    def __validate_header(self, header):
        header_format = header.split(':')
        if len(header_format) < 2:
            raise argparse.ArgumentTypeError('Please input header in the format headerName:valueName.')
        return header
    
    # Validates URL in simple manner (checks if has http:// or https:// + a hostname)
    def __validate_URL(self, url):
        result = urlparse(url)
        if all([result.scheme, result.netloc, result.hostname]):
            # Set the hostname and full url path
            self.__hostname = result.netloc
            self.__full_path = result.path
            if result.params: self.__full_path += f';{result.params}'
            if result.query: self.__full_path += f'?{result.query}'
            return url
        else:
            raise argparse.ArgumentTypeError('Please enter a valid URL.')

    # Validates in-line/file data for GET/POST
    def __validate_data(self):
        if self.get_method() != HTTPMethod.POST.name and (self.get_inline_data() or self.get_file_path()):
            raise self.__parser.error('You may use "-d" or "-f" only with the POST method.')
        elif self.get_method() == HTTPMethod.POST.name:
            # If both file and inline data are present, raise error.
            if self.get_inline_data() and self.get_file_path():
                raise self.__parser.error('You may only use one of either "-d" or "-f", but not both.')
            elif self.get_inline_data():
                self.__data = self.get_inline_data()
            else:
                self.__data = self.__read_file_data(self.get_file_path())
        return True
    
    # Read data from file to send as data
    def __read_file_data(self, path):
        txt_data = ''
        print(path)
        with open(path, 'r') as reader:
            # Read entire file
            txt_data = reader.read(-1)
        
        if not txt_data:
            raise self.__parser.error('There was an error reading from the provided path or the file\
                                      was empty. Are you sure you input the correct absolute path?')
        return txt_data
    
    # Getters (-> return type)
    def get_method(self): # -> HTTPMethod
        return self.__parsed_args.method
    def get_verbose(self): # -> bool
        return self.__parsed_args.verbose
    def get_headers(self): # -> [str]
        return self.__parsed_args.headers
    def get_inline_data(self): # -> str
        return self.__parsed_args.data
    def get_data(self): # -> str
        return self.__data
    def get_file_path(self): # -> str
        return self.__parsed_args.file
    def get_url(self): # -> str
        return self.__parsed_args.url
    def get_hostname(self): # -> str
        return self.__hostname
    def get_url_path(self): # -> str
        return self.__full_path
    def get_output_path(self): # -> str
        return self.__parsed_args.output
    
'''
- A module’s __name__ is set equal to '__main__' when read from standard input, a script,
or from an interactive prompt. 
- This is the program's starting point.
'''
def main():
    print("\n=====[Smit & Pan's HTTP program]=====\n")

    # Create parser class
    httpc = HTTPC()
    # Store user CLI inputs
    httpc.store_inputs()
    # Use our HTTP library to send request
    request = HTTPClientLibrary()
    request.sendHTTPRequest(httpc.get_hostname(),httpc.get_method(),httpc.get_url_path(),httpc.get_headers(),
                            httpc.get_data(),httpc.get_verbose(),httpc.get_output_path())
    #request.sendHTTPRequest('localhost:8080','GET', VERBOSE=True)

    print('\n===========[END]===========\n')

if __name__ == "__main__":
    main()