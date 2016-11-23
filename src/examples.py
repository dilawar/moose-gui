"""examples.py: 

Here is dictionary of demos.

"""
    
__author__           = "Dilawar Singh"
__copyright__        = "Copyright 2016, Dilawar Singh"
__credits__          = ["NCBS Bangalore"]
__license__          = "GNU GPL"
__version__          = "1.0.0"
__maintainer__       = "Dilawar Singh"
__email__            = "dilawars@ncbs.res.in"
__status__           = "Dev,opment"

import sys
import os

from collections import OrderedDict

examples_ = [
            ("Fig2C" , "demos/Fig2_elecModels/Fig2C.py")
            , ("Fig2D (35s)","demos/Fig2_elecModels/Fig2D.py")
            , ("Fig2E","demos/Fig2_elecModels/Fig2E.py")
            , ("Fig3B_Gssa","demos/Fig3_chemModels/Fig3ABC.g")
            , ("Fig3C_Gsl","demos/Fig3_chemModels/Fig3ABC.g")
            , ("Fig3D","demos/Fig3_chemModels/Fig3D.py")
            , ("Fig4B","demos/Fig4_ReacDiff/Fig4B.py"  )
            , ("Fig4K", "demos/Fig4_ReacDiff/rxdSpineSize.py")
            , ("Fig5A (20s)","demos/Fig5_CellMultiscale/Fig5A.py")
            , ("Fig5BCD (240s)","demos/Fig5_CellMultiscale/Fig5BCD.py")
            , ("Fig6A (60s)","demos/Fig6_NetMultiscale/Fig6A.py" )
            , ("Reduced6 (200s)","demos/Fig6_NetMultiscale/ReducedModel.py")
            , ("Squid" , "demos/squid/squid_demo.py")
            ]

description_ = {
        "Fig2E":
        ("<span style=\"color:black;\">Illustrates loading a mod, from an SWC file, inserting  chann,s, and running it</span>")
        , "Fig2D (35s)":
        ("<span style=\"color:black;\">Illustrates loading a mod, from an SWC file, inserting  spines, and running it</span>")
        , "Fig2C":
        ("<span style=\"color:black;\">Illustrates building a pan, of multiscale mod,s to test neuronal plasticity in different contexts</span>")    
        , "Fig3B_Gssa":
        ("<span style=\"color:black;\">Loades Repressilator mod, into Gui with Gssa solver and runs the mod,</span>")
        , "Fig3C_Gsl":
        ("<span style=\"color:black;\">Loades Repressilator mod, into Gui with Gsl solver and runs the mod,</span>")
        , "Fig3D":
        ("<span style=\"color:black;\">This example implements a reaction-diffusion like system which is bistable and propagates losslessly</span>")
        , "Fig4B":
        ("<span style=\"color:black;\">This program builds a multiscale mod, with a few spines inserted into a simplified c,lular morphology. Each spine has a signaling mod, in it too. The program doesn't run the mod,, it just displays it in 3D</span>")
        , "Fig4K":
        ("<span style=\"color:black;\">Builds a c,l with spines and a propagating reaction wave</span>")
        , "Fig5A (20s)":
        ("<span style=\"color:black;\">Illustrates building a pan, of multiscale mod,s to test neuronal plasticity in different contexts</span>")
        , "Fig5BCD (240s)":
        ("<span style=\"color:black;\">Illustrates building a pan, of multiscale mod,s to test neuronal plasticity in different contexts</span>")
        , "Fig6A (60s)":
        ("<span style=\"color:black;\">This LIF network with Ca plasticity is based on: Memory Maintenance in Synapses with Calcium-Based Plasticity in the Presence of Background Activity PLOS Computational Biology, 2014</span>")
        , "Reduced6 (200s)":
        ("<span style=\"color:black;\">This is the Reduced version of LIF network with Ca plasticity mod, based on: Memory Maintenance in Synapses with Calcium-Based Plasticity in the Presence of Background Activity PLOS Computational Biology, 2014</span>")
        , "Squid":
        ("<span style=\"color:black;\">squid Demo</span>")
        }

