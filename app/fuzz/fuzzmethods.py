from . import memberships as mem
from . import fuzzmf
import csv
import os
import os.path
import timeit

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

def sugeno_create_rule_func(memfuncs, target):
    def f(case):
        xs = [ g(case) for g in memfuncs ]
        w = min(xs)
        return w, target
    return f


RPATHS = {
  'mamdani': 'fuzz/rules.txt',
  'tsukamoto': 'fuzz/rules.txt',
  'sugeno': 'fuzz/rules-sugeno.txt',
}


# If running from top level directory
curr_dir = os.getcwd()
# print(os.path.split(curr_dir)[-1])
if os.path.split(curr_dir)[-1] != 'app':
    for k, v in RPATHS.items():
        RPATHS[k] = os.path.join('app', v)
# print(RPATHS)

class FuzzMethod:
    def __init__(self, rpath=''):
        self.rpath = rpath
    
    def load_rules(self):
        rules = []
        with open(self.rpath) as f:
            lines = f.readlines()
            for line in lines:
                rule = self.create_rule(line)
                rules.append(rule)
        self.rules = rules

    def create_rule(self, line):
        raise Exception('Not implemented')
    
    def run(self, case):
        raise Exception('Not implemented')

class Mamdani(FuzzMethod):

    def create_rule(self, line):
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
        return rule

    def run(self, case):
        result = [ r(case) for r in self.rules ]
        # print([r.cut for r in result])
        outputmf = fuzzmf.JoinMF(*result)

        maxc = max([ r.cut for r in result ])
        # print([ (x, u) for x, u in outputmf.plot() if u == maxc ])
        # Get x that has max membership function
        xmaxc = [ x for x, u in outputmf.plot() if u == maxc ]

        tot_x = sum( xmaxc )
        count = len( xmaxc )

        prob = tot_x * 1.0 / count
        return prob

class Tsukamoto(Mamdani):
    def run(self, case):
        result = [ r(case) for r in self.rules ]

        # Apply weighted defuzzification.
        nom = sum([ r.cut * r.inverse(r.cut) for r in result ])
        den = sum([ r.cut for r in result ])
        return 1.0 * nom / den

class Sugeno(FuzzMethod):

    def create_rule(self, line):
        ant, cons = ( s.strip() for s in line.split('->'))
        ants = [
            tuple( v.strip() for v in s.split('_') )
            for s in ant.split(',') 
        ]
        memfuncs = [ create_memf(varname, level) for varname, level in ants ]
        # Handle consequence
        _, z = cons.split('=')
        z = float(z)

        rule = sugeno_create_rule_func(memfuncs, z)
        return rule

    def run(self, case):
        result = [ r(case) for r in self.rules ]
        # Just weighted average
        nom = sum( w * z for w, z in result )
        den = sum( w for w, z in result )

        return nom / den

mamdani = Mamdani(RPATHS['mamdani'])
tsukamoto = Tsukamoto(RPATHS['tsukamoto'])
sugeno = Sugeno(RPATHS['sugeno'])

for met in (mamdani, tsukamoto, sugeno):
    met.load_rules()

def compare_methods(case, n=1000):
    # Provide scope for timeit
    scope = {
      'mamdani': mamdani,
      'tsukamoto': tsukamoto,
      'sugeno': sugeno,
      # And the case
      'case': case
    }
    m_result = timeit.timeit('mamdani.run(case)', globals=scope, number=n)
    t_result = timeit.timeit('tsukamoto.run(case)', globals=scope, number=n)
    s_result = timeit.timeit('sugeno.run(case)', globals=scope, number=n)

    return {
      'mamdani': m_result,
      'tsukamoto': t_result,
      'sugeno': s_result
    }

if __name__ == '__main__':
    case = Case(ipk=3.6, tan=4, pot=3_000_000)
    print(compare_methods(case))
