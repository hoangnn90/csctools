class CscRuleMapException(Exception):
    def __init__(self, message):
        super(CscRuleMapException, self).__init__(message)


class CscRuleMap:
    def __init__(self):
        self.m_dict = {}

    def __del__(self):
        self.m_dict.clear()

    def add(self, csc_file, list_rule):
        """ Add @list_rule to rule map with index @csc_file
        A CSC file can contains multiple rules
        """
        self.m_dict[csc_file] = list_rule

    def get(self, csc_file):
        """ Get rule list from rule map with index @csc_file
        """
        try:
            return self.m_dict[csc_file]
        except KeyError:
            raise CscRuleMapException("Key '%s' not found" % (csc_file))

    def remove(self, csc_file):
        """ Remove rule list of @csc_file from rule map
        """
        try:
            del self.m_dict[csc_file]
        except KeyError:
            raise CscRuleMapException("Key '%s' not found" % (csc_file))

    def clear(self):
        self.m_dict.clear()
