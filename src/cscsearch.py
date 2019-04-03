import os
from PyQt5 import uic, QtCore, QtGui, QtCore, QtWidgets
from PyQt5.QtGui import QIcon, QTextCursor
from PyQt5.QtCore import QSettings, Qt, QCoreApplication
from PyQt5.QtWidgets import QApplication, QDialog
import sys
import ctypes
import operator
import csv
import time
import subprocess
from threading import Thread
from enum import Enum
from utils.p4helper import P4Helper, P4HelperException, P4InvalidDepotFileException, P4FailedToSyncException
from utils.cscexception import CSCException, CSCFailOperation
from utils.xmlutils import XmlHelper, XmlHelperException
from utils.logutils import Logging, log_error, log_info, log_notice, log_warning
from utils.stringutils import isNotBlank

UI_MAIN_WINDOW = "ui\cscsearch.ui"
UI_OPEN_RESULT_DIALOG = "ui\cscsearch_open_file_dialog.ui"
ICON_FILE = "ui\cscsearch.png"
VERSION = "0.08"
EXTENSIONS = ['.xml']

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

class OpenFileType(Enum):
    TXT='txt'
    CSV='csv'
    SHOW_FOLDER='show_folder'

class OpenFileDialog(QDialog):
    def __init__(self, parent):
        super(OpenFileDialog, self).__init__()
        self.settings = QSettings('csctools', 'cscsearch_open_result_dialog')
        self.setupUI()
        self.parent=parent
    
    def closeEvent(self, event):
        self.parent.settings.setValue('do_not_show_cb', self.cb_do_not_show.isChecked())

    def setupUI(self):
        uic.loadUi(resource_path(UI_OPEN_RESULT_DIALOG), self)
        self.setWindowIcon(QIcon(resource_path(ICON_FILE)))
        self.setWindowTitle("Open result files")
        self.rb_txt.setChecked(True)
        self.setupOnChangedCallback()

    def setupOnChangedCallback(self):
        self.pb_ok.clicked.connect(self.onOKBtnClicked)
        self.pb_cancel.clicked.connect(self.onCancelBtnClicked)
    
    def getOpenFileType(self):
        file_type = None
        if self.rb_txt.isChecked():
            file_type=OpenFileType.TXT
        if self.rb_csv.isChecked():
            file_type=OpenFileType.CSV
        if self.rb_show.isChecked():
            file_type=OpenFileType.SHOW_FOLDER
        return file_type

    def onOKBtnClicked(self):
        file_type = self.getOpenFileType()
        if file_type is None:
            log_error("Please choose file type to open")
        else:
            os.startfile(self.parent.result_files[file_type])
        self.close()
    
    def onCancelBtnClicked(self):
        self.close()

class CSCSearch(QDialog):
    infos = []  # dict contains csc and files in branch
    results = []  # dict contains search result
    result_files = {}
    def __init__(self):
        super(CSCSearch, self).__init__()
        self.settings = QSettings('csctools', 'cscsearch')
        self.setupUI()
        self.setupLog()
        self.open_file_dialog = OpenFileDialog(parent=self)

    def closeEvent(self, event):
        self.settings.setValue('server', self.le_server.text())
        self.settings.setValue('user', self.le_user.text())
        self.settings.setValue('password', self.le_password.text())
        self.settings.setValue('wsp', self.le_wsp.text())
        self.settings.setValue('branch', self.le_branch.text())
        self.settings.setValue('tag_name', self.le_tag_name.text())
        self.settings.setValue('tag_values', self.le_tag_values.text())

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
        if isNotBlank(self.settings.value('tag_name')):
            self.le_tag_name.setText(self.settings.value('tag_name'))
        self.le_tag_values.setText(self.settings.value('tag_values'))

    def setupOnChangedCallback(self):
        self.pb_go.clicked.connect(self.onConnectBtnClicked)
        self.pb_search.clicked.connect(self.onSearchBtnClicked)
        self.cb_sale.currentIndexChanged.connect(self.onSaleCodeChanged)
        self.le_tag_name.textChanged.connect(self.onTagNameChanged)
        self.le_tag_values.textChanged.connect(self.onTagValuesChanged)
        self.le_branch.textChanged.connect(self.onBranchChanged)
        self.le_wsp.textChanged.connect(self.onClientWorkspaceChanged)
    
    def setupUI(self):
        myappid = 'mycompany.myproduct.subproduct.version'  # arbitrary string
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        uic.loadUi(resource_path(UI_MAIN_WINDOW), self)
        self.setWindowIcon(QIcon(resource_path(ICON_FILE)))
        self.label_version.setText(self.label_version.text() + VERSION)
        self.restoreSettings()
        self.setupOnChangedCallback()

    def setupLog(self):
        sys.stdout = Logging(newText=self.onLogChanged)

    def onLogChanged(self, text):
        cursor = self.te_message.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertHtml(text)
        self.te_message.setTextCursor(cursor)
        self.te_message.ensureCursorVisible()

    def onSaleCodeChanged(self):
        self.te_message.clear()
        self.te_result.clear()
        self.open_file_dialog.close()

    def onTagNameChanged(self):
        self.te_message.clear()
        self.te_result.clear()
        self.open_file_dialog.close()
    
    def onTagValuesChanged(self):
        self.te_message.clear()
        self.te_result.clear()
        self.open_file_dialog.close()

    def onBranchChanged(self):
        self.cb_sale.clear()
        self.pb_search.setEnabled(False)

    def onClientWorkspaceChanged(self):
        self.cb_sale.clear()
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
            self.p4 = P4Helper(server, user_name, password, client)
        except P4HelperException as e:
            log_error(e)
            return False
        return True

    def createClientWorkspace(self):
        clients = self.p4.getAllClientWorkspace()
        for client in clients:
            cmd_add = '{} {} {}'.format('p4 client -o', client, '| p4 client -i')
            # print(cmd_add)
            print(subprocess.call(cmd_add))
            cmd_reset = '{}'.format('set P4CLIENT=')
            # print(cmd_reset)
            # subprocess.call(cmd_reset)
            cmd_set = '{}{}'.format('p4 set P4CLIENT=', client)
            # print(cmd_set)
            # subprocess.call(cmd_set)

    def updateSale(self):
        sales = []
        branch = self.le_branch.text()
        branchs = []
        try:
            branchs = self.p4.getAllDepotBranch(branch)
        except P4HelperException as e:
            log_error(e)
            return
        for b in branchs:
            sale = self.p4.getSaleCodeFromBranch(b)
            if sale is not None:
                sales.append(sale)
        sales = set(sales)
        for sale in sorted(sales):
                if self.cb_sale.findText(sale) == -1:
                    self.cb_sale.addItem(sale)
                    self.pb_search.setEnabled(True)
        if len(sales) >= 2 and self.cb_sale.findText('All') == -1:
            self.cb_sale.insertItem(0, 'All')
            self.cb_sale.setCurrentIndex(0)
        if len(sales) == 0:
            log_error("Could not find any file in branch '%s'" % (branch))

    def onConnectBtnClicked(self):
        QApplication.setOverrideCursor(Qt.WaitCursor)
        self.te_message.clear()
        self.te_result.clear()
        self.open_file_dialog.close()
        if self.validateInput() and self.connecToPerforce():
            # self.createClientWorkspace() #TODO: Create client workspace automatically
            update_sale_thread = Thread(target=self.updateSale)
            update_sale_thread.start()
            update_sale_thread.join()
        QApplication.restoreOverrideCursor()

    def validateOptions(self):
        if not self.le_tag_name.text():
            log_error("Tag name is empty, please specify tag name !")
            return False
        return True

    def isItemToWrite(self, value):
        tag_values = self.le_tag_values.text()
        if not tag_values:
            return True
        required_values = tag_values.rstrip().split(',')
        for required_value in required_values:
            if required_value == value:
                return True
        return False

    def isCorrectFileExtension(self, file, extensions):
        if not file:
            return False
        for ext in extensions:
            extension = os.path.splitext(file)[1]
            if extension == ext:
                return True
        return False

    def getFilesInBranch(self, branch, extensions, infos):
        files = []
        try:
            files = self.p4.getAllDepotFile(branch)
        except P4HelperException as e:
            log_error(e)
            return
        for f in files:
            if self.isCorrectFileExtension(f, extensions) is True:
                sale = self.p4.getSaleCodeFromBranch(f)
                if sale is not None:
                    info = {'file': f, 'sale' : sale}
                    infos.append(info)
        return infos

    def getResult(self, infos, results):
        tag = self.le_tag_name.text()
        sale = self.cb_sale.currentText()
        for info in infos:
            if (sale == 'All') or (sale != 'All' and info['sale'] == sale):
                depot_file = info['file']
                local_file = ''
                try:
                    self.p4.syncP4File(depot_file)
                    local_file = self.p4.getLocalFilePath(depot_file)
                except P4FailedToSyncException as e:
                    pass
                except P4HelperException as e:
                    log_error(e)
                    return
                if os.path.isfile(local_file):  # Fix file that deleted from server but 'p4 files' cmd still get it
                    try:
                        helper = XmlHelper(local_file)
                    except XmlHelperException as e:
                        log_warning(e)
                        continue
                    tag_values = helper.getTagContents(local_file, tag)
                    if tag_values:
                        for tag_value in tag_values:
                            result = info.copy()  # copy sale and file values to result
                            result['value'] = tag_value
                            results.append(result)
                    else:
                        result = info.copy()
                        result['value'] = '-'
                        results.append(result)
        # results.sort(key=operator.itemgetter('sale'))
        # print(results)
        return results

    def writeOutput(self, results, result_files):
        tag = self.le_tag_name.text()
        cwd = os.getcwd()
        result_files[OpenFileType.SHOW_FOLDER] = cwd
        # Write to csv file
        csv_file = '{}\{}{}'.format(cwd, time.strftime("%Y%m%d-%H%M%S"), '.csv')
        with open(csv_file, 'w', newline='') as out:
            fields = ['tag', 'sale', 'value', 'file']
            writer = csv.DictWriter(out, fields)
            writer.writeheader()
            for result in results:
                if self.isItemToWrite(result['value']) is True:
                    writer.writerow({'tag' : tag, 'sale' : result['sale'], 'value' : result['value'], 'file' : result['file']})
        result_files[OpenFileType.CSV] = csv_file
        # Write to txt file
        txt_file = '{}\{}{}'.format(cwd, time.strftime("%Y%m%d-%H%M%S"), '.txt')
        tag_ljust_size = len(tag) + 4
        sale_ljust_size = 8
        value_ljust_size = 5
        for result in results:
            if value_ljust_size < len(result['value']):
                value_ljust_size = len(result['value'])
        value_ljust_size = value_ljust_size + 4
        with open(txt_file, 'w') as out:
            out.write('%s%s%s%s\n' % ('tag'.ljust(tag_ljust_size), 'sale'.ljust(sale_ljust_size), 'value'.ljust(value_ljust_size), 'file'))
            for result in results:
                if self.isItemToWrite(result['value']) is True:
                    # print("tag: %s, value %s, sale %s\n" %(tag, result['value'], result['sale']))
                    out.write('%s%s%s%s\n' % (tag.ljust(tag_ljust_size), result['sale'].ljust(sale_ljust_size), result['value'].ljust(value_ljust_size), result['file']))
        result_files[OpenFileType.TXT] = txt_file

    def onSearchBtnClicked(self):
        QApplication.setOverrideCursor(Qt.WaitCursor)
        self.te_message.clear()
        self.te_result.clear()
        self.open_file_dialog.close()
        if self.validateOptions():
            # log_notice('Search is starting ...')
            infos = []
            find_file_thread = Thread(target=self.getFilesInBranch, args=(self.le_branch.text(), EXTENSIONS, infos))
            find_file_thread.start()
            find_file_thread.join()
            CSCSearch.infos = infos
            log_notice("Infos:")
            log_notice(CSCSearch.infos)
            results = []
            get_result_thread = Thread(target=self.getResult, args=(CSCSearch.infos, results))
            get_result_thread.start()
            get_result_thread.join()
            CSCSearch.results = results
            # log_notice("Results:")
            # log_notice(CSCSearch.results)
            # log_notice('Writing result to file ...')
            write_output_thread = Thread(target=self.writeOutput, args=(CSCSearch.results, CSCSearch.result_files))
            write_output_thread.start()
            write_output_thread.join()
            # log_notice("Result files:")
            # log_notice(CSCSearch.result_files)
            # Print result
            f = open(CSCSearch.result_files[OpenFileType.TXT], "r")
            self.te_result.setText(f.read())
            log_notice('Output is written to %s and %s' % (CSCSearch.result_files[OpenFileType.CSV], CSCSearch.result_files[OpenFileType.TXT]))
            # log_notice('Search is finished')
        QApplication.restoreOverrideCursor()

        # Show open file dialog
        do_not_show_cb_setting = self.settings.value('do_not_show_cb')
        if do_not_show_cb_setting is None or do_not_show_cb_setting == 'false':
            self.open_file_dialog.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = CSCSearch()
    window.show()
    settings = QSettings
    sys.exit(app.exec_())
