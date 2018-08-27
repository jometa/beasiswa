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
    class Cons():
        def __init__(self, level, outputmf):
            self.level = level
            self.outputmf = outputmf
        def __call__(self, case):
            xs = [ g(case) for g in memfuncs ]
            cut = min(xs)
            return outputf.level(level).clip(cut)
    return Cons(level, outputf)

def load_rules(fname='app/fuzz/rules.txt'):
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

def mamdani(case):
    rules = load_rules()
    result = [ r(case) for r in rules ]
    print([r.level for r in rules])
    outputmf = fuzzmf.JoinMF(*result)

    maxv = -1
    cons_rule = None
    level = None
    for index, r in enumerate(result):
        if r.cut > maxv:
            maxv = r.cut
            cons_rule = rules[index]
            level = rules[index].level

    # print()
    return cons_rule.outputmf.level(level).inverse(maxv)

    # maxc = max([ r.cut for r in result ])
    # # Get x that has max membership function
    # xmaxc = [ x for x, u in outputmf.plot() if u == maxc ]

    # tot_x = sum( xmaxc )
    # count = len( xmaxc )

    # prob = tot_x * 1.0 / count
    # return prob

if __name__ == '__main__':
    case = Case(ipk=3.2, tan=3, pot=2_000_000)
    print(mamdani(case))
