# Define the membership functions for system.

from . import fuzzmf

# Fuzzy Variable
# name: name of this FuzzyVar
# variables: 2-tuple of 'level' and membership function
class FuzzyVar:
    def __init__(self, name, variables):
        self.name = name
        self.variables = variables
    
    def __call__(self, crisp_value):
        return [
          (level, mf(crisp_value))
          for level, mf in self.variables
        ]

    def level(self, lev):
        for l, func in self.variables:
            if l == lev: return func
        raise Exception('Can not find level: {}'.format(lev))


IPK = FuzzyVar(
  name='IPK',
  variables=[
    ('low', fuzzmf.TrapRMF(3, 3.5, 0, 4)),
    ('mid', fuzzmf.TriangleMF(3, 3.5, 4, 0, 4)),
    ('high', fuzzmf.TrapLMF(3.5, 4, 0, 4))
  ]
)

TAN = FuzzyVar(
  name='TAN',
  variables=[
    ('low', fuzzmf.TrapRMF(2, 4, 0, 6)),
    ('mid', fuzzmf.TriangleMF(2, 4, 6, 0, 6)),
    ('high', fuzzmf.TrapLMF(4, 6, 0, 6))
  ]
)

POT = FuzzyVar(
  name='POT',
  variables=[
    ('low', fuzzmf.TrapRMF(1_000_000, 3_000_000, 0, 5_000_000)),
    ('mid', fuzzmf.TriangleMF(1_000_000, 3_000_000, 5_000_000, 0, 5_000_000)),
    ('high', fuzzmf.TrapLMF(3_000_000, 5_000_000, 0, 5_000_000))
  ]
)

# Just for mamdani and tsukamoto
PLO = FuzzyVar(
  name='PLO',
  variables=[
    ('low', fuzzmf.TrapRMF(50, 100, 0, 100)),
    ('high', fuzzmf.TrapLMF(50, 100, 0, 100))
  ]
)
