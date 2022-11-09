import os
from pathlib import Path

class FileHandler:

    def __init__(self):
        self.defaultDirectory = 'Data'

    def setDefaultDirectory(self, dirName):
        self.defaultDirectory = dirName        
        absolutePath = os.path.join(os.getcwd(), dirName)

        # if Path(absolutePath).exists() and Path(absolutePath).is_dir():
        #     shutil.rmtree(absolutePath)

        # Path(absolutePath).mkdir(parents=True)

    def getNamesOfAllFiles(self):
        absolutePath = os.path.join(os.getcwd(), self.defaultDirectory)
        try:
            # Array of file names
            files = [f for f in os.listdir(absolutePath) if os.path.isfile(os.path.join(absolutePath, f))]
            print(0.6, files)
            return {
                'statusCode': 200,
                'data': '\n'.join(files)
            }
        except:
            print(0.7)
            return {
                'statusCode': 500,
                'data': 'Error getting names of files.'
            }

    def getFileContent(self,filename):
        filename = self.defaultDirectory + '/' + filename
        try:
            if not Path(filename).exists() or not Path(filename).is_file():
                print(1)
                return {
                    'statusCode': 404,
                    'data': 'File does not exist.'
                }
                
            with open(filename) as f: 
                file_data = f.read()
            print(2)
            return {
                'data': file_data,
                'statusCode': 200
            }
        except:
            print(3)
            return {
                'statusCode': 500,
                'data': 'Error getting file content.'
            }


    def writeToFile(self, filename, filecontent):
        filename = self.defaultDirectory + '/' + filename
        try:
            f = open(filename, "w")
            f.write(filecontent)
            f.close()
            return {
                'data': 'Successfully wrote file content.',
                'statusCode': 200
            }
        except:
            return {
                'statusCode': 500,
                'data': 'Error getting file content.'
            }