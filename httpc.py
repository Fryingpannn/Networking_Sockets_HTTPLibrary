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
from HTTPLibrary import HTTPLibrary

class HTTPMethod(Enum):
    GET = 'GET'
    POST = 'POST'

class HTTPC:
    def __init__(self):
        # Contains params needed to send to HTTP library
        self.__parsed_args = None
        self.__parser = None
    
    # Parses and stores user inputs from CLI
    def store_inputs(self):
        # Get input parameters using argparse library
        self.__parser = argparse.ArgumentParser(add_help=False)
        # When storing arguments, can use parameters to perform extra parsing
        self.__parser.add_argument('-help', action='help', help='Show this help message and exit')
        self.__parser.add_argument('method', type=str.upper, help='HTTP Method to use.', 
                            choices=[method.name for method in HTTPMethod])
        self.__parser.add_argument('-v', '--verbose', help='Display more information.',
                            default=False, action='store_true')
        self.__parser.add_argument('-h', '-H', dest='headers', help='Add headers in format headerName:valueName one at a time.',
                            action='append', type=self.__validate_header)
        self.__parser.add_argument('-d', dest='data', help='Add inline data to your request. Only for "POST" method.')
        self.__parser.add_argument('-f', dest='file', help='Add file path to read data from. Only for "POST" method.')
        self.__parser.add_argument('url', help='Add URL of the target HTTP server (can include query parameters).',
                            type=self.__validate_URL)

        # All arguments will be stored here
        self.__parsed_args = self.__parser.parse_args()
        self.__validate_data()
        print('Test: ', self.__parsed_args)
    
    # Validates input header should contain 1 occurence of ':'
    def __validate_header(self, header):
        header_format = header.split(':')
        if len(header_format) != 2:
            raise argparse.ArgumentTypeError('Please input header in the format headerName:valueName.')
        return header
    
    # Validates URL in simple manner (checks if has http:// or https:// + a hostname)
    def __validate_URL(self, url):
        result = urlparse(url)
        if all([result.scheme, result.netloc]):
            return url
        else:
            raise argparse.ArgumentTypeError('Please enter a valid URL.')

    # Validates in-line/file data for GET/POST
    def __validate_data(self):
        if self.get_method() != HTTPMethod.POST.name and (self.get_inline_data() or self.get_file_path()):
            raise self.__parser.error('You may use "-d" or "-f" only with the POST method.')
        elif self.get_method() == HTTPMethod.POST.name:
            # If both file and inline data are present, raise error.
            inline_or_file = [data for data in [self.get_inline_data(),self.get_file_path()] if data]
            if len(inline_or_file) > 1:
                raise self.__parser.error('You may only use one of either "-d" or "-f", but not both.')
        return True
    
    # Getters (-> return type)
    def get_method(self): # -> HTTPMethod
        return self.__parsed_args.method
    def get_verbose(self): # -> bool
        return self.__parsed_args.verbose
    def get_headers(self): # -> [str]
        return self.__parsed_args.headers
    def get_inline_data(self): # -> str
        return self.__parsed_args.data
    def get_file_path(self): # -> str
        return self.__parsed_args.file
    def get_url(self): # -> str
        return self.__parsed_args.url
    
'''
- A module’s __name__ is set equal to '__main__' when read from standard input, a script,
or from an interactive prompt. 
- This is the program's starting point.
'''
def main():
    print("\n=====[Pan & Smit's HTTP program]=====\n")

    # Create parser class
    httpc = HTTPC()
    # Store user CLI inputs
    httpc.store_inputs()
    # Use our HTTP library to send request
    request = HTTPLibrary()
    # request.sendHTTPRequest()

    print('\n=====[END]=====\n')
    
if __name__ == "__main__":
    main()