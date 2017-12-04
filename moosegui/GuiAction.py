"""GuiAction.py: 

"""
    
__author__           = "Dilawar Singh"
__copyright__        = "Copyright 2017-, Dilawar Singh"
__version__          = "1.0.0"
__maintainer__       = "Dilawar Singh"
__email__            = "dilawars@ncbs.res.in"
__status__           = "Development"

import sys
import os
import moose
import re
import logging

def loadPythonModel( modelfile ):
    return -1

    ## with open( modelfile ) as f:
    ##     text = f.read( )

    ## # File is read.
    ## text = re.sub( r'moose\.start\(.*?\)', '', text )
    ## print( text )
    ## try:
    ##     eval( text, globals( ) )
    ## except Exception as e:
    ##     logging.warn( "Failed to load %s" % modelfile )
    ##     return 

    ## print( "Model is loaded" )
    ## paths = moose.wildcardFile( '/##' )
    ## print( "Total %d paths created " % len( paths ) )

def load_SBML( modelfile ):
    logging.info( "Loading %s" % modelfile )
    


def loadModel( filepath ):
    """
    Load model into moose
    """

    ext = os.path.basename( filepath ).split( '.' )[-1]
    if ext in [ 'py', 'PY' ]:
        loadPythonModel( filepath )
    elif ext in [ 'sbml', 'xml' ]:
        load_SBML( filepath )
    else:
        logging.warn( "This extension %s is not supported" )

