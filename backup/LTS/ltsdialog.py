# -*- coding: utf-8 -*-
"""
/***************************************************************************
 LTSDialog
                                 A QGIS plugin
 Computes level of traffic stress
                             -------------------
        begin                : 2014-04-24
        copyright            : (C) 2014 by Peyman Noursalehi / Northeastern University
        email                : p.noursalehi@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import QtCore, QtGui
from qgis.core import *
from ui_lts import Ui_Dialog
# create the dialog for zoom to point


class LTSDialog(QtGui.QDialog, Ui_Dialog):
    def __init__(self):
        QtGui.QDialog.__init__(self)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.ui.progress_bar.setValue(0)
        self.ui.progressBar.setValue(0)
        self.setWindowTitle(("LTS Toolbox"))
        # self.layers = self.iface.legendInterface().layers()  # store the layer list 
        
        # for layer in self.layers:    # foreach layer in legend 
        #     self.dlg.ui.layerCombo.addItem( layer.name() )  
        # self.populate_layers()
    def populate_layers(self):
        layerlist = []
        self.ui.layerCombo.clear()  # clear the combo 
        layermap = QgsMapLayerRegistry.instance().mapLayers()
        for name, layer in layermap.iteritems():
            if layer.type() == QgsMapLayer.VectorLayer:
                if layer.geometryType() == QGis.Line:
                    layerlist.append( unicode( layer.name() ) )
        for layer in layerlist:    # foreach layer in legend 
            self.ui.layerCombo.addItem( layer )  