from utils.salecode import sales

SALE_CODE_POSITION_IN_BRANCH = 8 #//PEACE_CSC/Strawberry/EXYNOS5/a50/OMC/OLM/XXV/

def getSaleCodeFromBranch(branch):
    """Get sale code from @branch name
    """
    values = branch.split('/')
    for i in range(len(sales)):
        if len(values) >= SALE_CODE_POSITION_IN_BRANCH and sales[i] == values[SALE_CODE_POSITION_IN_BRANCH-1]:
            if sales[i] != 'EUR': # //depot/PEACE_CSC/Strawberry/EXYNOS5/a5xlte_MM/EUR/ATO/
                return sales[i]
            # //depot/PEACE_CSC/Strawberry/EXYNOS5/a5xlte_MM/OXX/EUR/, # //depot/PEACE_CSC/Strawberry/EXYNOS5/a5xlte_MM/OXA/EUR/, # //depot/PEACE_CSC/Strawberry/EXYNOS5/a5xlte_MM/OXM/EUR/,
            # //depot/PEACE_CSC/Strawberry/EXYNOS5/a5xlte_MM/GGSM/EUR/, # //depot/PEACE_CSC/Strawberry/EXYNOS5/a5xlte_MM/EUR/EUR/
            elif values[SALE_CODE_POSITION_IN_BRANCH-2] in {'OXX', 'OXA', 'OXM','GGSM', 'EUR'}:
                return sales[i]
            else:
                return None # //depot/PEACE_CSC/Strawberry/EXYNOS5/a50/OMC/EUR/ATO/
        if len(values) >= SALE_CODE_POSITION_IN_BRANCH+1 and sales[i] == values[SALE_CODE_POSITION_IN_BRANCH]: # //depot/PEACE_CSC/Strawberry/EXYNOS5/a50/OMC/OLM/ATO/
            return sales[i]
    return None