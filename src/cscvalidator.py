from PyQt5 import uic, QtCore, QtGui, QtCore, QtWidgets
from PyQt5.QtGui import QIcon, QTextCursor
from PyQt5.QtCore import QSettings, Qt, QCoreApplication
from PyQt5.QtWidgets import QApplication, QDialog, QMainWindow
import sys
import ctypes
from threading import Thread
from utils import cscutils, const, dictsutils, directoryutils, xmlutils, logutils, cscruleprovider, cscrulevalidator, cscrulemap, cscexception
from utils.p4helper import P4Helper
from utils.repo import CSCRepo, CSCRepoException, CSCRepoInvalidRepoFileException, CSCRepoInvalidRepoBranchException, CSCRepoFailedToSyncException, CSCRepoFailedToGetWspDirPath
from utils.cscexception import CSCException, CSCFailOperation
from utils.xmlutils import XmlHelper, XmlHelperException
from utils.logutils import Logging, log_error, log_info, log_notice, log_warning
from utils.cscruleprovider import CscRuleProvider, CscRuleProviderException
from utils.cscrulemap import CscRuleMap, CscRuleMapException
from utils.cscrulevalidator import CscRuleValidatorException
from utils.stringutils import isNotBlank


VERSION = "0.01"
UI_FILE = "ui\cscvalidator.ui"
ICON_FILE = "ui\cscvalidator.png"

import sys, os 
def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

class CSCValidator(QtWidgets.QDialog):
    infos = []
    def __init__(self):
        super(CSCValidator, self).__init__()
        self.settings = QSettings('csctools', 'cscvalidator')
        self.setupUI()
        self.setupLog()
        self.m_provider = self.setupValidator()
        self.m_map = self.setupRuleMap()
    
    def closeEvent(self, event):
        self.settings.setValue('server', self.le_server.text())
        self.settings.setValue('user', self.le_user.text())
        self.settings.setValue('password', self.le_password.text())
        self.settings.setValue('wsp', self.le_wsp.text())
        self.settings.setValue('branch', self.le_branch.text())
        self.settings.setValue('rule_file', self.cb_rule_file.currentText())

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
        if isNotBlank(self.settings.value('rule_file')):
            index = self.cb_rule_file.findText(self.settings.value('rule_file'), QtCore.Qt.MatchFixedString)
            if index >= 0:
                self.cb_rule_file.setCurrentIndex(index)

    def setupCallback(self):
        self.pb_go.clicked.connect(self.onGoBtnClicked)
        self.pb_validate.clicked.connect(self.onValidateBtnClicked)
        self.cb_rule_file.currentIndexChanged.connect(self.onRuleFileChanged)
        self.cb_sale.currentIndexChanged.connect(self.onSaleCodeChanged)
        self.le_branch.textChanged.connect(self.onBranchChanged)
        self.le_wsp.textChanged.connect(self.onClientWorkspaceChanged)
        self.cb_ims_supported.stateChanged.connect(self.onIMSSupportedChanged)
        self.cb_prj_type.currentIndexChanged.connect(self.onProjectTypeChanged)
        self.cb_dev_type.currentIndexChanged.connect(self.onDeviceTypeChanged)
        self.cb_sim_type.currentIndexChanged.connect(self.onSIMTypeChanged)
    
    def setupUI(self):
        myappid = 'mycompany.myproduct.subproduct.version' # arbitrary string
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        uic.loadUi(resource_path(UI_FILE), self)
        self.setWindowIcon(QIcon(resource_path(ICON_FILE)))
        self.label_version.setText(self.label_version.text() + VERSION)
        self.restoreSettings()
        self.setupCallback()
    
    

    def setupLog(self):
        sys.stdout = Logging(newText=self.onLogChanged)

    def setupValidator(self):
        provider = CscRuleProvider()
        provider.add(const.parent_child_rule, cscrulevalidator.CSCParentChildRuleValidator)
        provider.add(const.condition_rule, cscrulevalidator.CSCConditionRuleValidator)
        provider.add(const.measurement_rule, cscrulevalidator.CSCMeasurementRuleValidator)
        provider.add(const.unusedtag_rule, cscrulevalidator.CSCUnUsedTagRuleValidator)
        provider.add(const.profilehandle_rule, cscrulevalidator.CSCProfileHandleRuleValidator)
        return provider

    def setupRuleMap(self):
        map = CscRuleMap()
        # TODO: add more rule here
        map.add(const.customer, [
            const.parent_child_rule,
            const.measurement_rule,
            const.condition_rule,
            const.unusedtag_rule,
            const.profilehandle_rule
        ])
        map.add(const.csc_feature, [const.unusedtag_rule])
        map.add(const.csc_feature_network, [const.unusedtag_rule])
        map.add(const.default_application_order, [const.unusedtag_rule])
        map.add(const.default_workspace, [const.unusedtag_rule])
        map.add(const.apps, [const.unusedtag_rule])
        map.add(const.others, [const.unusedtag_rule])
        return map

    def onLogChanged(self, text):
        cursor = self.te_message.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertHtml(text)
        self.te_message.setTextCursor(cursor)
        self.te_message.ensureCursorVisible()

    def onRuleFileChanged(self):
        self.cb_sale.clear()
        self.pb_validate.setEnabled(False)
        self.te_message.clear()
        log_notice("File check is changed, please click 'Go' button to continue!")

    def onSaleCodeChanged(self):
        self.te_message.clear()

    def onBranchChanged(self):
        self.cb_sale.clear()
        self.pb_validate.setEnabled(False)

    def onProjectTypeChanged(self):
        self.te_message.clear()

    def onDeviceTypeChanged(self):
        self.te_message.clear()

    def onSIMTypeChanged(self):
        self.te_message.clear()

    def onIMSSupportedChanged(self):
        self.te_message.clear()
	
    def onClientWorkspaceChanged(self):
        self.te_message.clear()
        log_error("Workspace is changed, please click 'Go' button to continue!")
        self.pb_validate.setEnabled(False)

    def validateInput(self):
        if not self.le_server.text():
            log_error("Server address is empty, please specify server address !")
            return False
        if not self.le_user.text():
            log_error("Username is empty, please specify username !")
            return False
        if not self.le_password.text():
            log_error("Password is empty, please specify password !")
            return False
        if not self.le_wsp.text():
            log_error("Workspace is empty, please specify workspace !")
            return False
        if not self.le_branch.text():
            log_error("Branch is empty, please specify branch !")
            return False
        if not self.cb_rule_file.currentText():
            log_error("File is not selected, please specify file need to be checked")
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

    def updateSale(self, infos):
        # Update sale to sale list
        sales = []
        branch = self.le_branch.text()
        rule_file = self.cb_rule_file.currentText()
        branchs = []
        try:
            branchs = self.repo.getAllRepoBranch(branch)
        except CSCRepoException as e:
            log_error(e)
        for b in branchs:
            if self.repo.isRepoFile(b + rule_file) is True:
                sale = cscutils.getSaleCodeFromBranch(b)
                if sale is not None:
                    sales.append(sale)
                    info = {'sale': sale, 'branch': b}
                    infos.append(info)
        sales = set(sales)
        if len(sales) == 0:
            log_error("Could not find any file '%s' in branch '%s'" % (rule_file, branch))
        else:
            for sale in sorted(sales):
                if self.cb_sale.findText(sale) == -1:
                    self.cb_sale.addItem(sale)
                    self.pb_validate.setEnabled(True)
        if len(sales) >= 2 and self.cb_sale.findText('All') == -1:
            self.cb_sale.insertItem(0, 'All')
            self.cb_sale.setCurrentIndex(0)
        return infos

    def onGoBtnClicked(self):
        CSCValidator.infos = []
        QApplication.setOverrideCursor(Qt.WaitCursor)
        self.te_message.clear()
        if self.validateInput():
            try:
                if self.connecToPerforce():
                    infos = []
                    update_sale_thread = Thread(target=self.updateSale, args=[infos])
                    update_sale_thread.start()
                    update_sale_thread.join()
                    CSCValidator.infos = infos
            except CSCRepoException as e:
                log_error(str(e))
                return
        
        QApplication.restoreOverrideCursor()

    def validate(self, sale, rule_file, infos):
        try:
            rules = self.m_map.get(rule_file)
            for info in infos:
                if (sale == 'All') or (sale != 'All' and info['sale'] == sale):
                    repo_file = info['branch'] + rule_file
                    self.repo.syncFile(repo_file)
                    for rule in rules:
                        try:
                            local_path = self.repo.getLocalFilePath(repo_file)
                            self.m_provider.execute(rule, local_path, {})
                        except CSCRepoException as e:
                            log_error("Could not find local file of %s. Error is %s" %(repo_file, str(e)))
            log_notice("Validation is done. Please check above error(s) if any!")
        except CscRuleMapException:
            log_error("Rule file '%s' is not setup. Please check setupRuleMap()" % (rule_file))
        except CscRuleValidatorException as e:
            log_error("Validate file '%s' with rule '%s' failed with error '%s'" % (repo_file, rule_file, str(e)))

    def onValidateBtnClicked(self):
        QApplication.setOverrideCursor(Qt.WaitCursor)
        rule_file = self.cb_rule_file.currentText()
        sale = self.cb_sale.currentText()
        validate_thread = Thread(target=self.validate, args=(sale, rule_file, CSCValidator.infos))
        validate_thread.start()
        validate_thread.join()
        QApplication.restoreOverrideCursor()

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = CSCValidator()
    window.show()
    sys.exit(app.exec_())
