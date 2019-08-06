def isBlank (string):
    if string and string.strip():
        return False
    return True

def isNotBlank (string):
    if string and string.strip():
        return True
    return False