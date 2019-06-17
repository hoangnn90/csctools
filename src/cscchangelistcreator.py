import os
from PyQt5 import uic, QtCore, QtGui, QtCore, QtWidgets
from PyQt5.QtGui import QIcon, QTextCursor
from PyQt5.QtCore import QSettings, Qt, QCoreApplication
from PyQt5.QtWidgets import QApplication, QDialog, QMainWindow
import sys
import ctypes
import operator
import csv
import time
import subprocess
from threading import Thread
from enum import Enum
from utils import cscutils, const
from utils.p4helper import P4Helper
from utils.repo import CSCRepoException, CSCRepoInvalidRepoFileException, CSCRepoInvalidRepoBranchException, CSCRepoFailedToSyncException, CSCRepoFailedToGetWspDirPath
from utils.cscexception import CSCException, CSCFailOperation
from utils.xmlutils import XmlHelper, XmlHelperException
from utils.logutils import Logging, log_error, log_info, log_notice, log_warning
from utils.stringutils import isNotBlank
from utils.repo import CSCRepo
from utils import directoryutils

UI_MAIN_WINDOW = "ui\cscchangelistcreator.ui"
ICON_FILE = "ui\cscchangelistcreator.png"
VERSION = "0.01"
EXTENSION = [{'extension': '.dat', 'directory': 'etc'}] # {extension, directory}

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

class CSCChangeListCreator(QMainWindow):
    infos = []  # dict contains sale corresponding with branch
    data_files = []  # dict contains data files will be patched
    not_checkout_files = [] # list contains data files not patched
    result_files = {}
    def __init__(self):
        super(CSCChangeListCreator, self).__init__()
        self.settings = QSettings('csctools', 'cscchangelistcreator')
        self.setupUI()
        self.setupLog()

    def closeEvent(self, event):
        self.settings.setValue('server', self.le_server.text())
        self.settings.setValue('user', self.le_user.text())
        self.settings.setValue('password', self.le_password.text())
        self.settings.setValue('wsp', self.le_wsp.text())
        self.settings.setValue('branch', self.le_branch.text())
        self.settings.setValue('directory', self.le_directory.text())
        self.settings.setValue('sales', self.le_sales.text())

    def restoreSettings(self):
        if isNotBlank(self.settings.value('server')):
            self.le_server.setText(self.settings.value('server'))
        if isNotBlank(self.settings.value('user')):
            self.le_user.setText(self.settings.value('user'))
        if isNotBlank(self.settings.value('password')):
            self.le_password.setText(self.settings.value('password'))
        if isNotBlank(self.settings.value('wsp')):
            self.le_wsp.setText(self.settings.value('wsp'))
        if isNotBlank(self.settings.value('branch')):
            self.le_branch.setText(self.settings.value('branch'))
        if isNotBlank(self.settings.value('directory')):
            self.le_directory.setText(self.settings.value('directory'))
        self.le_sales.setText(self.settings.value('sales'))

    def setupCallback(self):
        self.pb_go.clicked.connect(self.onConnectBtnClicked)
        self.pb_search.clicked.connect(self.onCreateBtnClicked)
        self.cb_file_name.currentIndexChanged.connect(self.onFileNameChanged)
        self.le_directory.textChanged.connect(self.onDataDirectoryChanged)
        self.le_sales.textChanged.connect(self.onSalesChanged)
        self.le_branch.textChanged.connect(self.onBranchChanged)
        self.le_wsp.textChanged.connect(self.onClientWorkspaceChanged)
    
    def setupUI(self):
        myappid = 'mycompany.myproduct.subproduct.version'  # arbitrary string
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        uic.loadUi(resource_path(UI_MAIN_WINDOW), self)
        self.setWindowIcon(QIcon(resource_path(ICON_FILE)))
        self.label_version.setText(self.label_version.text() + VERSION)
        self.restoreSettings()
        self.setupCallback()

    def setupLog(self):
        sys.stdout = Logging(newText=self.onLogChanged)

    def onLogChanged(self, text):
        cursor = self.te_message.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertHtml(text)
        self.te_message.setTextCursor(cursor)
        self.te_message.ensureCursorVisible()

    def onFileNameChanged(self):
        self.te_message.clear()
        self.te_result.clear()

    def onDataDirectoryChanged(self):
        self.te_message.clear()
        self.te_result.clear()
    
    def onSalesChanged(self):
        self.te_message.clear()
        self.te_result.clear()

    def onBranchChanged(self):
        self.pb_search.setEnabled(False)

    def onClientWorkspaceChanged(self):
        self.pb_search.setEnabled(False)

    def validateInput(self):
        if not self.le_server.text():
            log_error(
                "Server address is empty, please specify server address !")
            return False
        if not self.le_user.text():
            log_error("Username is empty, please specify username !")
            return False
        if not self.le_password.text():
            log_error("Password is empty, please specify password !")
            return False
        if not self.le_wsp.text():
            log_error("Workspace is empty, please specify branch !")
            return False
        if not self.le_branch.text():
            log_error("Branch is empty, please specify branch !")
            return False
        return True

    def connecToPerforce(self):
        try:
            server = self.le_server.text()
            user_name = self.le_user.text()
            password = self.le_password.text()
            client = self.le_wsp.text()
            self.repo = CSCRepo(P4Helper(server, user_name, password, client))
            self.repo.connect()
        except CSCRepoException as e:
            log_error(e)
            return False
        return True

    def getDepotDataInfo(self, infos):
        branch = self.le_branch.text()
        branchs = []
        found = False
        try:
            branchs = self.repo.getAllRepoBranch(branch)
        except CSCRepoException as e:
            log_error(e)
            return
        for b in branchs:
            sale = cscutils.getSaleCodeFromBranch(b)
            if sale is not None:
                found = True
                if cscutils.isRepoSaleCodeRootBranch(b):
                    info = {'repo_branch': b, 'sale' : sale}
                    infos.append(info)
        if not found:
            log_error("Could not find any sale code in branch '%s'" % (branch))
        else:
            self.pb_search.setEnabled(True)
        return infos

    def onConnectBtnClicked(self):
        QApplication.setOverrideCursor(Qt.WaitCursor)
        self.te_message.clear()
        self.te_result.clear()
        if self.validateInput():
            try:
                self.connecToPerforce()
                infos = []
                collect_sale_thread = Thread(target=self.getDepotDataInfo, args=[infos])
                collect_sale_thread.start()
                collect_sale_thread.join()
                CSCChangeListCreator.infos = infos
                log_notice("Connection is established succesfully. Click 'Create' button to create change list!")
            except CSCRepoException as e:
                log_error(str(e))
        QApplication.restoreOverrideCursor()

    def validateOptions(self):
        if not self.le_directory.text():
            log_error("Data directory is empty, please specify data directory !")
            return False
        return True


    def onCreateBtnClicked(self):
        QApplication.setOverrideCursor(Qt.WaitCursor)
        self.te_message.clear()
        self.te_result.clear()
        if self.validateOptions():
            files = []
            directory = self.le_directory.text()
            find_file_thread = Thread(target=directoryutils.findFileInDirectory, args=(directory, EXTENSION[0]['extension'], files))
            find_file_thread.start()
            find_file_thread.join()
            if not files:
                log_error("Could not find file with extension %s in directory %s" %(EXTENSION[0]['extension'], directory))
                QApplication.restoreOverrideCursor()
                return
            for f in files:
                checkout_flag = False
                file_full_name = os.path.join(directory, f)
                sale = cscutils.getSaleCodeFromKeyStringFile(f)
                for info in CSCChangeListCreator.infos:
                    if info['sale'] == sale:
                        checkout_flag = True
                        data = info.copy()
                        data['local_file'] = file_full_name
                        CSCChangeListCreator.data_files.append(data)
                if not checkout_flag:
                    CSCChangeListCreator.not_checkout_files.append(f)
            if CSCChangeListCreator.data_files:
                changelist = self.repo.createChangeList(const.DEFAULT_CHANGELIST_DESCRIPTION)
                for data in CSCChangeListCreator.data_files:
                    checkout_file_name = self.cb_file_name.currentText()
                    csc_file = cscutils.getCSCFileBySale(checkout_file_name, data['sale'])
                    repo_branch = data['repo_branch']
                    repo_file = cscutils.getRepoBranchByFile(repo_branch, checkout_file_name) + csc_file
                    try:
                        self.repo.syncFile(repo_file)
                    except CSCRepoInvalidRepoFileException as e:
                        pass # file not existed in repo, so will add it in next step
                    wsp_path = ""
                    try:
                        wsp_path = self.repo.getWspDirPath(repo_branch)
                    except CSCRepoFailedToGetWspDirPath as e:
                        log_error(str(e))
                        continue
                    wsp_branch = cscutils.getWspBranchByFile(wsp_path, checkout_file_name)
                    if not os.path.exists(wsp_branch):
                        os.makedirs(wsp_branch)
                    wsp_file = wsp_branch + csc_file
                    try:
                        self.repo.checkoutFile( repo_file, wsp_file, data['local_file'], int(changelist))
                    except CSCRepoInvalidRepoFileException as e:
                        log_error(str(e))
                log_notice("Changelist %d has been created" %(changelist))
                log_warning("Following file(s) are not checkout %s" %([str(f) for f in CSCChangeListCreator.not_checkout_files]))
            else:
                log_error("Could not find any sale in branch %s to apply file %s" %(self.le_branch.text(), checkout_file_name))
        QApplication.restoreOverrideCursor()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = CSCChangeListCreator()
    window.show()
    sys.exit(app.exec_())
