from utils.salecode import sales

SALE_CODE_POSITION_IN_BRANCH = 8 #//PEACE_CSC/Strawberry/EXYNOS5/a50/OMC/OLM/XXV/

def getSaleCodeFromBranch(branch):
    """Get sale code from @branch name
    """
    values = branch.split('/')
    for i in range(len(sales)):
        if len(values) >= SALE_CODE_POSITION_IN_BRANCH and sales[i] == values[SALE_CODE_POSITION_IN_BRANCH-1]:
            if sales[i] != 'EUR': # //PEACE_CSC/Strawberry/EXYNOS5/a5xlte_MM/EUR/ATO/
                return sales[i]
            # //PEACE_CSC/Strawberry/EXYNOS5/a5xlte_MM/OXX/EUR/, # //PEACE_CSC/Strawberry/EXYNOS5/a5xlte_MM/OXA/EUR/, # //PEACE_CSC/Strawberry/EXYNOS5/a5xlte_MM/OXM/EUR/,
            # //PEACE_CSC/Strawberry/EXYNOS5/a5xlte_MM/GGSM/EUR/, # //PEACE_CSC/Strawberry/EXYNOS5/a5xlte_MM/EUR/EUR/
            elif values[SALE_CODE_POSITION_IN_BRANCH-2] in {'OXX', 'OXA', 'OXM','GGSM', 'EUR'}:
                return sales[i]
            else:
                return None # //PEACE_CSC/Strawberry/EXYNOS5/a50/OMC/EUR/ATO/
        if len(values) >= SALE_CODE_POSITION_IN_BRANCH+1 and sales[i] == values[SALE_CODE_POSITION_IN_BRANCH]: # //PEACE_CSC/Strawberry/EXYNOS5/a50/OMC/OLM/ATO/
            return sales[i]
    return None

def getSaleCodeFromKeyStringFile(file):
    values = file.split('_')
    for i in range(len(sales)):
        if sales[i] == values[0]:
            return sales[i]
    return None

def isRepoSaleCodeRootBranch(branch):
    values = branch.split('/')
    sale = getSaleCodeFromBranch(branch)
    if sale is not None and values[len(values)-2] == sale:
        return True
    return False

def getRepoBranchByFile(repo_branch, file_name):
    if file_name == 'keystrings.dat':
        return repo_branch + 'etc/'
    return repo_branch

def getWspBranchByFile(wsp_branch, file_name):
    if file_name == 'keystrings.dat':
        return wsp_branch + 'etc\\'
    return wsp_branch

def getCSCFileBySale(file_name, sale):
    if file_name == 'keystrings.dat':
        return sale + '_' + file_name
    return file_name