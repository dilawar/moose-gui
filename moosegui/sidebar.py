# -*- coding: utf-8 -*-

"""
Sidebar for plugins. The sidebar comprises of actions.
Currently mode, connect and settings are defined.
"""

__author__      =   "Aviral Goel"
__email__       =   "goel.aviral@gmail.com"
__credits__     =   ["NCBS Bangalore"]
__license__     =   "GPL3"
__version__     =   "1.0.0"
__maintainer__  =   "Dilawar Singh <dilawars@ncbs.res.in>"
__status__      =   "Development"


import sys
import os
from PyQt5.QtWidgets import QDialog
from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtWidgets import QAction, QToolBar
from PyQt5.QtGui import QPixmap, QIcon

from moosegui import SettingsDialog
from moosegui import config

import logging
logger_ = logging.getLogger("sidebar")

ICON_DIRECTORY              = "../icons"
HAND_ICON_FILENAME          = "hand.png"
CONNECTOR_ICON_FILENAME     = "straight_connector_with_filled_circles.png"
WRENCH_ICON_FILENAME        = "wrench.png"
DELETE_GRAPH_ICON_FILENAME  = "add_graph.png"
ADD_GRAPH_ICON_FILENAME     = "delete_graph.png"
LIST_ICON_FILENAME          = "list.png"


def create_action( parent
                 , callback
                 , text
                 , checkable
                 , checked
                 , icon_path
                 ):
    pixmap = QPixmap(icon_path)
    icon = QIcon(pixmap)
    action  = QAction(icon, text, parent)
    action.triggered.connect(callback)
    action.setCheckable(checkable)
    action.setChecked(checked)
    return action

def do_nothing(event, msg):
    logger_.debug( "do_nothing: %s" % msg )

def mode_action( parent
        , callback   = lambda ev: do_nothing(ev, "Action clicked")
        , text       = "Mode"
        , checkable  = True
        , checked    = True
        , icon_path  = os.path.join( ICON_DIRECTORY
            , HAND_ICON_FILENAME
            )
        ):
    return create_action( parent
            , callback
            , text
            , checkable
            , checked
            , icon_path
            )

def add_graph_action( parent
                   , callback   = lambda event: do_nothing(event, "Add Graph Clicked!")
                   , text       = "Add Graph"
                   , checkable  = False
                   , checked    = False
                   , icon_path  = os.path.join( ICON_DIRECTORY
                                              , ADD_GRAPH_ICON_FILENAME
                                              )
                   ):
    return create_action( parent
                        , callback
                        , text
                        , checkable
                        , checked
                        , icon_path
                        )

def delete_graph_action( parent
                      , callback   = lambda event: do_nothing(event, "Delete Graph Clicked!")
                      , text       = "Delete Graph"
                      , checkable  = False
                      , checked    = False
                      , icon_path  = os.path.join( ICON_DIRECTORY
                                                 , DELETE_GRAPH_ICON_FILENAME
                                                 )
                      ):
    return create_action( parent
                        , callback
                        , text
                        , checkable
                        , checked
                        , icon_path
                        )

def list_action( parent
               , callback   = lambda event: do_nothing(event, "List Clicked!")
               , text       = "Show List"
               , checkable  = False
               , checked    = False
               , icon_path  = os.path.join( ICON_DIRECTORY
                                          , LIST_ICON_FILENAME
                                          )
               ):
    return create_action( parent
                        , callback
                        , text
                        , checkable
                        , checked
                        , icon_path
                        )

def connector_action( parent
        , callback   = lambda event: do_nothing(event, "Connector Clicked!")
        , text       = "Mode"
        , checkable  = True
        , checked    = False
        , icon_path  = os.path.join( ICON_DIRECTORY , CONNECTOR_ICON_FILENAME)
        ):
    return create_action( parent
            , callback
            , text
            , checkable
            , checked
            , icon_path
            )

def settings_action( parent
        , callback   = (lambda event: do_nothing(event, "Settings Clicked"))
        , text       = "Mode"
        , checkable  = False
        , checked    = False
        , icon_path  = os.path.join(ICON_DIRECTORY, WRENCH_ICON_FILENAME)
        ):
    return create_action( parent
            , callback
            , text
            , checkable
            , checked
            , icon_path
            )

def sidebar():
    return QToolBar()


def main():
    from PyQt5.QtWidgets import QApplication, QMainWindow
    app = QApplication(sys.argv)
    window = QMainWindow()
    widget = SettingsDialog.SettingsWidget({
        'LeakyIaF':['Vm'],
        'Compartment':['Vm','Im'],
        'HHChannel':['Ik','Gk'],
        'ZombiePool':['n','conc'],
        'ZombieBufPool':['n','conc'],
        'HHChannel2D':['Ik','Gk'],
        'CaConc':['Ca']
        })
    d = QDialog()
    l = QHBoxLayout()
    d.setLayout(l)
    l.addWidget(widget)
    bar = sidebar()
    bar.addAction(mode_action(bar))
    bar.addAction(connector_action(bar))
    bar.addAction(settings_action(bar, d.show))
    window.addToolBar(bar)
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
