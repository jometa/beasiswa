import math

EULER = math.e
'''
    Fuzzy Membership Functions Modules (Discrete Version).
'''

class DiscretePlot:
    def plot(self):
        return [ (x, self(x)) for x in range(self.low, self.high) ]
    
    def cog(self):
        xy = self.plot()
        nom = sum( x * y for x, y in xy )
        den = sum( y for _, y in xy )
        den = 1 if den == 0 else den
        return nom * 1.0 / den

class JoinMF(DiscretePlot):
    def __init__(self, *fs):
        self.fs = fs
        self.low = min( g.low for g in self.fs )
        self.high = max( g.high for g in self.fs )
    
    def __call__(self, x):
        return max( f(x) for f in self.fs )

class TrapRMF(DiscretePlot):
    def __init__(self, c, d, low, high, cut=1):
        self.c = c
        self.d = d
        self.low = low
        self.high = high
        self.cut = cut
    
    def __call__(self, x):
        result = 0
        if x <= self.c: result = 1.0
        if self.c <= x <= self.d: result = 1.0 * (self.d - x) / (self.d - self.c)
        if self.d <= x: result = 0

        return min(self.cut, result)
    
    def clip(self, cut):
        return TrapRMF(self.c, self.d, self.low, self.high, cut=cut)

class TrapLMF(DiscretePlot):
    def __init__(self, a, b, low, high, cut=1):
        self.a = a
        self.b = b
        self.low = low
        self.high = high
        self.cut = cut
    
    def __call__(self, x):
        result = 0
        if x <= self.a: result = 0
        if self.a <= x <= self.b: result = 1.0 * (x - self.a) / (self.b - self.a)
        if self.b <= x: result = 1.0

        return min(self.cut, result)
    
    def clip(self, cut):
        return TrapLMF(self.a, self.b, self.low, self.high, cut=cut)

class TrapMF(DiscretePlot):
    def __init__(self, a, b, c, d, low, high, cut=1):
        self.a = a
        self.b = b
        self.c = c
        self.d = d
        self.low = low
        self.high = high
        self.cut = cut
    
    def __call__(self, x):
        result = 0
        if x <= self.a: result = 0
        if self.a <= x <= self.b: result = 1.0 * (x - self.a) / (self.b - self.a)
        if self.b <= x <= self.c: result = 1.0
        if self.c <= x <= self.d: result = 1.0 * (self.d - x) / (self.d - self.c)
        if self.d <= x: result = 0

        return min(self.cut, result)
    
    def clip(self, cut):
        return TrapMF(self.a, self.b, self.c, self.d, self.low, self.high, cut=cut)

class GaussMF(DiscretePlot):
    def __init__(self, c, theta, low, high, cut=1):
        self.c = c
        self.theta = theta
        self.low = low
        self.high = high
        self.cut = cut
    
    def __call__(self, x):
        p1 = -1 * 0.5 * pow(( x - self.c ) / self.theta * 1.0, 2)
        result = pow(EULER, p1)
        return min(self.cut, result)

    def clip(self, clip):
        return GaussMF(self.c, self.theta, self.low, self.high, cut=clip)

class TriangleMF(DiscretePlot):
    def __init__(self, a, b, c, low, high, cut=1):
        self.a = a
        self.b = b
        self.c = c
        self.low = low
        self.high = high
        self.cut = cut

    def __call__(self, x):
        result = 0
        if x <= self.a: result = 0
        if self.a <= x <= self.b: result = 1.0 * (x - self.a) / (self.b - self.a)
        if self.b <= x <= self.c: result = 1.0 * (self.c - x) / (self.c - self.b)
        if self.c <= x: result = 0

        return min(self.cut, result)

    def clip(self, cut):
        return TriangleMF(self.a, self.b, self.c, self.low, self.high, cut=cut)

if __name__ == '__main__':
    f1 = TriangleMF(0, 25, 50, 0, 100)
    f2 = GaussMF(50, 20, 0, 100)

    _f1 = f1.clip(0.9)
    _f2 = f2.clip(0.3)

    g = JoinMF(_f1, _f2)
    print(g.plot())