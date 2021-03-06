import os
import queue
import shutil

from P4 import P4, P4Exception
from p4swamp import p4, P4Error

from utils import logutils, const, repo
from utils.salecode import sales

from utils.repo import CSCRepo, CSCRepoException, CSCRepoInvalidRepoFileException, CSCRepoInvalidRepoBranchException, CSCRepoFailedToSyncException, CSCRepoFailedToGetWspDirPath, CSCRepoConnectionErrorException, CSCRepoFailedToGetClientWorkspace

class P4Helper(CSCRepo):
    """ Helper class provide method to manipulate P4 data
    """
    def __init__(self, server, user, password, client=None):
        """ Connect to P4 with following params:
            @server: P4 server address (include port number)
            @user: P4 user
            @password: password of @user
            @client: P4 workspace name
        """ 
        self.p4 = P4()
        self.p4.port = server
        self.p4.user = user
        self.p4.password = password
        self.p4.client = client

    def connect(self):
        try:
            self.setClient(self.p4.client)
            self.setUser(self.p4.user)
            self.setPort(self.p4.port)
            self.p4.connect()
            self.p4.run_login()
        except P4Exception as e:
            raise CSCRepoConnectionErrorException("Failed to connect to perfore server %s with user %s, error %s" % (self.p4.port, self.p4.user, str(e)))

    def __del__(self):
        if self.p4.connected() is True:
            self.p4.disconnect()
    
    def disconnect(self):
        if self.p4.connected() is True:
            self.p4.disconnect()

    def getAllClientWorkspace(self, options=None):
        """ Get all client workspace of P4
        """
        clients = []
        dicts = {}
        try:
            if options is None:
                dicts = self.p4.run("clients")
            else:
                dicts = self.p4.run("clients", options)
        except P4Exception as e:
            raise CSCRepoFailedToGetClientWorkspace("Failed to get client workspace, error %s" %(str(e)))
        for d in dicts:
            clients.append(d['client'])
        return clients

    def setClient(self, client):
        """ Set P4CLIENT with @client
        """
        self.p4.set_env('P4CLIENT', client)

    def setUser(self, user):
        """ Set P4USER with @user
        """
        self.p4.set_env('P4USER', user)

    def setPort(self, port):
        """ Set P4PORT with @port
        """
        self.p4.set_env('P4PORT', port)

    def getFileNameFromPath(self, file):
        """Get file name from @file path
        """
        if not file:
            return None
        data = file.split("/")
        name = data[len(data) - 1]
        if name is not '':
            return name
        return None

    def getAllRepoBranch(self, branch):
        """Get all branchs of @branch including itself and its sub-directories
        """
        branchs = []
        mqueue = queue.Queue()
        if branch[len(branch) - 1] is not '/':
            branch = branch + "/"
        mqueue.put(str(branch))
        while not mqueue.empty():
            dir = mqueue.get()
            branchs.append(dir)
            dirs = []
            try:
                dirs = self.p4.run("dirs", dir + '*')
            except P4Exception:
                raise CSCRepoException("Could not find branch %s in depot, error %s" %(branch, self.p4.errors))
            for subdir in dirs:
                mqueue.put(str(subdir["dir"] + "/"))
        return branchs

    def getAllRepoFileInBranch(self, branch):
        """Get all files included in @branch including itself and its sub-directories
        """
        files = []
        if branch[len(branch) - 1] is not '/':
            branch = branch + "/"
        try:
            files_dict = self.p4.run('files', '-e', branch + '...')
        except P4Exception:
            raise CSCRepoException("Could not find any file in branch %s in depot" %(branch))
        for file_dict in files_dict:
            files.append(file_dict['depotFile'])
        return files

    def isRepoFile(self, depot_file):
        """Verify if @depot_file is existed in P4 depot
        """
        if not depot_file:
            return False
        try:
            self.p4.run("files", depot_file)
            return True
        except P4Exception:
            return False

    def getLocalFilePath(self, depot_file):
        """ Find the file path in local PC of depot file @depot_file
            Note: p4 where does not check file exists is local or not.
            So local path of file that already removed from depot will also found
        """
        if self.isRepoFile(depot_file) is True:
            file_infos = {}
            try:
                file_infos = p4('where', depot_file)
                local_path = file_infos[0]["path"]
                return local_path
            except P4Error as e:
                raise CSCRepoFailedToGetWspDirPath(" %s " %(str(e)))
        else:
            raise CSCRepoInvalidRepoFileException("File %s is not existed in depot" %(depot_file))            
    
    
    def getWspDirPath(self, depot_branch):
        """ Find the wsp dir path of @depot_branch
        """
        if depot_branch[len(depot_branch) - 1] is '/':
            depot_branch = depot_branch[:-1]
        
        dir_infos = {}
        try:
            dir_infos = p4('where', depot_branch)
            local_dir = dir_infos[0]["path"]
            return local_dir + '\\'
        except P4Error:
            raise CSCRepoFailedToGetWspDirPath("Failed to get wsp dir path of %s. Please map it to wsp and get latest revision before doing checkout" %(depot_branch))

    def syncFile(self, depot_file):
        """ Sync @depot_file from P4 server to local
            It does map @depot_file to client workspace
            Note: p4 sync command try to map file even if it is already removed from depot
            Use option -q to suppress normal output messages. Messages describing errors or exceptional conditions are not suppressed.
        """
        if self.isRepoFile(depot_file) is True:
            try:
                p4('sync', '-f', '-q', depot_file + '#head')
            except P4Error as e:
                raise CSCRepoFailedToSyncException("Failed to sync '%s' with error %s" % (depot_file, str(e)))
        else:
            raise CSCRepoInvalidRepoFileException("File '%s' is not existed in depot" % (depot_file))

    def createChangeList(self, description):
        """ Create a new changelist and return the changelist number
        """
        changespec = self.p4.save_change({'Change': 'new', 'Description': description})[0]
        return int(changespec.split()[1])

    def checkoutFile(self, repo_file, wsp_file, local_file, changelist):
        """ Replace @repo_file content by @local_file in @changelist
        If @repo_file is not existed in repo, add it to repo
        If @repo_file is checkout in another changelist, throw exception
        """
        opened_files = self.p4.run('opened')
        for f in opened_files:
            if(f['depotFile'] == repo_file and f['change'] != str(changelist)):
                raise CSCRepoInvalidRepoFileException("File %s is already checkout in changelist %s" %(repo_file, f['change']))
        try:
            self.p4.run('edit', '-c' , int(changelist), repo_file)
            shutil.copy2(local_file, wsp_file)
        except P4Exception as e:
            try:
                shutil.copy2(local_file, wsp_file)
                self.p4.run('add', '-c', int(changelist), wsp_file)
            except FileNotFoundError as e:
                raise CSCRepoInvalidRepoFileException(str(e))        
        except FileNotFoundError as e:
            raise CSCRepoInvalidRepoFileException(str(e))