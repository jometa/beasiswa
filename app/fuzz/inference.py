# We model the implications as [ANTECENDENT] -> [CONSEQUENCE]
# Where ANTECENDENT is dnf of terms and CONSEQUENCE is single value fuzzy set.
# Unfold our structure:
#   ( [TERM, TERM, TERM] ^ [TERM, TERM] ) -> [TERM]
from . import fuzzop
from . import fuzzmf

class Term:
    ''' Atomic fuzzy set term 
        [name] is correspondent (type) name of this term.
        [ling] is fuzzy linguistic category of this (type) name.
        [f] is membership functions
    '''
    def __init__(self, name, ling, f):
        self.name = name
        self.ling = ling
        self.f = f
    
    def __call__(self, x):
        '''
            Single Fuzzification of this term.
            [x] argument of membership function
        '''
        return self.f(x)

    def cut(self, cut):
        return self.f.clip(cut)

class DNFElement:
    '''
        This is list of terms that will be joined by OR.
    '''
    def __init__(self, *terms):
        self.terms = terms
    
    def __call__(self, user_data):
        '''
            Iterate all terms, return mf result if the (type) name equal,
            then join all mf result by OR
            ===================================================
            [user_data] dict of [type name: String] -> [value: Number]
        '''
        results = []
        for k, v in user_data.items():
            for term in self.terms:
                if k == term.name:
                    results.append(term(v))
        # Join results by OR
        result = fuzzop.stor(results)
        return result

    
class DNF:
    ''' ANTECENDENT part. 
        [dnf_els] list of DNFElement that will be joined by AND.
    '''
    def __init__(self, *dnf_els):
        self.dnf_els = dnf_els
    
    def get_names(self):
        ''' Get (type) names in this DNF. '''
        names = set()
        # Iterate all dnf elements.
        for dnf_el in self.dnf_els:
            # Iterate all term in DNFElement
            for term in dnf_el.terms:
                names.add(term.name)
        return names

    def __call__(self, user_data):
        '''
            Call each dnf_el that has some part of user types with given user_data, 
            and return combined AND.
        '''
        results = [ dnf_el(user_data) for dnf_el in self.dnf_els ]
        result = fuzzop.stand(results)
        return result
        

class Rule:
    ''' Single Atomic Rule.
        [dnf] Antecendent of the rule (DNF)
        [cons] consequence of the rule (Term).
        [weight] weight of this rule, default is 1.

    '''
    def __init__(self, dnf, cons, weight=1):
        self.dnf = dnf
        self.cons = cons
        self.weight = weight

    def match(self, user_data):
        ''' Check if the given (type) names is equal to all (type) names of this Rule.
        '''
        return self.dnf.get_names() == set(user_data.keys())
    
    def __call__(self, user_data):
        # Firing rate
        fr = self.dnf(user_data)
        return fr, self.cons.cut(fr)

    def __repr__(self):
        sant = ' AND '.join([ 
            '(' + ' | '.join([ '{}_{}'.format(term.name, term.ling) for term in d_el.terms ]) + ')'
            for d_el in self.dnf.dnf_els
        ])
        return sant + ' -> ' + '{}:{}'.format(self.cons.name, self.cons.ling)

if __name__ == '__main__':
    A = 'A'
    B = 'B'
    C = 'C'

    C1 = 'C1'
    C2 = 'C2'

    LOW = 'LOW'
    MID = 'MID'
    HIGH = 'HIGH'

    D_LOW = 0
    D_HIGH = 100

    def gaussmf(c, theta):
        return fuzzmf.GaussMF(c, theta, D_LOW, D_HIGH)

    A_LOW = Term(A, LOW, gaussmf(25, 20))
    A_MID = Term(A, MID, gaussmf(50, 20))
    A_HIGH = Term(A, HIGH, gaussmf(75, 20))

    B_LOW = Term(B, LOW, gaussmf(25, 20))
    B_MID = Term(B, MID, gaussmf(50, 20))
    B_HIGH = Term(B, HIGH, gaussmf(75, 20))

    C_LOW = Term(C, LOW, gaussmf(25, 20))
    C_MID = Term(C, MID, gaussmf(50, 20))
    C_HIGH = Term(C, HIGH, gaussmf(75, 20))

    C1_LOW = Term(C1, LOW, gaussmf(23, 20))
    C1_MID = Term(C1, MID, gaussmf(48, 15))
    C1_HIGH = Term(C1, HIGH, gaussmf(74, 20))

    # C2_LOW = Term(C2, LOW, fuzzmf.gaussmf(25, 20))
    # C2_MID = Term(C2, MID, fuzzmf.gaussmf(50, 20))
    # C2_HIGH = Term(C2, HIGH, fuzzmf.gaussmf(75, 20))

    rules = [
        Rule(
            DNF(
                DNFElement( A_LOW ), 
                DNFElement( B_LOW )
            ),
            C1_LOW),
        Rule(
            DNF(
                DNFElement( A_HIGH ), 
                DNFElement( B_HIGH )
            ),
            C1_HIGH)
    ]

    user_data = {
        A: 88,
        B: 77
    }

    clipped_mf = []

    for r in rules:
        if r.match(user_data):
            clipped_mf.append( r(user_data) )

    # Combine clipped mfs.
    combined_mf = fuzzmf.JoinMF(*clipped_mf)

    print('results : ', combined_mf.cog())
    

