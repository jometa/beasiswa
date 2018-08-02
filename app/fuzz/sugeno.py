# Implement sugeno fuzzy inference
from . import memberships as mem
from . import fuzzmf
import csv

# The path of this rules will change depends on
# the position you run this script
# If you run it as: python3.6 -m fuzz.sugeno
#     RPATH must be "fuzz/rules-sugeno.txt"
# If you run it as: python3.6 -m app.fuzz.sugeno
#     RPATH must be "app/fuzz/rules-sugeno.txt"

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

def create_rule_func(memfuncs, target):
    def f(case):
        xs = [ g(case) for g in memfuncs ]
        w = min(xs)
        return w, target
    return f

def load_rules(fname='app/fuzz/rules-sugeno.txt'):
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
            _, z = cons.split('=')
            z = float(z)

            rule = create_rule_func(memfuncs, z)
            rules.append(rule)
    return rules

def sugeno(case):
    rules = load_rules()
    result = [ r(case) for r in rules ]

    # Just weighted average
    nom = sum( w * z for w, z in result )
    den = sum( w for w, z in result )

    return nom / den

if __name__ == '__main__':
    case = Case(ipk=3.6, tan=4, pot=3_000_000)
    print(sugeno(case))