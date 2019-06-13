"""camkii_pp1_scheme.py

See http://www.ncbi.nlm.nih.gov/pmc/articles/PMC1069645/

"""

__author__           = "Dilawar Singh"
__copyright__        = "Copyright 2015, Dilawar Singh and NCBS Bangalore"
__credits__          = ["NCBS Bangalore"]
__license__          = "GNU GPL"
__version__          = "1.0.0"
__maintainer__       = "Dilawar Singh"
__email__            = "dilawars@ncbs.res.in"
__status__           = "Development"

import params as _p
import datetime
import moose
import moose.utils as mu
import numpy as np
import re
import sys
import time
import math
from collections import defaultdict

import logging
logging.basicConfig(level=logging.DEBUG,
    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
    datefmt='%m-%d %H:%M',
    filename='__log__.txt',
    filemode='a'
    )
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
console.setFormatter(formatter)
_logger = logging.getLogger('')
_logger.addHandler(console)

class Args: pass
args = Args()

print( '[INFO] Using moose from %s' % moose.__file__ )
print( '[INFO] Using moose from %s' % moose.__version__ )

# global data-structures
model_path_ = '/model'
molecules_ = {}
tables_ = defaultdict( list )
curr_subsec_ = None
compt_ = None

N = 6.023e23

gainers_ , loosers_ = [], []
dephospho_ = []

def pool_name( root, name ):
    global molecules_
    molName = '%s.%s' % (root.name, name )
    return molName


def conc_to_n( conc ):
    val = conc * float( args['volume'] ) * N
    assert val > 0.0
    return val


def num_subunits( name ):
    m = re.search( r'x(?P<xs>\d)y(?P<ys>\d)', name )
    try:
        xs, ys = int(m.group('xs')), int(m.group( 'ys' ))
    except Exception as e:
        mu.warn( 'Failed to get subunit numbers in %s' % name )
        raise e
    return xs + ys 


def inv_conc_to_N( conc ):
    return conc / (float(args['volume']) * N )

def n_to_conc( n ):
    global args
    return n / (N * args['volume'] )


def add_pool( root, name ):
    global molecules_
    pname = pool_name( root, name )
    ppath = '%s/%s' % (root.path, name)
    if moose.exists( ppath ):
        _logger.warn( 'Already exists %s' % ppath )
        return moose.element( ppath )
    else:
        p = moose.Pool( ppath )
        p.name = pname
        molecules_[pname] = p
        return p


def init_pools( compt ):
    global args
    # Ring with 6 subunits.
    for st in range(7):
        state = 'x%dy%d' % (st, 6 - st )
        p = add_pool( compt, state )
        p.nInit = 0

    if args['enable_subunit_exchange']:
        # Ring with 7 subunits
        for st in range(8):
            state = 'x%dy%d' % (st, 7 - st )
            p = add_pool( compt, state )
            p.nInit = 0
            molecules_[p.name] = p

    if args['enable_subunit_exchange']:
        # Add subunit x and y.
        # NOTE: These guys are shared across multiple sub_sections..
        x = add_pool( compt, 'x' )
        x.nInit = 0
        molecules_[x.name] = x

        y = add_pool( compt, 'y' )
        y.nInit = 0
        molecules_[y.name] = y
    else:
        _logger.info( "Subunit exchange is disabled" )
        

    for p in [ 'I1', 'PP1', 'PP1_', 'I1P', 'I1P_', 'I1PPP1' ]:
        if p in [ 'I1' ]:
            c = moose.BufPool( '%s/%s' % (compt.path, p) )
            c.name = pool_name( compt, p )
            molecules_[c.name] = c
        else:
            c = moose.Pool( '%s/%s' % (compt.path, p) )
            c.name = pool_name( compt, p )
            molecules_[c.name] = c

        molecules_[c.name].nInit = 0

    if args['enable_subunit_exchange']:
        # Here we are using concInit rather than nInit to setup the number of
        # molecules. This is because when Dsolve is used, setting nInit causes
        # problem: they don't get divided into different voxels.
        molecules_[ pool_name(compt, 'x0y7') ].concInit = args[ 'camkii_conc' ] / 2.0
        molecules_[ pool_name(compt, 'x0y6') ].concInit = args[ 'camkii_conc' ] / 2.0
    else:
        molecules_[ pool_name(compt, 'x0y6') ].concInit = args['camkii_conc'] 

    if args['enable_subunit_exchange']:
        _logger.debug('CaMKII = %f (6sym) %f (7sym)' % (
            molecules_[ pool_name(compt,'x0y6')].nInit,
            molecules_[pool_name(compt,'x0y7')].nInit )
            )
    else:
        _logger.debug('CaMKII = %d (6sym)' % ( 
            molecules_[pool_name(compt,'x0y6')].nInit ) 
            )

    molecules_[ pool_name(compt, 'PP1') ].concInit = args['pp1_conc']
    _logger.debug('Total PP1 %s' % molecules_[pool_name(compt,'PP1')].nInit )

    # TODO: Much of it only make sense if stochastic solver is used.
    molecules_[ pool_name(compt,'I1') ].concInit =  _p.conc_i1_free
    pp1CamKIICplx = moose.Pool( '%s/camkii_pp1_cplx' % compt.path )
    pp1CamKIICplx.name = pool_name( compt, pp1CamKIICplx.name )
    pp1CamKIICplx.concInit = 0
    molecules_[ pp1CamKIICplx.name ] = pp1CamKIICplx

    for k in sorted(molecules_):
        _logger.debug( 'Molecule: %s (%f)' % (k, molecules_[k].nInit ) )


def add_table( moose_elem, field, tableName = None):
    global tables_
    tablePath = '%s/tab%s' % (moose_elem.path, field)
    if moose.exists( tablePath ):
        return None
    t = moose.Table2( tablePath )
    moose.connect( t, 'requestOut', moose_elem, 'get'+field[0].upper()+field[1:])
    tables_[ moose_elem.name ].append( t )
    _logger.debug( 'Added table on %s' % moose_elem.path )


def add_reaction( reacPath ):
    if moose.exists( reacPath ):
        mu.warn( 'Reaction %s already exists' % reacPath )
        return moose.element( reacPath )
    else:
        r =  moose.Reac( reacPath )
        return r


def looseX( pool, xs ):
    # Only pool with 7 subunits can loose subunit.
    assert num_subunits( pool.name ) == 7, 'Only CaMKII(7) can gain subunit'
    global curr_subsec_
    loosers_.append( ('x', pool.name) )
    r = add_reaction( '%s/%s.loose_x' % (pool.path, pool.name))
    r.numKf = _p.rate_loosex
    r.numKb = 0.0
    moose.connect( r, 'sub', pool, 'reac' )
    toPoolName = 'x%dy%d' % (xs-1, 7 - xs )
    toPool = molecules_[ curr_subsec_ + '.' + toPoolName ]
    moose.connect( r, 'prd', toPool, 'reac' )
    moose.connect( r, 'prd', molecules_[curr_subsec_ + '.x'], 'reac' )
    assert num_subunits(pool.name) == num_subunits(toPool.name) + 1
    _logger.debug( 'Reaction: %s -> %s + x' % ( pool.name, toPool.name) )


def looseY( pool, ys ):
    # Only pool with 7 subunits can loose subunit.
    assert num_subunits( pool.name ) == 7, 'Only CaMKII(7) can gain subunit'
    global curr_subsec_
    loosers_.append( ('y', pool.name) )
    r = add_reaction( '%s/%s.loose_y' % (pool.path, pool.name) )
    r.numKf = _p.rate_loosey
    r.numKb = 0.0
    moose.connect( r, 'sub', pool, 'reac' )
    toPoolName = 'x%dy%d' % (7-ys, ys - 1 )
    toPool = molecules_[ curr_subsec_ + '.' + toPoolName ]
    moose.connect( r, 'prd', toPool, 'reac' )
    moose.connect( r, 'prd', molecules_[curr_subsec_ + '.y'], 'reac' )
    _logger.debug( 'Reaction: %s -> %s + y' % ( pool.name, toPool.name ) )
    assert  num_subunits( pool.name) == num_subunits( toPool.name) + 1


def gainX( pool, xs ):
    # Only pool with 6 subunits can gain subunit.
    global curr_subsec_
    gainers_.append( ('x', pool.name) )
    r = add_reaction( '%s/%s.gainx' % (pool.path, pool.name))
    r.numKf = _p.rate_gainx
    r.numKb = 0.0
    moose.connect( r, 'sub', pool, 'reac' )
    moose.connect( r, 'sub', molecules_['%s.x' % curr_subsec_ ], 'reac' )
    toPoolName = 'x%dy%d' % (xs+1, 6 - xs )
    toPool = molecules_[ curr_subsec_ + '.' + toPoolName ]
    moose.connect( r, 'prd', toPool, 'reac' )
    _logger.debug( 'Reaction: %s + x -> %s' % ( pool.name, toPool.name ) )
    assert num_subunits( pool.name ) == 6, 'Only CaMKII(6) can gain subunit'
    assert num_subunits( pool.name) == num_subunits( toPool.name)  - 1


def gainY( pool, ys ):
    # Only pool with 6 subunits can gain subunit.
    global curr_subsec_
    gainers_.append( ('y', pool.name) )
    r = add_reaction( '%s/%s.gainy' % (pool.path, pool.name) )
    r.numKf = _p.rate_gainy
    r.numKb = 0.0
    moose.connect( r, 'sub', pool, 'reac' )
    moose.connect( r, 'sub', molecules_['%s.y' % curr_subsec_], 'reac' )
    toPoolName = 'x%dy%d' % ( 6-ys, ys+1 )
    toPool = molecules_[ curr_subsec_ + '.' + toPoolName ]
    moose.connect( r, 'prd', toPool, 'reac' )
    _logger.debug( 'Reaction: %s, y -> %s' % ( pool.name, toPool.name ) )
    assert num_subunits( pool.name ) == 6, 'Only CaMKII(6) can gain subunit'
    assert num_subunits( pool.name) == num_subunits( toPool.name) - 1


def ca_input( root ):
    """Input calcium pulse

    When using stochastic solver, any event less than 100 or so seconds would
    not work.
    """
    global args
    # Input calcium
    ca = moose.Pool( '%s/ca' % root.path )
    ca.concInit = _p.ca_basal
    ca.name = pool_name( root, ca.name )
    molecules_[ ca.name ] = ca

    _logger.info("Setting up input calcium : init = %s" % ca.concInit )

    # _logger.debug("Baselevel ca conc = %s" % _p.resting_ca_conc)
    concFunc = moose.Function( "%s/cafunc" % ca.path )
    concFunc.expr = args[ 'ca_expr' ]
    moose.connect( concFunc, 'valueOut', ca, 'setConc' )
    _logger.info( "Ca conc expression = %s " % concFunc.expr )


def i1_to_i1p( root ):
    global molecules_
    global curr_subsec_
    i1p_const = moose.BufPool( '%s/i1p_const' % molecules_[curr_subsec_ + '.' + 'I1'].path)
    i1p_const.name = pool_name( root, i1p_const.name )
    molecules_[i1p_const.name] = i1p_const

    f = moose.Function( '%s/i12i1p' % molecules_[pool_name(root, 'I1P')].path )
    f.x.num = 2
    f.expr = 'x1*(1+(x0/{kh2})^3)/(x0/{kh2})^3'.format(kh2=conc_to_n(_p.K_H2))
    frmName = pool_name( root, 'I1' )
    toName = pool_name( root, 'I1P_' )
    moose.connect( molecules_[pool_name(root,'ca')], 'nOut', f.x[0], 'input' )
    moose.connect( molecules_[frmName], 'nOut', f.x[1], 'input' )
    moose.connect( f, 'valueOut',  molecules_[toName], 'setN' )
    _logger.debug('Reaction: %s -> %s, Expr = %s' % (frmName, toName, f.expr ))

    # A slow reaction between I1P and I1P_ which synchornize both pools.
    r = add_reaction( '%s/sync' % molecules_[pool_name(root,'I1P')].path );
    frmPool = molecules_[ pool_name( root, 'I1P_' ) ]
    toPool = molecules_[ pool_name( root, 'I1P' ) ]
    moose.connect( r, 'sub', frmPool, 'reac' )
    moose.connect( r, 'prd', toPool, 'reac' )
    r.Kf = r.Kb = 1.0
    _logger.debug( 'Reaction: %s -> %s' % ( frmPool.name, toPool.name ) )


def pp1_activation( root ):
    """Here we setup the reactions PP1

    I1P binds with PP1 and give rise to complex I1PPP1 (which is inavtivated PP1)
    I1P + PP1 <- -> I1PPP1
    """
    activePP1 = molecules_[pool_name(root, 'PP1')]
    i1pPool = molecules_[ pool_name( root, 'I1P' ) ]
    inactive_pp1 = molecules_[ pool_name( root, 'I1PPP1' ) ]
    r = add_reaction( '%s/reac_inactivate_pp1' % activePP1.path )

    moose.connect( r, 'sub', activePP1, 'reac' )
    moose.connect( r, 'prd', inactive_pp1, 'reac')
    k3, k4, s = 1e5, 0.0001, 1
    kfFun = moose.Function( '%s/kffunc' % r.path )
    kfFun.expr = '{scale}*{k3}*x0'.format( k3 = k3, scale = s )
    moose.connect( i1pPool, 'nOut', kfFun.x[0], 'input' )
    moose.connect( kfFun, 'valueOut', r, 'setNumKf' )
    r.numKb = s * k4

    _logger.debug( 'Reaction: %s + %s -> %s' % ( activePP1.name, i1pPool.name,
        inactive_pp1.name ) )


def dephosphorylate( root, frmPool, toPool ):
    global molecules_
    global curr_subsec_
    dephospho_.append( frmPool.name )

    _logger.info( 'Not using Michealson Menten scheme for dephosphorylate' )
    inter = moose.Pool( '%s/pp1_%s_cplx' % (frmPool.path, frmPool.name) )
    inter.name = curr_subsec_ + '.' + inter.name
    inter.nInit = 0
    r = add_reaction( '%s/%s.add_pp1' % (frmPool.path, frmPool.name) )
    moose.connect( r, 'sub', frmPool, 'reac' )
    moose.connect( r, 'sub', molecules_[curr_subsec_+ '.' + 'PP1'], 'reac' )
    moose.connect( r, 'prd', inter, 'reac' )
    r.Kf = _p.k_2 / _p.K_M
    r.Kb = 0.0

    rr = add_reaction( '%s/%s_dephospho' % (frmPool.path,frmPool.name) )
    moose.connect( rr, 'sub', inter, 'reac' )
    moose.connect( rr, 'prd', molecules_[curr_subsec_ + '.' + 'PP1'], 'reac' )
    moose.connect( rr, 'prd', toPool, 'reac' )
    rr.Kf = 1.0
    rr.Kb = 0.0
    _logger.debug( "Reac (dephospho): %s -> %s" % (frmPool.name, toPool.name ))


def phosphorylation_first_step( root, nc ):
    # CaMKII to x1y0 is slow.
    subPool = molecules_[ pool_name( root, 'x0y%d' % nc ) ]
    prdPool = molecules_[ pool_name( root, 'x1y%d' % (nc-1) ) ]
    r0 = add_reaction( '%s/reac_0to1_%d' % (subPool.path, nc) )
    r0.numKb = 0
    moose.connect( r0, 'sub', subPool, 'reac' )
    moose.connect( r0, 'prd', prdPool, 'reac' )
    # The rate expression of this reaction depends on Ca++
    f = moose.Function( '%s/func_kf' % r0.path  )
    f.expr = '{nc}*{k1}*(x0/{kh1})^6/(1 + (x0/{kh1})^3)^2'.format(
            k1 = _p.k_1, kh1= conc_to_n(_p.K_H1), nc = nc
            )
    f.x.num = 1
    moose.connect( molecules_[pool_name(root,'ca')], 'nOut', f.x[0], 'input' )
    moose.connect( f, 'valueOut', r0, 'setNumKf' )
    _logger.debug( 'Reaction: %s -> %s' % (subPool.name, prdPool.name ) )


def phosphorylation_first_step_subunit( compt ):
    """
    NOTE: Phosphorylation of detached subunit is much faster than the subunits in
    holoenzyme. Why?

    Phosphorylation of detached subunit is not possible. To phosphorylate, the
    subunit must have a neighbour i.e. two subunit must come together first.

    """
    return 

    # Previously I was phosphrylating the subunits.
    global molecules_ 
    global curr_subsec_
    subPool = molecules_[ pool_name( compt, 'y') ]
    prdPool = molecules_[ pool_name( compt, 'x') ]
    r0 = add_reaction( '%s/reac_y2x' % compt.path )
    r0.numKb = 0
    moose.connect( r0, 'sub', subPool, 'reac' )
    moose.connect( r0, 'prd', prdPool, 'reac' )
    # The rate expression of this reaction depends on Ca++
    f = moose.Function( '%s/func_kf' % r0.path  )
    f.expr = '{k1}*(x0/{kh1})^3/(1 + (x0/{kh1})^3)'.format(
            k1 = _p.k_1 , kh1= conc_to_n(_p.K_H1)
            )
    f.x.num = 1
    moose.connect( molecules_[ pool_name(compt, 'ca') ], 'nOut', f.x[0], 'input' )
    moose.connect( f, 'valueOut', r0, 'setNumKf' )
    _logger.info( 'Phosphorylation of subunit y in voxel %s' % compt.name )
    _logger.debug( 'Reaction: %s -> %s' % (subPool.name, prdPool.name ) )


def camkii_activation_deactivation( root ):
    """All reaction involved in activating CaMKII"""

    phosphorylation_first_step( root, 6 )

    if args['enable_subunit_exchange']:
        phosphorylation_first_step( root, 7 )

    # Phosphorylation of CaMKII occurs in various stages:
    # x0y0 -> x1y0 -> x2y0 -> x3y0 -> x4y0 -> x5y0 -> CaMKII*
    for pp in range(1, 6):
        frm, to = 'x%dy%d' % (pp, 6-pp), 'x%dy%d' % (pp + 1, 6-pp-1)
        frmName, toName = [pool_name(root, x) for x in [frm, to]]
        r = add_reaction( '%s/phospho_%s_%s' % (root.path, frmName, toName))
        # And its rate is controlled by another function
        f = moose.Function( '%s/funcKf' % r.path  )
        f.expr = '{k1}*(x0/{kh1})^3/(1 + (x0/{kh1})^3)'.format(
                k1 = _p.k_1, kh1= conc_to_n(_p.K_H1)
                )
        f.x.num = 1
        moose.connect(  molecules_[pool_name(root,'ca')], 'nOut', f.x[0], 'input' )
        moose.connect( f, 'valueOut', r, 'setNumKf' )
        r.numKb = 0
        moose.connect( r, 'sub', molecules_[frmName], 'reac')
        moose.connect( r, 'prd', molecules_[toName], 'reac')
        _logger.debug("Reaction: %s -> %s, numKf=%s" % (frmName, toName, f.expr ))

    # The symmetry of 7 kicks in only when args['enable_subunit_exchange'] is enabled.
    if args['enable_subunit_exchange']:
        for pp in range(1, 7):
            frm, to = 'x%dy%d' % (pp, 7-pp), 'x%dy%d' % (pp + 1, 7-pp-1)
            frmName, toName = [ pool_name(root, x) for x in [frm, to] ]
            r = add_reaction( '%s/phospho_%s_%s' % (root.path, frm, to))
            # And its rate is controlled by another function
            f = moose.Function( '%s/funcKf' % r.path  )
            f.expr = '{k1}*(x0/{kh1})^3/(1 + (x0/{kh1})^3)'.format(
                    k1 = _p.k_1, kh1= conc_to_n(_p.K_H1)
                    )
            f.x.num = 1
            moose.connect(  molecules_[pool_name(root,'ca')], 'nOut', f.x[0], 'input' )
            moose.connect( f, 'valueOut', r, 'setNumKf' )
            r.numKb = 0
            moose.connect( r, 'sub', molecules_[frmName], 'reac')
            moose.connect( r, 'prd', molecules_[toName], 'reac')
            _logger.debug("Reaction: %s -> %s (numKf = %s)" % (frmName, toName, f.expr ))

        gainX( molecules_[ pool_name(root, 'x0y6') ], 0 )
        gainY( molecules_[ pool_name(root, 'x6y0') ], 0 )

    for nP in range(1, 7):
        if args['enable_subunit_exchange']:
            gainX( molecules_[ pool_name(root, 'x%dy%d' % (nP, 6-nP) )], nP )
            gainY( molecules_[ pool_name(root, 'x%dy%d' % (6-nP, nP) )], nP )

        frmPool = molecules_[ pool_name(root, 'x%dy%d' % (nP, 6-nP)) ]
        toPool = molecules_[ pool_name( root, 'x%dy%d' % (nP-1, 6-nP+1)) ]
        dephosphorylate( root, frmPool, toPool )

    if args['enable_subunit_exchange']:
        for nP in range(1, 8):
            looseX( molecules_[ pool_name(root,'x%dy%d' % (nP, 7-nP)) ], nP )
            looseY( molecules_[ pool_name(root,'x%dy%d' % (7-nP, nP)) ], nP )

            frmPool = molecules_[ pool_name(root, 'x%dy%d' % (nP, 7-nP)) ]
            toPool =  molecules_[ pool_name(root, 'x%dy%d' % (nP-1, 7-nP+1)) ]
            dephosphorylate( root, frmPool, toPool )

    if False:
        # A  reaction between PP1 and PP1_ which synchornize both pools.
        r = add_reaction( '%s/sync' % molecules_[pool_name(root,'PP1_')].path );
        a = molecules_[ pool_name( root, 'PP1_' ) ]
        b = molecules_[ pool_name( root, 'PP1' ) ]
        moose.connect( r, 'sub', a, 'reac' )
        moose.connect( r, 'prd', b, 'reac' )
        r.Kf = 0.1
        r.Kb = 0
        _logger.debug( "Reac %s -> %s" % (a.name, b.name ))

def remove_extra( pool, limit ):
    null = moose.BufPool( '%s/null' % pool.path )
    null.nInit = 0.0
    nullReac = moose.Reac( '%s/null_reac' % pool.path )
    nullReac.numKb = 0.0
    moose.connect( nullReac, 'sub', pool, 'reac' )
    moose.connect( nullReac, 'prd', null, 'reac' )
    nullF = moose.Function( '%s/func_null' % pool.path )
    nullF.expr = '(x0 > %f)?1e-2:0' % limit
    _logger.debug( 'Removing extra from pool %s' % pool.path )
    _logger.debug( '\tExpression on nullR %s' % nullF.expr )
    moose.connect( pool, 'nOut', nullF.x[0], 'input' )
    moose.connect( nullF, 'valueOut', nullReac, 'setNumKf' )


def add_turnover( root ):
    # Added turnover of CaMKII
    global curr_subsec_
    global args

    r = add_reaction( '%s/%s.turnover6' % (root.path, curr_subsec_) )
    moose.connect( r, 'sub', molecules_[pool_name(root,'x6y0')], 'reac' )
    moose.connect( r, 'prd', molecules_[pool_name(root,'x0y6')], 'reac' )
    r.Kf =  args[ 'turnover_rate' ]
    _logger.info( "Turnover rate for CaMKII(6) %g" % r.Kf )
    r.Kb = 0.0

    if args['enable_subunit_exchange']:
        rr = add_reaction( '%s/%s.turnover7' % (root.path, curr_subsec_) )
        moose.connect( rr, 'sub', molecules_[pool_name(root,'x7y0')], 'reac' )
        moose.connect( rr, 'prd', molecules_[pool_name(root,'x0y7')], 'reac' )
        rr.Kf =  args[ 'turnover_rate' ]
        _logger.info( "Turnover rate for CaMKII(7) %g" % rr.Kf )
        rr.Kb = 0.0


def print_compt( compt ):
    reacs = moose.wildcardFind( '%s/##[TYPE=ZombieReac]' % compt.path )
    reacs += moose.wildcardFind( '%s/##[TYPE=Reac]' % compt.path )
    _logger.debug( 'Total %s reactions ' % len(reacs ))
    dot = [ "digraph system { " ]
    molecules = []
    rtext = ''
    for r in reacs:
        subs = []
        for ss in r.neighbors['sub']:
            for s in ss:
                subs.append( '"%s"' % s.path  )
                molecules.append( '"%s" [label="%s",shape=circle,diffConst="%g"]; ' % (
                    s.path, "", s.diffConst ) )
        rtext += '\t' + ' , '.join( subs )
        molecules.append( '"%s" [label="", shape=rect];' % r.name )
        rtext += ' -> "%s" -> ' % r.name
        tgt = [ ]
        # print( '->' )
        for tt in r.neighbors['prd']:
            for t in tt:
                # print(t.path[-20:])
                tgt.append( '"%s"' % t.path )
                molecules.append( '"%s" [label="%s",shape=circle,diffConst="%g"]; ' % (
                    t.path, t.name, t.diffConst ) )
        rtext += ' , '.join( tgt )
        rtext += '\n'
        # print( '\n')
    try:
        _logger.debug( 'Volume of compartment : %g, ' % compt.volume )
    except Exception as e:
        _logger.warn( ' Compartment does not have volume'  )

    _logger.info( 'Total reactions %d' % len( set( reacs ) ) )
    _logger.info( 'Total species %d' % len( set(molecules) ) )
    dot.append( '\t\n'.join( molecules ) )
    dot.append( rtext )
    dot.append( "}" )
    with open( '%s.dot' % sys.argv[0], 'w' ) as f:
        f.write( "\n".join( dot ) )


def setup_solvers( compt, stochastic ):
    global args
    stoich = moose.Stoich( "%s/stoich" % compt.path)
    if stochastic:
        _logger.info("Setting up Stochastic solver in %s" % compt.path )
        s = moose.Gsolve('%s/gsolve' % compt.path)
        s.useClockedUpdate = True
    else:
        s = moose.Ksolve('%s/ksolve' % compt.path)
        _logger.info( 'Using method %s' % s.method )

    stoich.compartment = moose.element(compt.path)
    stoich.ksolve = s
    stoich.path = '%s/##' % compt.path


def is_close( val, ref, rtol):
    if abs(val - ref)/float(ref) <= rtol:
        return True
    return False


def assert_close( val, ref, rtol):
    if is_close( val, ref, rtol ):
        return True
    _logger.warn('FAILED'
            , "Expected %s, got %s, relative tolerance: %s" % (ref, val, rtol)
            )
    return False


def make_model( root, **kwargs):
    global args
    _logger.info( 'Making model under %s' % root )
    init_pools( root )
    ca_input( root )
    i1_to_i1p( root )
    pp1_activation( root )
    camkii_activation_deactivation( root )
    if args['enable_subunit_exchange']:
        _logger.info( 'Subunit exchange is enabled' )
        if True:
            dephosphorylate( root, molecules_[ pool_name( root, 'x') ], molecules_[ pool_name( root, 'y' ) ] )
        else:
            _logger.warn( 'x is not dephosphorylated to y in this version' )
        # And y phosphorylate into x
        phosphorylation_first_step_subunit( root )
    else:
        _logger.info( 'No subunit exchage in voxel %s' % root.name )
    add_turnover( root )



def verify( ):
    global compt_
    # pools = moose.wildcardFind( '%s/##[TYPE=Pool]' % model_path_ )
    pools = moose.wildcardFind( '%s/##[TYPE=ZombiePool]' % model_path_ )
    assert len(pools) > 0
    allMolecules = np.sum( [ x.nInit for x in pools ] )
    _logger.debug( 'All molecules in systems %d' % allMolecules )

def setupTables( plotlist = [ ] ):
    """Create tables. 
    Once can add table when pools are created. But when Dsolve is used, table
    must be created after setting the solvers. If number of voxels are n (>1 ),
    each pool is divided into n but Tables are not replicated. 
    Is it a bug BhallaLab/moose-core#159

    If plotlist is empty, create table on all Pools/BuffPools
    """

    global tables_ 
    global model_path_ 

    allPools = moose.wildcardFind( '%s/##[TYPE=ZombiePool]' % model_path_ )
    allPools += moose.wildcardFind( '%s/##[TYPE=ZombieBufPool]' % model_path_ )
    if not plotlist:
        plotlist = allPools

    for i, p in enumerate( plotlist ):
        add_table( p, 'n' )

    # Now renamed the tables for better plotting.
    tables = [ ]
    for k in tables_:
        for i, tab in enumerate( tables_[ k ] ):
            tab.columnName = '%s[%d].N' % ( k, i ) 
            tables.append( tab )
    return tables

def setup_diffusion_of_pool( voxel1, voxel2, species, diff_const = 1e-12 ):
    """Setup diffusion between voxels """
    global molecules_
    global compt_
    pool1 = molecules_[ '%s.%s' % (voxel1.name, species ) ]
    pool2 = molecules_[ '%s.%s' % (voxel2.name, species ) ]
    r = moose.Reac( '%s/diff_%s' % (voxel1.path, species ) )
    moose.connect( r, 'sub', pool1, 'reac' )
    moose.connect( r, 'prd', pool2, 'reac' )
    _logger.info( 
            'Diffusion reaction between %s <-> %s' % (pool1.name, pool2.name)
            )
    # The rate constant is given by D / l / l. For diffusion coefficients of 1
    # uM^2/sec in a 
    d = diff_const / (( compt_.x1 - compt_.x0 ) ** 2)
    _logger.debug( 'Diffusion coefficient (%s) %f -> rate %f' % (species, diff_const, d) )
    r.numKf = d 
    r.numKb = d

def setup_diffusion( voxels, species ):
    """Setup diffusion across voxels """
    global args

    if len( voxels ) < 2:
        _logger.info( 'Not enough voxels to setup diffusion' )
        return 

    if False:
        # A <-> B <-> C where <-> is diffusion between two compartments.
        for i, v2 in enumerate( voxels[1:] ):
            v1 = voxels[i]
            setup_diffusion_of_pool( v1, v2
                    , species, args[ 'diff_dict'].get( species, 0.0 ) 
                    )
    else:
        # A <-> B <-> C <-> A where <-> is diffusion between two compartments.
        for i, v1 in enumerate( voxels ):
            v2 = voxels[ (i+1) % len(voxels) ]
            setup_diffusion_of_pool( v1, v2, species, args[ 'diff_dict'].get( species, 0.0 ) )


def main( compt_name, **kwargs ):
    global args
    global model_path_
    global curr_subsec_
    global compt_
    moose.Neutral( model_path_ )
    args = kwargs

    voxels = [ ]
    l = args[ 'voxel_length' ]
    nVoxels = args[ 'num_voxels' ]
    radius = 30e-9 
    args[ 'volume' ] = math.pi * radius * radius * l
    args[ 'camkii_conc' ] = n_to_conc( args[ 'camkii' ] / nVoxels  )
    args[ 'pp1_conc' ] = n_to_conc( args[ 'pp1' ] / nVoxels )
    args[ 'psd_volume' ] = 0.0

    if isinstance( args['diff_dict'], str ):
        args[ 'diff_dict' ] = eval( args[ 'diff_dict' ] )
        _logger.info( 'Diffusion dict %s' % args[ 'diff_dict' ] )

    compt_ = moose.CylMesh( '%s/%s' % (model_path_, compt_name ) )
    compt_.x1 = l
    compt_.r0 = compt_.r1 = radius

    _logger.info( 'Volume of compt %g' % compt_.volume )
    for i in range( args[ 'num_voxels' ] ):
        curr_subsec_ = 'sw%d' % i
        voxel = moose.Neutral( '%s/%s' % ( compt_.path, curr_subsec_ ) )
        _logger.info( "Creating voxles %d" % i )
        _logger.debug( '==== Created subsystem inside %s' % voxel.name )
        make_model( voxel, **kwargs )
        voxels.append( voxel )

    for x in args[ 'diff_dict' ].keys( ):
        _logger.info( "Setting up diffusion for %s" % x )
        try:
            setup_diffusion( voxels, x )
        except Exception as e:
            _logger.warn( 'Could not enable diffusion for %s' % x )
            _logger.warn( '\tError was %s' % e )


    setup_solvers( compt_, stochastic = True )
    print_compt( compt_ )

    # Now add solvers and other goodies in compartment.
    moose.setClock(18, args['record_dt'] ) # Table2
    tables = setupTables( )

    st = moose.Streamer( '/model/streamer' )
    st.outfile = args['outfile']
    _logger.info( 'Added streamer with outfile  %s' % st.outfile )
    st.addTables( tables )
    t1 = time.time()
    stamp = datetime.datetime.now().isoformat()
    # moose.setClock( 10, 0.003 )
    # moose.setClock( 15, 0.03 )
    # moose.setClock( 16, 0.03 )
    moose.reinit()
    print( '== Gainers' )
    print( sorted( gainers_ ) )
    print( '== Loosers' )
    print( sorted( loosers_ ) )
    print( '== Dephosphorylated' )
    print( sorted( dephospho_ ) )

    # sanity tests
    verify( )
    runtime = 24 * 3600 * float( args[ 'simtime' ] )
    _logger.info('Running for %d seconds' %  runtime )
    t = time.time( )
    moose.start( runtime, 1 )
    print( '[INFO] Time taken %f' % (time.time() - t ) )

    # append parameters to streamer file.
    with open( st.outfile, 'a' ) as f:
        f.write( "# %s" % str( args ) )
    print( '[INFO] Appended simulation parameters to file' )

    _logger.info( 'Total time taken %s' % (time.time() - t1 ) )



if __name__ == '__main__':
    import argparse
    # Argument parser.
    description = 'CaMKII/PP1 switch. Most parameters are in params.py file.'
    parser = argparse.ArgumentParser(description=description)

    parser.add_argument('--simtime', '-st'
        , required = False
        , default = _p.run_time
        , type = float
        , help = 'Run time for simulation (days)'
        )

    parser.add_argument('--outfile', '-o'
        , required = False
        , default = '%s.dat' % sys.argv[0]
        , help = 'Outfile to save the data in (csv) file.'
        )

    parser.add_argument('--camkii', '-ck'
        , required = False
        , default = _p.N_CaMK
        , type = float
        , help = 'No of CaMKII molecules in each voxel.'
        )

    parser.add_argument('--pp1', '-pp'
        , required = False
        , type = float
        , default = _p.N_PP1
        , help = 'No of PP1 molecules in each voxel.'
        )

    parser.add_argument('--turnover-rate', '-tr'
        , required = False
        , type = float
        , default = _p.turnover_rate
        , help = 'Turnover rate of CaMKKII (in per second)'
        )

    parser.add_argument('--record-dt', '-dt'
        , required = False
        , default = 60
        , type = float
        , help = 'Record dt for plot'
        )

    parser.add_argument('--enable-subunit-exchange', '-SE'
        , required = False
        , default = False
        , action = 'store_true'
        , help = 'Enable subunit exchange.'
        )

    parser.add_argument('--num-switch', '-ns'
        , required = False
        , default = _p.num_switch
        , type = int
        , help = 'No of switches in system'
        )

    parser.add_argument('--num-voxels', '-nv'
        , required = False
        , default = _p.num_voxels
        , type = int
        , help = 'No of voxels in one switch.'
        )

    parser.add_argument('--diff-dict', '-dd'
        , required = False
        , default = '%s' % _p.diff_consts
        , type = str
        , help = 'Diffusion coefficients as python dictionary'
        )

    parser.add_argument('--voxel-length', '-nl'
        , required = False
        , default = _p.voxel_length
        , type = float
        , help = 'Length of individial voxel'
        )

    parser.add_argument('--ca-expr', '-ca'
        , required = False
        , default = _p.ca_expr
        , help = 'Calcium expression (muParser/moose expression)'
        )

    parser.add_argument('--michaelis-menten', '-mm'
        , required = False
        , default = False
        , action = 'store_true'
        , help = 'Use Michealson-Menten scheme for dephosphorylated.'
        )

    parser.parse_args( namespace = args )
    main( 'camkii_pp1_0', **vars(args) )
