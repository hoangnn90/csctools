class CSCException(Exception):
    def __init__(self, message):
        super(CSCException, self).__init__(message)

class CSCFailOperation(CSCException):
    def __init__(self, message):
        super(CSCFailOperation, self).__init__(message)