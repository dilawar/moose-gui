"""sbml.py: 

"""
    
__author__           = "Dilawar Singh"
__copyright__        = "Copyright 2017-, Dilawar Singh"
__version__          = "1.0.0"
__maintainer__       = "Dilawar Singh"
__email__            = "dilawars@ncbs.res.in"
__status__           = "Development"

import sys
import os
import libsbml
import moose
from moosegui.config import _logger

def moose_value( value, unit ):
    if not unit:
        return float( value )
    else:
        _logger.warn( "No support of %s" % unit )
        return value


class SBML( ):
    """SBML class
    """

    def __init__(self, filepath = '' ):
        self.sbml = None
        self.filepath = filepath
        self.model = None
        self.compartments = { }
        self.species = { }
        self.reactions = { }
        self.currentCompt = ''
        if filepath:
            self.load( filepath  )

    def load( self, filepath = '' ):
        if not filepath:
            self.filepath = filepath
        try:
            self.sbml = libsbml.readSBML( self.filepath )
        except Exception as e:
            _logger.warn( 'Failed to load %s' % self.filepath )
            _logger.warn( '\tError was %s' % e )
        _logger.debug( "SBML is loaded" )

    def addSpeciesById( self, i ):
        elem = self.model.getSpecies( i )
        baseCompt = self.compartments[ elem.getCompartment( ) ]
        
        mooseName = elem.id 
        moosePath = '%s/%s' % ( baseCompt.path, mooseName)
        if elem.constant:
            ms = moose.BufPool( moosePath )
        else:
            ms = moose.Pool( moosePath )

        # Set conc of n. Prefer 'n' over conc.
        n0 = float( elem.getInitialAmount( ))
        conc0 = float( elem.getInitialConcentration())
        ms.nInit = moose_value( n0, elem.getUnits( ) )
        if ms.nInit <= 0.0:
            ms.concInit = moose_value( conc0, elem.getUnits( ) )

        self.species[ elem.id ] = ms
        _logger.debug( "Added Species elem %s (Buffered?=%s) conc=%g" % ( 
            mooseName, elem.constant, ms.concInit)
            )

    def getStoichiometry( self, s ):
        if s.getStoichiometry( ):
            return int( s.getStoichiometry( ) )
        else:
            return 1

    def addReactionById( self, i ):
        elem = self.model.getReaction( i )
        compt = elem.getCompartment( ) or self.currentCompt
        assert self.currentCompt, \
            "I could not determine compartment for reaction %s" % elem.id 

        mooseCompt = self.compartments[ compt ] 
        reacid = elem.id 
        reacpath = '%s/%s' % (mooseCompt.path, reacid )
        r = moose.Reac( reacpath )

        subs = elem.getListOfReactants( )
        prds = elem.getListOfProducts( )
        subs1, prds1 = [ ], [ ]
        for i, s in enumerate( subs ):
            sname = s.getSpecies( )
            mooseSub = self.species[ sname ]
            for i in range( self.getStoichiometry( s ) ):
                moose.connect( r, 'sub', mooseSub, 'reac' )
                subs1.append( mooseSub.name )

        for i, p in enumerate( prds ):
            pname = p.getSpecies( )
            moosePrd = self.species[ pname ]
            for i in range( self.getStoichiometry( p ) ):
                moose.connect( r, 'prd', moosePrd, 'reac' )
                prds1.append( moosePrd.name )

        _logger.debug( 'Added reaction: %s <--> %s' % (
            ' + '.join(subs1), ' + '.join(prds1) )
            )


    def addCompartmentById( self, i, moose_parent ):
        c = self.model.getCompartment( i )
        comptPath = '%s/%s' % (moose_parent.path, c.name )
        _logger.info( 'Loading compartment %s' % comptPath )

        # get the geometry.
        ctype =  c.getCompartmentType( ) or 'cube'
        if ctype == [ 'cylinder' ]:
            mooseCompt = moose.CubeMesh( comptPath )
        else:
            mooseCompt = moose.CubeMesh( comptPath )

        mooseCompt.volume = float(c.getVolume( )) or 1.0
        _logger.debug( 'Volume of compartment %g' % c.volume )

        self.compartments[ c.name ] = mooseCompt
        self.currentCompt = c.name


    def loadIntoMOOSE( self ):
        import moose
        root = moose.Neutral( '/model' )
        self.model = self.sbml.getModel( )
        [ self.addCompartmentById( i, root ) for i in
                range(self.model.getNumCompartments() ) ]
        [ self.addSpeciesById( i ) for i in 
                range( self.model.getNumSpecies( ) ) ]
        [ self.addReactionById( i ) for i in 
                range( self.model.getNumReactions( ) ) ]

def test( ):
    fpath = sys.argv[1]
    sbml = SBML( fpath )
    print( sbml )
    sbml.loadIntoMOOSE( )

def main( ):
    test( )

if __name__ == '__main__':
    main()
