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
        print('xs: ', xs)
        cut = min(xs)
        print('cut: ', cut)
        input()
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

def mamdani(case):
    rules = load_rules()
    result = [ r(case) for r in rules ]
    # print( [ r.cut for r in rules ] )
    # input()
    outputmf = fuzzmf.JoinMF(*result)
    # print( outputmf.plot() )
    # exit()
    cuts = [ r.cut for r in result ]

    # Find maximum cut
    maxc = max([ r.cut for r in result ])
    print( [ r.cut for r in result ] )
    print(cuts)
    # print( result[0].d )
    # print(maxc)
    # print(resu)

    # Get x that has max membership function
    xmaxc = [ x for x, u in outputmf.plot() if u == maxc ]
    print(xmaxc)

    tot_x = sum( xmaxc )
    count = len( xmaxc )

    print('tot_x: ', tot_x)
    print('count: ', count)

    prob = tot_x * 1.0 / count
    return prob

if __name__ == '__main__':
    case = Case(ipk=3.6, tan=4, pot=3_000_000)
    print(mamdani(case))
