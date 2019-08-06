def isExisted(dicts, key, value):
    for d in dicts:
        if d[key] == value:
            return True
    return False