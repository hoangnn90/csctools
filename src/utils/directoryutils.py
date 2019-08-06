import os

def findFileInDirectory(directory, extension, files):
    try:
        for f in os.listdir(directory):
            if extension == None:
                files.append(f)
            elif f.endswith(extension):
                files.append(f)
    except FileNotFoundError:
        pass
    return files