import os
import shutil
import mimetypes
from pathlib import Path
from Modules.FileLock import FileLock

class FileHandler:

    def __init__(self):
        self.defaultDirectory = 'Data'

    def setDefaultDirectory(self, dirName):
        self.defaultDirectory = dirName        
        # absolutePath = os.path.join(os.getcwd(), dirName)

        # if Path(absolutePath).exists() and Path(absolutePath).is_dir():
        #     shutil.rmtree(absolutePath)

        # Path(absolutePath).mkdir(parents=True)

    def getNamesOfAllFiles(self):
        absolutePath = os.path.join(os.getcwd(), self.defaultDirectory)
        try:
            # Array of file names
            files = [f for f in os.listdir(absolutePath) if os.path.isfile(os.path.join(absolutePath, f))]
            return {
                'statusCode': 200,
                'data': '\n'.join(files)
            }
        except Exception as e:
            return {
                'statusCode': 500,
                'data': f'Error getting names of files: {e}'
            }

    def getFileContent(self,filename):
        # If user tries to access outside of default directory
        if '..' in filename:
            return {
                'statusCode': 403,
                'data': 'Forbidden access.'
            }

        file_path = self.defaultDirectory + '/' + filename
        try:
            if not Path(file_path).exists() or not Path(file_path).is_file():
                return {
                    'statusCode': 404,
                    'data': 'File does not exist.'
                }
                
            with open(file_path) as f: 
                file_data = f.read()

            CONTENT_TYPE = 'Content-Type: ' + mimetypes.guess_type(file_path)[0] 
            CONTENT_DISPOSITION = 'Content-Disposition: attachment; filename="' + filename + '"'

            return {
                'data': file_data,
                'statusCode': 200,
                'headers': [CONTENT_TYPE, CONTENT_DISPOSITION]
            }
        except Exception as e:
            return {
                'statusCode': 500,
                'data': f'Error getting file content: {e}'
            }

    def writeToFile(self, filename, filecontent):
        # If user tries to access outside of default directory
        if '..' in filename:
            return {
                'statusCode': 403,
                'data': 'Forbidden access.'
            }
            
        filename = self.defaultDirectory + '/' + filename

        # Locking the file to perform the write operation
        with FileLock(filename):
            try:
                f = open(filename, "w")
                f.write(filecontent)
                f.close()
                return {
                    'data': 'Successfully wrote file content.',
                    'statusCode': 200
                }
            except Exception as e:
                return {
                    'statusCode': 500,
                    'data': f'Error getting file content: {e}'
                }