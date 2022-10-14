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
- (HOST, HTTP_METHOD, PATH, HEADERS: str "k:v" , BODY_DATA, VERBOSE)
'''
import argparse

class HTTPC:
    def __init__(self):
        # Contains params needed to send to HTTP library
        self.parsed_args = None
    
    # Parses and stores user inputs from CLI
    # Ref: httpc (get|post) [-v] (-h "k:v")* [-d inline-data] [-f file] URL
    def store_inputs(self):
        # Get input parameters using argparse library
        parser = argparse.ArgumentParser()
        # When storing arguments, can use parameters to perform extra parsing
        parser.add_argument('method', type=str.upper, help='HTTP Method to use.', 
                                 choices=['GET', 'POST'])
        parser.add_argument('-v', '--verbose', help='Displays more \
                                 information.', required=False, action='store_true')
        # parser.add_argument('-h', help='Add headers in format headerName:valueName.',
        #                    required=False, action='append')

        # All arguments will be stored here
        self.parsed_args = parser.parse_args()
        print('Test: ', self.parsed_args)


'''
- A module’s __name__ is set equal to '__main__' when read from standard input, a script,
or from an interactive prompt. 
- This is the program's starting point.
'''
def main():
    print("\n=====[Starting Pan & Smit's HTTP program!]=====\n")

    # Create parser class
    httpc = HTTPC()
    # Store user CLI inputs
    httpc.store_inputs()

    print('\n=====[END]=====\n')
    
if __name__ == "__main__":
    main()