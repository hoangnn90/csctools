class CSCRepo(object):
    def __init__(self, repo):
        self.repo = repo

    def connect(self):
        self.repo.connect()
    
    def disconnect(self):
        self.repo.disconnect()

    def getAllDepotBranch(self, branch):
        return self.repo.getAllDepotBranch(branch)

    def getAllDepotFileInBranch(self, branch):
        return self.repo.getAllDepotFileInBranch(branch)

    def syncFile(self, repo_file):
        self.repo.syncFile(repo_file)
    
    def getLocalFilePath(self, repo_file):
        return self.repo.getLocalFilePath(repo_file)
