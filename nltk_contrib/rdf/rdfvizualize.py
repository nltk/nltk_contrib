#!/opt/local/bin/python
# Natural Language Toolkit: Generating RDF Triples from NL Relations
#
# Author: Ewan Klein <ewan@inf.ed.ac.uk>
# URL: <http://www.nltk.org/>
# For license information, see LICENSE.TXT

"""
Visualize RDF Graphs
"""
from rdflib import ConjunctiveGraph, Literal, BNode
import pydot
from Cheetah.Template import Template


class Visualizer(object):
    def __init__(self, graph, **vizoptions):
        self.graph = graph
        self.options = vizoptions
    
    def graph_options(self, uri, count):
        # set the defaults
        self.options['shape'] = 'oval'
        self.options['color'] = 'blue'
        self.options['label'] = '"%s"' % self.graph.namespace_manager.normalizeUri(uri)    
        self.options['fontname'] = 'Arial'
        self.options['fontsize'] = '10'
        self.options['fontcolor'] = 'black'
        
        if isinstance(uri, Literal):
            self.options['shape'] = 'box'
            self.options['color'] = 'green'
                        
        if isinstance(uri, BNode):
            self.options['label'] = '"_:bn%03d"' % count
            
        
    def graph2dot(self, filter_edges=False):
        """ 
        Convert an RDF graph into a pydot (U{http://code.google.com/p/pydot/}) C{Dot} object.
        This can be serialized as a string in dot (Graphviz graph drawing) format, or converted
        into an image file.
        
        Usage examples:
        
            >>> g = graph2dot(store, filter_edges=True)
            >>> print g.to_string()
            >>> g.write('myrdf.dot')
            >>> g.write_jpeg('myrdf.jpg', prog='dot')
        
        See U{http://www.research.att.com/sw/tools/graphviz/} for information on the dot language.
        
        @param filter_edges: if True, don't generate any edges which match the URIs in the list FILTER.
        @rtype: C{pydot.Dot}
        """

        dot = pydot.Dot(rankdir='LR', bgcolor='white', arrowsize='0.7')
        dot.set_suppress_disconnected(True)
        
        FILTER = ["rdfs:%s" % p for p in ['label', 'comment', 'description', 'isDefinedBy']] 
     
        # dictionary to associate URIs with node identifiers
        nodes = {}
        count = 1
        
        # add subjects and objects as nodes in the Dot instance
        for s, o in self.graph.subject_objects():
            for uri in s, o:
                if uri not in nodes.keys():
                    # generate a new node identifier
                    node_id = "n%03d" % count
                    nodes[uri] = node_id
                    
                    if isinstance(uri, Literal):
                        shape = 'box'
                        color = 'green'                
                    else:
                        shape = 'oval'
                        color = 'blue'
                        
                    # make nicer labels for blank nodes
                    if isinstance(uri, BNode):
                        label = "_:bn%03d" % count
                    else:
                        label = '"%s"' % self.graph.namespace_manager.normalizeUri(uri)
                    
                    
                    #n = pydot.Node(node_id, shape=shape, fontcolor='white', fontname ='Helvetica', color=color, label=label)
                    self.graph_options(uri, count)
                    n = pydot.Node(node_id, **self.options)
                    dot.add_node(n)
                    count += 1           
                    
        # add edges between subject and object nodes
        for s, p, o in self.graph.triples((None,None,None)):
            p = '"%s"' % self.graph.namespace_manager.normalizeUri(p)
            if filter_edges and p in FILTER: continue
            e = pydot.Edge(nodes[s], nodes[o], label=p, color='blue', fontcolor='black', fontname='Helvetica', fontsize='10')
            dot.add_edge(e)
        return dot


#def print_rdf_demo():
    #(postsdict, tagsdict, bundlesdict) = fetch_dlcs(USER, PASSWORD, BUNDLETAG)
    #posts = postsdict['posts']
    #rdf = Template(file='dlcs-tmpl01.txt')
    #rdf.posts = posts
    #print str(rdf)

#def write_rdf_demo():
    #(postsdict, tagsdict, bundlesdict) = fetch_dlcs(USER, PASSWORD, BUNDLETAG)
    #posts = postsdict['posts']
    #rdf = Template(file='dlcs-tmpl01.txt')
    #rdf.posts = posts
    #f = open(FILE, mode='w')
    #f.write(str(rdf))
    #print "Wrote some rdf to '%s'" % FILE
    #f.close()

def serialize_demo():
    try:
        store = ConjunctiveGraph()    
        store.parse(FILE, format='xml')
        print store.serialize(format='xml')
    except OSError:
        print "Cannot read file '%s'" % FILE

def make_dot_demo(infile):    
    try:
        store = ConjunctiveGraph()    
        store.parse(infile, format='xml')
        basename = infile.split('.')[0]
        v = Visualizer(store)
        g = v.graph2dot(filter_edges=True)
        g.write('%s.dot' % basename) 
        print "Wrote '%s.dot'" % basename
        g.write_png('%s.png' % basename, prog='dot') 
        print "Wrote '%s.png'" % basename
        g.write_svg('%s.svg' % basename, prog='dot') 
        print "Wrote '%s.svg'" % basename
    except OSError:
        print "Cannot read file '%s'" % FILE
        
        
def main():
    import sys
    from optparse import OptionParser 
    description = \
    """
Turn an RDF file into a viewable graph using Graphviz.
    """
    opts = OptionParser(description=description)    
    (options, args) = opts.parse_args()
    if len(args) != 1:
        parser.error("incorrect number of arguments")
    infile = args[0]
    #print
    #print "Fill up a template and print out the resulting rdf in n3 format"
    #print '*' * 30
    #print_rdf_demo()
    
    #print
    #print "Write some rdf to a file"
    #print '*' * 30
    #write_rdf_demo()
    
    #print
    #print "Serialize some rdf in XML format"
    #print '*' * 30
    #serialize_demo()
    
    print
    print "Visualise an rdf graph with Graphviz"
    print '*' * 30
    make_dot_demo(infile)
    
if __name__ == '__main__':    
    main()
    

    

    

