# -*- coding: utf-8 -*-
'''
Parser for HTTP library

General
- Take in text input from cURL
- Convert to one string that can be input into HTTP library directly

Specifics
- Must check the command options. Not all should exist, also different for GET and POST
  (E.g.: GET shouldn't take 'd').

HTTP library receives parameters:
- (HOST, HTTP_METHOD, PATH, QUERY_PARAMS, HEADERS: str "k:v" , BODY_DATA, VERBOSE)

Make Python in excecutable
https://towardsdatascience.com/how-to-easily-convert-a-python-script-to-an-executable-file-exe-4966e253c7e9
'''
from collections import defaultdict
import sys

class HTTPC:
    # Constructor: 'self' refers to this current class: default parameter for all class functions.
    # Class member variables are defined here.
    def __init__(self):
        # Hashmap containing params needed to send to HTTP library
        self.params = defaultdict(None)
    
    # Parses user input into hashmap
    def parse(self, input):
        pass


'''
- A module’s __name__ is set equal to '__main__' when read from standard input, a script,
or from an interactive prompt. 
- This is the program's starting point.
- main() takes in as input the user's input
'''
def main():
    print("[Starting Pan & Smit's HTTP program!]")
    # sys.argv holds the inputs passed by user from CLI
    # these inputs are separated by the spaces in-between them.
    # sys.argv[0] will always be the file name (httpc.exe)
    if len(sys.argv) <= 1:
        print('Please specify input parameters for httpc.')

    # create parser class
    httpc = HTTPC()
    

if __name__ == "__main__":
    main()