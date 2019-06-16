import os.path
import sys
sys.modules['_elementtree'] = None
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import XMLParser
from utils import const
from utils import logutils

class XmlHelperException(Exception):
    def __init__(self, message):
        super(XmlHelperException, self).__init__(message)

class LineNumberingParser(XMLParser):
    def _start_list(self, *args, **kwargs):
        # Here we assume the default XML parser which is expat
        # and copy its element position attributes into output Elements
        element = super(self.__class__, self)._start_list(*args, **kwargs)
        element._start_line_number = self.parser.CurrentLineNumber
        element._start_column_number = self.parser.CurrentColumnNumber
        element._start_byte_index = self.parser.CurrentByteIndex
        return element

    def _end(self, *args, **kwargs):
        element = super(self.__class__, self)._end(*args, **kwargs)
        element._end_line_number = self.parser.CurrentLineNumber
        element._end_column_number = self.parser.CurrentColumnNumber
        element._end_byte_index = self.parser.CurrentByteIndex
        return element

class XmlHelper(LineNumberingParser):
    """XML Helper class that manipulate XML file
    """
    def __init__(self, file):
        LineNumberingParser.__init__(self)
        self.file = file
        if not file:
            raise XmlHelperException("File is NULL")
        if os.path.isfile(file) == False:
            raise XmlHelperException("File %s is not existed" % (file))
        try:
            ET.parse(file)
        except ET.ParseError as err:
            raise XmlHelperException("%s - %s in %s" % (type(err).__name__, err, file))

    def getTree(self, file):
        """Get XML tree
        """
        return ET.parse(file, parser=LineNumberingParser())

    def getAllTag(self, file):
        """Get all tag of @file
        """
        tags = []
        tree = self.getTree(file)
        for e in tree.iter():
            if e.get("name") is None:
                # print("%s-%s\n" %(e.tag, e.text))
                pass
            else:
                # print("%s-%s\n" %(e.tag, e.get("name")))
                pass
            tags.append(e.tag)
        return tags
    
    def getAllIterator(self, file):
        """Get all iterators of @file
        """
        it_list = []
        tree = self.getTree(file)
        for it in tree.iter():
            it_list.append(it)
        return it_list

    def getAllElementAttribute(self, file, element, attribute):
        """Get all element @element of @file
        """
        attributes = []
        tree = ET.parse(file)
        root = tree.getroot()
        for e in root.findall(element):
            attributes.append(e.get(attribute))
        return attributes

    def getTagContent(self, file, tag):
        """Get value of @tag that appear 1st on file
        """
        tree = self.getTree(file)
        for e in tree.iter():
            if e.tag == tag:
                return e.text
        return None

    def getTagContents(self, file, tag):
        """Get all values of @tag on @file
        """
        contents = []
        tree = self.getTree(file)
        for e in tree.iter():
            if e.tag == tag:
                contents.append(e.text)
        contents = set(contents)
        return contents

    def countTag(self, file, tag):
        """Count the number of @tag in @file
        """
        count = 0
        tree = self.getTree(file)
        for e in tree.iter():
            if e.tag == tag:
                count += 1
        return count

    def getPair(self, file, element, first, second):
        """Get all pairs [@first, @second] of @element in @file
        """
        pairs = {}
        tree = ET.parse(file)
        root = tree.getroot()
        for m in root.findall(element):
            first_element = m.find(first)
            second_element = m.find(second)
            pairs[first_element.text] = second_element.text
        return pairs
    
    def getAllElement(self, file, element_name, child_list):
        """Get all element information tag @element_name including its child in XML file
        
        Args:
            file: XML file
            element_name: tag name of element
            child_list: list child tag of element
        
        Returns:
            A list of dictionary of element information
            Each element contains child tag and its value
        """
        element_list = []
        tree = ET.parse(file)
        root = tree.getroot()
        for element in root.iter():
            if element.tag == element_name:
                element_dict = {}
                for child in child_list:
                    if element.find(child) is not None:
                        element_dict[child] = element.find(child).text
                element_list.append(element_dict)
        return element_list

    def getUnUsedRules(self):
        """Get all unused tags defined in UNUSED_RULE_FILE
        """
        rules = []
        tree = ET.parse(const.UNUSED_RULE_FILE)
        root = tree.getroot()
        for e in root.findall("Rule"):
            info = {}
            info['name'] = e.get('name')
            for cond in self.getAllTag(const.UNUSED_RULE_FILE):
                if cond is not "CSCRules" and cond is not "Rule":
                    child = e.find(cond)
                    if child is not None:
                        info[cond] = child.text
            rules.append(info)
        return rules

    def getMatchingRules(self):
        """Get all matching rules defined in UNUSED_RULE_FILE
        """
        rules = []
        tree = ET.parse(const.MATCHING_RULE_FILE)
        root = tree.getroot()
        for e in root.findall("Rule"):
            info = {}
            for cond in self.getAllTag(const.MATCHING_RULE_FILE):
                if cond is not "CSCRules" and cond is not "Rule":
                    child = e.find(cond)
                    if child is not None:
                        info[cond] = child.text
            rules.append(info)
        return rules

    def isInfoMatchingWithRule(self, rule, info):
        """Validate if @info matched with @rule
        """
        if len(rule.keys()) == 1:
            return True
        for key in (key for key in rule if key is not "name"):
            if not info:
                return False
            if key not in info:
                return False
            if rule[key] != info[key]:
                return False
        return True

    def validateParentChildTag(self, file, parent, child):
        """Validate whether parent-child tag is valid
        """
        tree = self.getTree(file)
        tree.getroot()
        for iter in tree.iter(parent):
            value = iter.findtext(child)
            if (value == None):
                logutils.log_error("Tag '%s' not found under '%s' in '%s'" % (child, parent, self.file))
            else:
                pass

    def validateParentChildRule(self, file, info):
        """Validate parent-child rule
        """
        pairs = self.getPair(const.PARENT_CHILD_RULE_FILE, "Rule", "Parent", "Child")
        for parent, childs in pairs.items():
            tags = childs.rstrip().split(',')
            for child in tags:
                self.validateParentChildTag(file, parent, child)

    def validateConditionRule(self, info):
        """Validate measurement rule
        """

    def validateMeasurementRule(self, file, info):
        """Validate measurement rule is valid in @file with device @info
        """
        pairs = self.getPair(const.MEASUREMENT_RULE_FILE, "Rule", "Quantity", "Item")
        for quantity, item in pairs.items():
            content = self.getTagContent(file, quantity)
            if content is not None:
                value = int(content)
                count = self.countTag(file, item)
                if value == count:
                    pass
                else:
                    logutils.log_error("Tag '%s' is %d but '%s' is %d in '%s'" % (quantity, value, item, count, self.file))

    def validateUnusedRule(self, file, info):
        """Validate unused rule in @file with device @info
        """
        rules = self.getUnUsedRules()
        for rule in rules:
            if self.isInfoMatchingWithRule(rule, info) is True:
                tag_name = rule["name"]
                content = self.getTagContent(file, tag_name)
                if content is not None:
                    msg = []
                    tree = self.getTree(file)
                    if len(rule.keys()) == 1:
                        # TODO: add line number here
                        msg.append("Tag %s should NOT be used in %s" % (tag_name, self.file))
                    else:
                        msg.append("Tag %s should NOT be used in %s because:\n" % (tag_name, self.file))
                        for key in rule:
                            if key is not "name":
                                msg.append('%s - %s\n' % (key, rule[key]))
                    logutils.log_error(''.join(msg))

    def validateMatchingRule(self, file, info):
        """Validate matching tags
        """
        # rules = self.getMatchingRules()
        # for rule in rules:
        #     decl_tag = rule["Declaration"]
        #     imp_tag = rule["Implementation"]
        #     logutils.log_error("%s - %s" %(decl_tag, imp_tag))
        #     decl = self.getTagContent(file, decl_tag)
        #     imp = self.getTagContent(file, imp_tag)
        #     logutils.log_error("%s - %s" %(decl, imp))

    
    def validateProfileCount(self, file, info):
        """Validate whether value of NbNetProfile matching with profile declared in ProfileHandle with device's info @info

        Params:
            file: XML file will be validated

        Returns:
            Print NetworkName not matching
        
        """
        profile_handle_lst = self.getAllElement(file, "ProfileHandle", {"NbNetProfile", "NetworkName", "ProfBrowser", "ProfMMS", "ProfIMS", "ProfXCAP"})
        for profile_handle in profile_handle_lst:
            nb_prof = int(profile_handle['NbNetProfile'])
            declare_prof = len(profile_handle) - 2
            if(nb_prof != declare_prof):
                logutils.log_error("NetworkName '%s' declared %d NbNetProfile but has %d Profile in '%s'" %(profile_handle['NetworkName'], nb_prof, declare_prof, file))
    

    def validateProfileExistence(self, file, info):
        """Validate the existing of profile declared in ProfileHandle with device's info @info
        """
        profile_handle_lst = self.getAllElement(file, "ProfileHandle", {"NetworkName", "ProfBrowser", "ProfMMS", "ProfIMS", "ProfXCAP"})
        profile_lst = self.getAllElement(file, "Profile", {"NetworkName", "ProfileName"})
        for profile_handle in profile_handle_lst:
            network_name = profile_handle['NetworkName']
            for prof_name in profile_handle.items():
                if prof_name[0] is not "NetworkName":
                    found = False
                    for profile in profile_lst:
                        if prof_name[1] == profile["ProfileName"] and network_name == profile['NetworkName']:
                            found = True
                            break
                        if found:
                            break
                    if found is False:
                        print("Profile '%s' of NetworkName '%s' is declared in ProfileHandle but not implemented in '%s'" %(prof_name[1], network_name , file))


    def validateProfileHandle(self, file, info):
        """Validate profile handle rule in file @file with device's info @info
        """
        self.validateProfileExistence(file, info)
        self.validateProfileCount(file, info)
                

