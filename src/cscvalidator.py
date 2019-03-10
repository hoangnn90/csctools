from PyQt5 import uic, QtWidgets, QtGui
import sys
import ctypes
from utils import xmlutils, logutils, const, cscruleprovider, cscrulevalidator, cscrulemap, cscexception
from utils.p4helper import P4Helper, P4HelperException
from utils.cscruleprovider import CscRuleProvider, CscRuleProviderException
from utils.cscrulemap import CscRuleMap, CscRuleMapException
from utils.cscrulevalidator import CscRuleValidatorException

tool_version = "1.00"
UI_FILE = "ui\cscvalidator.ui"
ICON_FILE = "ui\cscvalidator.png"

import sys, os 
def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

class CSCValidator(QtWidgets.QDialog):
    def __init__(self):
        super(CSCValidator, self).__init__()
        self.setupUI()
        self.setupLog()
        self.m_provider = self.setupValidator()
        self.m_map = self.setupRuleMap()

    def setupUI(self):
        myappid = 'mycompany.myproduct.subproduct.version' # arbitrary string
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        uic.loadUi(resource_path(UI_FILE), self)
        self.setWindowIcon(QtGui.QIcon(resource_path(ICON_FILE)))
        self.label_version.setText(self.label_version.text()  + tool_version)
        self.pb_go.clicked.connect(self.onGoBtnClicked)
        self.pb_validate.clicked.connect(self.onValidateBtnClicked)
        self.cb_rule_file.currentIndexChanged.connect(self.onFileBoxChanged)
        self.cb_sale.currentIndexChanged.connect(self.onSaleCodeChanged)
        self.le_branch.textChanged.connect(self.onBranchChanged)
        self.cb_ims_supported.stateChanged.connect(self.onIMSSupportedChanged)
        self.cb_prj_type.currentIndexChanged.connect(self.onProjectTypeChanged)
        self.cb_dev_type.currentIndexChanged.connect(self.onDeviceTypeChanged)
        self.cb_sim_type.currentIndexChanged.connect(self.onSIMTypeChanged)

    def setupLog(self):
        sys.stdout = logutils.Logging(newText=self.onUpdateText)

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

    def onUpdateText(self, text):
        cursor = self.te_message.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        # cursor.insertText(text)
        cursor.insertHtml(text)
        self.te_message.setTextCursor(cursor)
        self.te_message.ensureCursorVisible()

    def onFileBoxChanged(self):
        self.cb_sale.clear()
        self.pb_validate.setEnabled(False)
        self.te_message.clear()

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

    def validateInput(self):
        if not self.le_server.text():
            logutils.log_error("Server address is empty, please specify server address !")
            return False
        if not self.le_user.text():
            logutils.log_error("Username is empty, please specify username !")
            return False
        if not self.le_password.text():
            logutils.log_error("Password is empty, please specify password !")
            return False
        if not self.le_wsp.text():
            logutils.log_error("Workspace is empty, please specify workspace !")
            return False
        if not self.le_branch.text():
            logutils.log_error("Branch is empty, please specify branch !")
            return False
        if not self.cb_rule_file.currentText():
            logutils.log_error("File is not selected, please specify file need to be checked")
            return False
        return True

    def connecToPerforce(self):
        server = self.le_server.text()
        user_name = self.le_user.text()
        password = self.le_password.text()
        client = self.le_wsp.text()
        try:
            self.p4 = P4Helper(server, user_name, password, client)
        except P4HelperException as e:
            logutils.log_error(e)
            return False
        return True

    def updateSale(self):
        # Update sale to sale list
        branch = self.le_branch.text()
        rule_file = self.cb_rule_file.currentText()
        is_sale_found = False
        branchs = []
        try:
            branchs = self.p4.getAllDepotBranch(branch)
        except P4HelperException as e:
            logutils.log_error(e)
            return
        for b in branchs:
            if self.p4.isDepotFile(b + rule_file) is True:
                sale = self.p4.getSaleCodeFromBranch(b)
                if sale is not None:
                    is_sale_found = True
                    if self.cb_sale.findText(sale) == -1:
                        self.cb_sale.addItem(sale)
                        self.pb_validate.setEnabled(True)
        if is_sale_found is False:
            logutils.log_error("Could not find any file '%s' in branch '%s'" % (rule_file, branch))

    def onGoBtnClicked(self):
        self.te_message.clear()
        if self.validateInput() and self.connecToPerforce():
            self.updateSale()

    def onValidateBtnClicked(self):
        rule_file = self.cb_rule_file.currentText()
        sale = self.cb_sale.currentText()
        branch = self.le_branch.text()
        try:
            rules = self.m_map.get(rule_file)
            branchs = self.p4.getAllDepotBranch(branch)
            for b in branchs:
                p4_file = b + rule_file
                if sale in b and self.p4.isDepotFile(p4_file) is True:
                    self.p4.syncP4File(p4_file)
                    for rule in rules:
                        try:
                            local_path = self.p4.getLocalFilePath(p4_file)
                            self.m_provider.execute(rule, local_path, {})
                        except P4HelperException as e:
                            logutils.log_error("Could not find local file of %s. Error is %s" %(p4_file, str(e)))
            logutils.log_notice("Validation is done")
        except CscRuleMapException:
            logutils.log_error("Rule file '%s' is not setup. Please check setupRuleMap()" % (rule_file))
        except CscRuleValidatorException as e:
            logutils.log_error("Validate file '%s' with rule '%s' failed with error '%s'" % (p4_file, rule_file, str(e)))


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = CSCValidator()
    window.show()
    sys.exit(app.exec_())
