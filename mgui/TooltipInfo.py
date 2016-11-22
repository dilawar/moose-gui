"""TooltipInfo.py:

Keeps all TooltipInfo here.

"""

__author__ = "Dilawar Singh"
__copyright__ = "Copyright 2016, Dilawar Singh"
__credits__ = ["NCBS Bangalore"]
__license__ = "GNU GPL"
__version__ = "1.0.0"
__maintainer__ = "Dilawar Singh"
__email__ = "dilawars@ncbs.res.in"
__status__ = "Development"

import sys
import os

tooltip_info_dict_ = {
    "CubeMesh": "Cubical compartment",
    "CylMesh": "Cylinderical compartment",
    "Pool": "A Pool is a collection of molecules of a given species in a given cellular compartment.\n It can undergo reactions that convert it into other pool(s). \nParameters: initConc (Initial concentration), diffConst (diffusion constant). Variable: conc (Concentration)",
    "BufPool": "A BufPool is a buffered pool. \nIt is a collection of molecules of a given species in a given cellular compartment, that are always present at the same concentration.\n This is set by the initConc parameter. \nIt can undergo reactions in the same way as a pool.",
    "Function": "A Func computes an arbitrary mathematical expression of one or more input concentrations of Pools. The output can be used to control the concentration of another Pool, or as an input to another Func",
    "StimulusTable": "A StimulusTable stores an array of values that are read out during a simulation, and typically control the concentration of one of the pools in the model. \nParameters: size of table, values of entries, start and stop times, and an optional loopTime that defines the period over which the StimulusTable should loop around to repeat its values",
    "Reac": "A Reac is a chemical reaction that converts substrates into products, and back. \nThe rates of these conversions are specified by the rate constants Kf and Kb respectively.",
    "MMenz": "An MMenz is the Michaelis-Menten version of an enzyme activity of a given Pool.\n The MMenz must be created on a pool and can only catalyze a single reaction with a specified substrate(s). \nIf a given enzyme species can have multiple substrates, then multiple MMenz activites must be created on the parent Pool. \nThe rate of an MMenz is V [S].[E].kcat/(Km + [S]). There is no enzyme-substrate complex. Parameters: Km and kcat.",
    "Enz": "An Enz is an enzyme activity of a given Pool. The Enz must be created on a pool and can only catalyze a single reaction with a specified substrate(s). \nIf a given enzyme species can have multiple substrates, then multiple Enz activities must be created on the parent Pool. \nThe reaction for an Enz is E + S <===> E.S ---> E + P. \nThis means that a new Pool, the enzyme-substrate complex E.S, is always formed when you create an Enz. \nParameters: Km and kcat, or alternatively, K1, K2 and K3. Km = (K2+K3)/K1"
}
