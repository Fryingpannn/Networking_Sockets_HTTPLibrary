'''
    Status Code: 
        1) 200: All Good
        2) 404: File Not Found
        3) 400: Security issue

    Return Type: dict
    {
        'statusCode': 'value',
        'data': 'Actual data or the error message'
    }
'''


'''
    Possbile status code returned: 200
'''
def getNamesOfAllFiles():
    pass


'''
    Possbile status code returned: 200, 400, 404
'''
def getFileContent(filename):
    pass


'''
    Possbile status code returned: 200, 400
'''
def writeToFile(filename, filecontent):
    pass