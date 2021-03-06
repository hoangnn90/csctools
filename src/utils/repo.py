class CSCRepoException(Exception):
    def __init__(self, message):
        super(CSCRepoException, self).__init__(message)

class CSCRepoFailedException(CSCRepoException):
    def __init__(self, message):
        super(CSCRepoFailedException, self).__init__(message)

class CSCRepoInvalidException(CSCRepoException):
    def __init__(self, message):
        super(CSCRepoInvalidException, self).__init__(message)

class CSCRepoFailedToSyncException(CSCRepoFailedException):
    def __init__(self, message):
        super(CSCRepoFailedToSyncException, self).__init__(message)

class CSCRepoInvalidRepoBranchException(CSCRepoInvalidException):
    def __init__(self, message):
        super(CSCRepoInvalidRepoBranchException, self).__init__(message)

class CSCRepoInvalidRepoFileException(CSCRepoInvalidException):
    def __init__(self, message):
        super(CSCRepoInvalidRepoFileException, self).__init__(message)

class CSCRepoFailedToGetWspDirPath(CSCRepoFailedException):
    def __init__(self, message):
        super(CSCRepoFailedToGetWspDirPath, self).__init__(message)

class CSCRepoConnectionErrorException(CSCRepoFailedException):
    def __init__(self, message):
        super(CSCRepoConnectionErrorException, self).__init__(message)

class CSCRepoFailedToGetClientWorkspace(CSCRepoFailedException):
    def __init__(self, message):
        super(CSCRepoFailedToGetClientWorkspace, self).__init__(message)


class CSCRepo(object):
    def __init__(self, repo):
        self.repo = repo

    def connect(self):
        self.repo.connect()
    
    def disconnect(self):
        self.repo.disconnect()

    def getAllRepoBranch(self, branch):
        return self.repo.getAllRepoBranch(branch)

    def getAllRepoFileInBranch(self, branch):
        return self.repo.getAllRepoFileInBranch(branch)

    def syncFile(self, repo_file):
        self.repo.syncFile(repo_file)
    
    def getLocalFilePath(self, repo_file):
        return self.repo.getLocalFilePath(repo_file)
    
    def getWspDirPath(self, repo_file):
        return self.repo.getWspDirPath(repo_file)

    def createChangeList(self, description):
        return self.repo.createChangeList(description)

    def checkoutFile(self, repo_file, wsp_file, local_file, changelist):
        self.repo.checkoutFile(repo_file, wsp_file, local_file, changelist)

    def isRepoFile(self, repo_file):
        return self.repo.isRepoFile(repo_file)