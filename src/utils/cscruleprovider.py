class CscRuleProviderException(Exception):
    def __init__(self, message):
        super(CscRuleProviderException, self).__init__(message)


class CscRuleProvider:
    def __init__(self):
        self.m_dict = {}

    def __del__(self):
        self.m_dict.clear()

    def add(self, rule, validator):
        """ Add validator associtated with @rule
        Each rule has each validator function
        """
        self.m_dict[rule] = validator

    def remove(self, rule):
        try:
            del self.m_dict[rule]
        except KeyError:
            raise CscRuleProviderException("Key '%s' not found" % (rule))

    def clear(self):
        self.m_dict.clear()

    def execute(self, rule, file, info):
        """ Execute validator function of @rule with input data @file and @info
        @file: file need to validate
        @info: features of device
        """
        self.m_dict[rule](file).validate(info)
