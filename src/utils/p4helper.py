import os
import queue

from P4 import P4, P4Exception
from p4swamp import p4, P4Error

from utils import logutils, const, repo
from utils.salecode import sales

from utils.repo import CSCRepo

class P4HelperException(Exception):
    def __init__(self, message):
        super(P4HelperException, self).__init__(message)

class P4FailedToSyncException(P4HelperException):
    def __init__(self, message):
        super(P4FailedToSyncException, self).__init__(message)

class P4InvalidDepotFileException(P4HelperException):
    def __init__(self, message):
        super(P4InvalidDepotFileException, self).__init__(message)

class P4FailedToGetLocalPath(P4HelperException):
    def __init__(self, message):
        super(P4FailedToGetLocalPath, self).__init__(message)

class P4ConnectionErrorException(P4HelperException):
    def __init__(self, message):
        super(P4ConnectionErrorException, self).__init__(message)

class P4FailedToGetClientWorkspace(P4HelperException):
    def __init__(self, message):
        super(P4FailedToGetClientWorkspace, self).__init__(message)

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
            self.p4.connect()
            self.p4.run_login()
        except P4Exception as e:
            raise P4ConnectionErrorException("Failed to connect to perfore server %s with user %s, error %s" % (self.p4.port, self.p4.user, str(e)))

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
            raise P4FailedToGetClientWorkspace("Failed to get client workspace, error %s" %(str(e)))
        for d in dicts:
            clients.append(d['client'])
        return clients

    def setClient(self, client):
        """ Set P4CLIENT with @client
        """
        self.p4.set_env('P4CLIENT', client)

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

    def getAllDepotBranch(self, branch):
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
                raise P4HelperException("Could not find branch %s in depot, error %s" %(branch, self.p4.errors))
            for subdir in dirs:
                mqueue.put(str(subdir["dir"] + "/"))
        return branchs

    def getAllDepotFileInBranch(self, branch):
        """Get all files included in @branch including itself and its sub-directories
        """
        files = []
        if branch[len(branch) - 1] is not '/':
            branch = branch + "/"
        try:
            files_dict = self.p4.run('files', '-e', branch + '...')
        except P4Exception:
            raise P4HelperException("Could not find any file in branch %s in depot" %(branch))
        for file_dict in files_dict:
            files.append(file_dict['depotFile'])
        return files

    def isDepotFile(self, depot_file):
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
        if self.isDepotFile(depot_file) is True:
            file_infos = {}
            try:
                file_infos = p4('where', depot_file)
                # logutils.log_info(file_infos)
                local_path = file_infos[0]["path"]
                # logutils.log_info("local_path: %s" %(local_path))
                return local_path
            except P4Error as e:
                raise P4FailedToGetLocalPath(" %s " %(str(e)))
        else:
            raise P4InvalidDepotFileException("File %s is not existed in depot" %(depot_file))
            

    def syncFile(self, depot_file):
        """ Sync @depot_file from P4 server to local
            It does map @depot_file to client workspace
            Note: p4 sync command try to map file even if it is already removed from depot
            Use option -q to suppress normal output messages. Messages describing errors or exceptional conditions are not suppressed.
        """
        if self.isDepotFile(depot_file) is True:
            try:
                p4('sync', '-s', '-q', depot_file + '#head')
            except P4Error as e:
                raise P4FailedToSyncException("Failed to sync '%s' with error %s" % (depot_file, str(e)))
        else:
            raise P4InvalidDepotFileException("File '%s' is not existed in depot" % (depot_file))
    