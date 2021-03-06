from . import memberships as mem
from . import fuzzmf
import csv

class Case:
    def __init__(self, ipk=1, tan=2, pot=1_000_000):
        self.ipk = ipk
        self.tan = tan
        self.pot = pot

def _target(level, pairs):
    for lev, _ in pairs:
        if lev == level: return _
    levels = [ lev for lev, _ in pairs ]
    raise Exception('{} level not found. Available levels: {}'.format(level, levels))

def create_memf(varname, level):
    fvar = getattr(mem, varname)
    small_case_vname = varname.lower()
    def f(case):
        input = getattr(case, small_case_vname)
        return _target(level, fvar(input))
    return f

def create_rule_func(memfuncs, outputf, level):
    def f(case):
        xs = [ g(case) for g in memfuncs ]
        cut = min(xs)
        return outputf.level(level).clip(cut)
    return f

def load_rules(fname='fuzz/rules.txt'):
    rules = []
    with open(fname) as f:
        lines = f.readlines()
        for line in lines:
            ant, cons = ( s.strip() for s in line.split('->'))
            ants = [
                tuple( v.strip() for v in s.split('_') )
                for s in ant.split(',') 
            ]
            memfuncs = [ create_memf(varname, level) for varname, level in ants ]
            
            # Handle consequence
            cvar, clevel = cons.split('_')
            cvar, clevel = cvar.strip(), clevel.strip()
            outputf = getattr(mem, cvar)

            rule = create_rule_func(memfuncs, outputf, clevel)
            rules.append(rule)
    return rules