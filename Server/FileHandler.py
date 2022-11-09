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

import os
import shutil
from pathlib import Path

class FileHandler:

    def __init__(self):
        self.defaultDirectory = 'Data'

    def setDefaultDirectory(self, dirName):
        self.defaultDirectory = dirName        
        absolutePath = os.path.join(Path().resolve, dirName)

        if Path(absolutePath).exists() and Path(absolutePath).is_dir():
            shutil.rmtree(absolutePath)

        Path(absolutePath).mkdir(parents=True)

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