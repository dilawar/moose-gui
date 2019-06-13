# -*- coding: utf-8 -*-

# Filename: config.py
# Description:
# Author: Subhasis Ray
# Maintainer:
# Created: Sat Feb 13 16:07:56 2010 (+0530)
# Version:

import os
import sys
from PyQt5 import QtCore

# Logger
import logging
logging.basicConfig(level=logging.DEBUG)

KEY_UNDO_LENGTH = 'main/undolength'
KEY_WINDOW_GEOMETRY = 'main/geometry'
KEY_WINDOW_LAYOUT = 'main/layout'
KEY_RUNTIME_AUTOHIDE = 'main/rtautohide'
KEY_DEMOS_DIR = 'main/demosdir'
KEY_DOCS_DIR = 'main/docsdir'
KEY_HOME_DIR = 'main/homedir'
KEY_ICON_DIR = 'main/icondir'
KEY_COLORMAP_DIR = 'main/colormapdir'
KEY_BIOMODEL_DIR = 'main/biomodelsdir'
KEY_LOCAL_DEMOS_DIR = 'main/localdemosdir'
KEY_MOOSE_LOCAL_DIR = 'main/localdir'
KEY_NUMPTHREADS = 'main/numpthreads'
KEY_LOCAL_BUILD = 'main/localbuild'
KEY_LAST_PLUGIN = 'main/lastplugin'

# These are the keys for mode specific configuration.
# Ideally the default values should be provided by the plugin.
# We use the QSettings to remember the last values
KEY_KINETICS_SIMDT = 'kinetics/simdt'
KEY_KINETICS_PLOTDT = 'kinetics/plotdt'
KEY_ELECTRICAL_SIMDT = 'electrical/simdt'
KEY_ELECTRICAL_PLOTDT = 'electrical/plotdt'
KEY_SIMTIME = 'main/simtime'

QT_VERSION = ('%s' % QtCore.QT_VERSION_STR).split('.')
QT_MAJOR_VERSION = int(QT_VERSION[0])
QT_MINOR_VERSION = int(QT_VERSION[1])

MOOSE_DOC_URL = 'http://moose.ncbs.res.in/builtins_classes/moose_builtins.html'
MOOSE_REPORT_BUG_URL = 'http://github.com/BhallaLab/moose/issues'
MOOSE_GUI_BUG_URL  = 'https://github.com/BhallaLab/moose-gui/issues'
MOOSE_CORE_BUG_URL = 'https://github.com/BhallaLab/moose-core/issues'
MOOSE_DOCS_DIR =  '/usr/share/doc/moose'

MOOSE_GUI_DIR = os.path.dirname(os.path.abspath(__file__))
assert os.path.exists(MOOSE_GUI_DIR)
MOOSE_PLUGIN_DIR = os.path.join(MOOSE_GUI_DIR, 'plugins')
assert os.path.exists(MOOSE_PLUGIN_DIR)
MOOSE_ICON_DIR = os.path.join(MOOSE_GUI_DIR, 'icons' )
assert os.path.exists(MOOSE_ICON_DIR)
NEUROKIT_PLUGIN_DIR = os.path.join(MOOSE_GUI_DIR, 'plugins/NeuroKit')
MOOSE_NUMPTHREADS = '1'

MOOSE_UNDO_LENGTH = 128 # Arbitrary undo length

# It is important that MOOSE_PLUGIN_DIR is added to system path. This is ued to
# search multiple plugins.
sys.path.append( MOOSE_PLUGIN_DIR )


def qvalue( qsetting, key ):
    """ Return value as unicode from QSetting object.
    Calling toString is not compatible with python3.
    """
    return qsetting.value( key )


class MooseSetting(dict):
    """
    dict-like access to QSettings.

    This subclass of dict wraps a QSettings object and lets one set
    and get values as Python strings rather than QVariant.

    This is supposed to be a singleton in the whole application (all
    QSettings are with same parameters).
    """
    _instance = None
    def __new__(cls, *args, **kwargs):
        # This is designed to check if the class has been
        # instantiated, if so, returns the single instance, otherwise
        # creates it.
        if cls._instance is None:
            cls._instance = super(MooseSetting, cls).__new__(cls, *args, **kwargs)
            QtCore.QCoreApplication.setOrganizationName('NCBS Bangalore')
            QtCore.QCoreApplication.setOrganizationDomain('ncbs.res.in')
            QtCore.QCoreApplication.setApplicationName('MOOSE')
            cls._instance.qsettings = QtCore.QSettings()
            # If this is the first time, then set some defaults
            cls._instance.qsettings.setValue(KEY_COLORMAP_DIR, os.path.join(MOOSE_GUI_DIR, 'colormaps'))
            cls._instance.qsettings.setValue(KEY_BIOMODEL_DIR, os.path.join(MOOSE_GUI_DIR, 'bioModels'))
            cls._instance.qsettings.setValue(KEY_ICON_DIR, os.path.join(MOOSE_GUI_DIR, 'icons'))
            cls._instance.qsettings.setValue(KEY_NUMPTHREADS, '1')
            cls._instance.qsettings.setValue(KEY_UNDO_LENGTH, ('%s' % MOOSE_UNDO_LENGTH))
            # These are to be checked at every run
            cls._instance.qsettings.setValue(KEY_HOME_DIR, os.environ['HOME'])
            cls._instance.qsettings.setValue(KEY_DOCS_DIR, MOOSE_DOCS_DIR)
        return cls._instance

    def __init__(self, *args, **kwargs):
        super(MooseSetting, self).__init__(self, *args, **kwargs)

    def __iter__(self):
        return ('%s' % key for key in self.qsettings.allKeys())

    def __setitem__(self, key, value):
        if isinstance(key, type("")):
            self.qsettings.setValue(key, value)
        else:
            raise TypeError('Expect only strings as keys')

    def __getitem__(self, key):
        val = qvalue( self.qsettings, key )
        return val

    def keys(self):
        return ['%s' % key for key in self.qsettings.allKeys()]

    def values(self):
        return [ qvalue(self.qsettings, key) for key in self.qsettings.allKeys()]

    def itervalues(self):
        return ( qvalue(self.qsettings, key) for key in self.qsettings.allKeys())

settings = MooseSetting()
