'''
    Fuzzy Operators module.
'''

def stand(*args):
    return min(*args)

def stor(*args):
    return max(*args)

def stnot(A):
    return 1 - A
