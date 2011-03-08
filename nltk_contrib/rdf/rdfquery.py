# Natural Language Toolkit: Convert English sentences in SPARQL Queries
#
# Copyright (C) 2001-2011 NLTK Project
# Author: Ewan Klein <ewan@inf.ed.ac.uk>,
# URL: <http://nltk.sourceforge.net>
# For license information, see LICENSE.TXT
#

import nltk
from nltk import parse, LogicParser, sem
from string import join


class SPARQLTranslator(object):
    """
    SPARQLTranslator to convert logical expressions into a SPARQL query
    """
    def __init__(self, ns=None):
        self.clauses = []
        self._query = []
        self.query = ''

        
    def flatten_conjunct(self, expr):
        """
        Turn a nested AndExpression into a list of atomic clauses.
        """
        if isinstance(expr, sem.ApplicationExpression):
            self.clauses.append(expr)
        elif isinstance(expr, sem.AndExpression):
            self.flatten_conjunct(expr.first)
            self.flatten_conjunct(expr.second)
 
    def rdf_atom(self, clause):
        """
        Turn an atomic clause into an RDF triple.
        """
        if isinstance(clause, sem.ApplicationExpression):
            function, arguments = clause.uncurry()
            if len(arguments) == 1:
                return "?%s rdf:type %s.\n" % (str(arguments[0].variable.name), str(function.variable))
            elif len(arguments) == 2:
                return "?%s %s ?%s.\n" % (str(arguments[0].variable.name), str(function.variable), str(arguments[1].variable.name))
            else:
                raise ValueError("cannot parse clause %s" % clause)
        
    def translate(self, semrep):
        """
        Given a semantic representation as parsed by sem.LogicParser(),
        return a SPARQL query.
        """
        function = ''
        # This needs to be more clever about deciding whether a given semrep
        # can in fact be converted into a valid SPARQL query
        selectword = False
        
        # Assume the main input is a function application
        if isinstance(semrep, sem.ApplicationExpression):
            function, arguments = semrep.uncurry()
 
        if str(function.variable) in ['list', 'name']:
            self._query.append('SELECT DISTINCT')
            body = arguments[1]
        
        # Everything is a lot easier if we can get hold of a lambda expression
        # which represents the body of the query
        if isinstance(body, sem.LambdaExpression):
            var = body.variable.name
            self._query.append('?'+var)
            self._query.append('WHERE\n{\n')
            if isinstance(body.term.term, sem.AndExpression):
                
                self.flatten_conjunct(body.term.term)
                triples = [self.rdf_atom(c) for c in self.clauses]
                self._query.extend(triples)
                
            
        self.query = join(self._query) + '}'
        

def demo():
    cp = parse.load_parser('file:rdf.fcfg', trace=0)
    tokens = 'list the actors in the_shining'.split()
    trees = cp.nbest_parse(tokens)
    tree = trees[0]
    semrep = sem.root_semrep(tree)
    trans = SPARQLTranslator()
    trans.translate(semrep)
    print trans.query
    
    
if __name__ == '__main__':
    demo()

