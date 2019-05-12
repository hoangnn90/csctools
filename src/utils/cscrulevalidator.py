from utils.xmlutils import XmlHelper, XmlHelperException


class CscRuleValidatorException(Exception):
    def __init__(self, message):
        super(CscRuleValidatorException, self).__init__(message)


class CscRuleValidator:
    """ Parent CSC rule validator
    """
    def __init__(self, file):
        try:
            self.m_helper = XmlHelper(file)
        except XmlHelperException as e:
            raise CscRuleValidatorException(str(e))


class CSCParentChildRuleValidator(CscRuleValidator):
    """ Parent-child rule validator
    """
    def __init__(self, file):
        self.file=file
        CscRuleValidator.__init__(self, file)

    def validate(self, info):
        self.m_helper.validateParentChildRule(self.file, info)


class CSCConditionRuleValidator(CscRuleValidator):
    """ Condition rule validator
    """
    def __init__(self, file):
        CscRuleValidator.__init__(self, file)

    def validate(self, info):
        self.m_helper.validateConditionRule(info)


class CSCMeasurementRuleValidator(CscRuleValidator):
    """ Measurement rule validator
    """
    def __init__(self, file):
        self.file=file
        CscRuleValidator.__init__(self, file)

    def validate(self, info):
        self.m_helper.validateMeasurementRule(self.file, info)


class CSCUnUsedTagRuleValidator(CscRuleValidator):
    """ Unused tag rule validator
    """
    def __init__(self, file):
        self.file=file
        CscRuleValidator.__init__(self, file)

    def validate(self, info):
        self.m_helper.validateUnusedRule(self.file, info)

class CSCMatchingTagRuleValidator(CscRuleValidator):
    """ Matching tag rule validator
    """
    def __init__(self, file):
        self.file=file
        CscRuleValidator.__init__(self, file)

    def validate(self, info):
        self.m_helper.validateMatchingRule(self.file, info)

class CSCProfileHandleRuleValidator(CscRuleValidator):
    """ Profile handle rule validator
    """
    def __init__(self, file):
        self.file=file
        CscRuleValidator.__init__(self, file)

    def validate(self, info):
        self.m_helper.validateProfileHandle(self.file, info)