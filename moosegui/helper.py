"""helper.py: 

"""
    
__author__           = "Dilawar Singh"
__copyright__        = "Copyright 2017-, Dilawar Singh"
__version__          = "1.0.0"
__maintainer__       = "Dilawar Singh"
__email__            = "dilawars@ncbs.res.in"
__status__           = "Development"

import sys
import os

from moosegui.config import _logger
import networkx as nx
import moose

def compute_layout( graph, prog = 'neato' ):
    # Layout is a dictionary of moose element with position.
    layout =  nx.nx_agraph.graphviz_layout( graph, prog )
    pos = layout.values( )
    xs, ys = zip( *pos )
    xmin, xmax = min(xs), max(xs)
    ymin, ymax = min(ys), max(ys)

    mx, my = 1.0 / (xmax-xmin), 1.0/(ymax-ymin)
    cx, cy = - xmin * mx, -ymin * my

    for k in layout:
        x, y = layout[k]
        layout[k] = ( x * mx + cx, y * my + cy )

    return layout


def toNXGraph( ):
    g = nx.DiGraph( )
    reacs = moose.wildcardFind( '/##[TYPE=Reac]' )
    for r in reacs:
        g.add_node( r.path, type = 'reac' )
        for s in r.neighbors[ 'sub' ]:
            g.add_edge( r.path, s.path )
        for p in r.neighbors[ 'prd' ]:
            g.add_edge( r.path, p.path )
    return g

