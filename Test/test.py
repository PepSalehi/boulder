# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Test
                                 A QGIS plugin
 Computes level of traffic stress for bikes
                              -------------------
        begin                : 2014-04-24
        copyright            : (C) 2014 by Peyman Noursalehi/ Northeastern University
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
# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import QtCore, QtGui
from qgis.core import *
# Initialize Qt resources from file resources.py
import resources_rc
# Import the code for the dialog
from testdialog import TestDialog
from ui_test import Ui_Test
import os.path
from os.path import expanduser
from math import floor,ceil

class Test:

    def __init__(self, iface):
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value("locale/userLocale")[0:2]
        localePath = os.path.join(self.plugin_dir, 'i18n', 'test_{}.qm'.format(locale))
        self.fileName = None
        if os.path.exists(localePath):
            self.translator = QTranslator()
            self.translator.load(localePath)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg = TestDialog()
        self.update_ui

    def initGui(self):
        # Create action that will start plugin configuration
        self.action = QAction(
            QIcon(":/plugins/test/icon.png"),
            u"test", self.iface.mainWindow())
        # connect the action to the run method
        self.action.triggered.connect(self.run)

        # Add toolbar button and menu item
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu(u"&test", self.action)


        QtCore.QObject.connect(self.dlg.ui.browse_in, QtCore.SIGNAL("clicked()"), self.browse)
        # QtCore.QObject.connect(self.dlg.ui.browse_out, QtCore.SIGNAL("clicked()"), self.browse_dest)
        # QtCore.QObject.connect(self.dlg.ui.checkBox, QtCore.SIGNAL("clicked()"), self.activate_browse_out)
        # QtCore.QObject.connect(self.dlg.ui.buttonBox, QtCore.SIGNAL("clicked()"), self.browse)
        QtCore.QObject.connect(self.dlg.ui.process_Button,QtCore.SIGNAL("clicked()"), self.process)

    def browse(self):
        self.fileName = QtGui.QFileDialog.getOpenFileName(self.dlg,'Select shapefile',expanduser("~"),"shapefile (*.shp)")
        self.dlg.ui.lineEdit_in.setText(self.fileName)
        # self.ui.label_3.setText(fileName)

    def update_ui(self):
        # self.dlg.ui.lineEdit_in.clear()
        self.dlg.ui.progressBar.setValue(0)
   

    def unload(self):
        # Remove the plugin menu item and icon
        self.iface.removePluginMenu(u"&test", self.action)
        self.iface.removeToolBarIcon(self.action)
        self.dlg.ui.lineEdit_in.clear()
        self.dlg.ui.progressBar.setValue(0)

    def process(self):

        if self.fileName is None:
            QMessageBox.information(self.dlg, ("Error"), ("Please first select a shapefile"))
            return

        layer = QgsVectorLayer(self.fileName, "layer_name", "ogr")
 

        nFeat = layer.featureCount()
        layer.startEditing()

        index = layer.fieldNameIndex("_lts")
        if index == -1: # field doesn't exist
            caps = layer.dataProvider().capabilities()
            if caps & QgsVectorDataProvider.AddAttributes:
              res = layer.dataProvider().addAttributes( [ QgsField("_lts", \
                QVariant.Int) ] )
            layer.updateFields()
        index = layer.fieldNameIndex("_num_lane")
        if index == -1: # field doesn't exist
            caps = layer.dataProvider().capabilities()
            if caps & QgsVectorDataProvider.AddAttributes:
              res = layer.dataProvider().addAttributes( [ QgsField("_num_lane", \
                QVariant.Int) ] )
            layer.updateFields()

        index = layer.fieldNameIndex("_protected")
        if index == -1: # field doesn't exist
            caps = layer.dataProvider().capabilities()
            if caps & QgsVectorDataProvider.AddAttributes:
              res = layer.dataProvider().addAttributes( [ QgsField("_protected", \
                QVariant.Int) ] )
            layer.updateFields()
        index = layer.fieldNameIndex("_bike_lane")
        if index == -1: # field doesn't exist
            caps = layer.dataProvider().capabilities()
            if caps & QgsVectorDataProvider.AddAttributes:
              res = layer.dataProvider().addAttributes( [ QgsField("_bike_lane", \
                QVariant.Int) ] )
            layer.updateFields()
        index = layer.fieldNameIndex("CROSSINGME")
        if index == -1: # field doesn't exist
            caps = layer.dataProvider().capabilities()
            if caps & QgsVectorDataProvider.AddAttributes:
              res = layer.dataProvider().addAttributes( [ QgsField("CROSSINGME", \
                QVariant.Int) ] )
            layer.updateFields()
        index = layer.fieldNameIndex("_lts11")
        if index == -1: # field doesn't exist
            caps = layer.dataProvider().capabilities()
            if caps & QgsVectorDataProvider.AddAttributes:
              res = layer.dataProvider().addAttributes( [ QgsField("_lts11", \
                QVariant.Int) ] )
            layer.updateFields()
        index = layer.fieldNameIndex("_lts12")
        if index == -1: # field doesn't exist
            caps = layer.dataProvider().capabilities()
            if caps & QgsVectorDataProvider.AddAttributes:
              res = layer.dataProvider().addAttributes( [ QgsField("_lts12", \
                QVariant.Int) ] )
            layer.updateFields()
        index = layer.fieldNameIndex("_lts13")
        if index == -1: # field doesn't exist
            caps = layer.dataProvider().capabilities()
            if caps & QgsVectorDataProvider.AddAttributes:
              res = layer.dataProvider().addAttributes( [ QgsField("_lts13", \
                QVariant.Int) ] )
            layer.updateFields()
        index = layer.fieldNameIndex("_lts_woX")
        if index == -1: # field doesn't exist
            caps = layer.dataProvider().capabilities()
            if caps & QgsVectorDataProvider.AddAttributes:
              res = layer.dataProvider().addAttributes( [ QgsField("_lts_woX", \
                QVariant.Int) ] )
            layer.updateFields()
        index = layer.fieldNameIndex("LTS")
        if index == -1: # field doesn't exist
            caps = layer.dataProvider().capabilities()
            if caps & QgsVectorDataProvider.AddAttributes:
              res = layer.dataProvider().addAttributes( [ QgsField("LTS", \
                QVariant.Int) ] )
            layer.updateFields()



        i=1
        featid_lts ={}
        for feature in layer.getFeatures():
            street = street_link_object()
            street.path_width = feature['PATHWIDTH']
            street.park_width = feature['PARKWIDTH']
            street.num_lane = feature['NUMLANE']
            street.f_code = feature['ROADCLASS']
            street.foc_width = feature['FOC_WIDTH']
            # street.median = feature['MEDIAN']
            street.speed_limit = feature['SPD_LIM']
            # street.pocket_lane = feature['RTLANE']
            street.illegial_parking = feature['ILLPARKING']
            street.center_line = feature['CL']
            street.net_type = feature['NET_TYPE']
            street.right_turn_speed=feature['RTSPEED']
            street.pocket_lane_shift = feature['RTLANSHIFT']
            street.right_turn_lane_length = feature['RTPOCKLENG']
            street.one_way = feature['ONEWAY']
            street.raw_cross_stress = feature['_rawCrossS']
            street.cross_treat = feature['CrossTreat']

            street.calculate_crossing_me(street.num_lane) # has to always be before computing lts
            street.compute_LTS()
            if street.LTS != None :
                i+=1
                j=ceil(i/(nFeat/100))
                self.dlg.ui.progressBar.setValue(j)
            feature["_lts_woX"] = street.LTS
            feature["_lts11"] = street.lts11
            feature["_lts12"] = street.lts12
            feature["_lts13"] = street.lts13
            feature["_num_lane"] = street.num_lane
            feature["_bike_lane"] = street.bike_lane
            feature["_protected"] = street.protected
            feature["CROSSINGME"] = street.crossing_me
            layer.updateFeature(feature)
        # layer.updateFields()
        # QMessageBox.information(self.dlg, ("WAIT"), ("Please wait!"))
        layer.commitChanges()
            # layer.commitChanges()
        QMessageBox.information(self.dlg, ("Successful"), ("LTS has been computed!"))  

        self.dlg.close()

    # run method that performs all the real work
    def run(self):
        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # self.dlg.exec_()
        # if self.fileName is None:
        #     QMessageBox.information(self.dlg, ("Error"), ("Please first select a shapefile"))
        #     return
        # See if OK was pressed
        if result == 1:
            # do something useful (delete the line containing pass and
            # substitute with your code)
            pass

        



#############################################################################################################
class street_link_object(object):
    ''' object representing a link, with the goal of calculating its LTS'''
    def __init__(self):
        self.id = None
        self.center_line = None
        self.path_width=None
        self.f_code = None
        self.park_width = None 
        self.num_lane = None
        self.speed_limit = None
        self.illegial_parking = None
        self.foc_width = None
        self.protected = None
        self.override = None
        self.LTS = 1
        self.lts11 = 1
        self.lts12 = 1
        self.lts13 = 1
        self.cross_LTS=None
        self.bike_lane = None 
        self.cl_guess = None
        self.one_way = None
        self.net_type=None
        self.right_turn_lane_length = None
        self.pocket_lane_shift = None
        self.right_turn_speed = None
        self.multi_right_turn_lane = None
        self.crossing_me = 1
        self.raw_cross_stress = None
        self.cross_treat = None 



    def update_LTS(self, new_lts):
        ''' updates LTS if input is higher''' 
        if new_lts > self.LTS:
            self.LTS = new_lts


    def compute_num_lane(self):
        if self.one_way:  #it's not NULL
            self.num_lane = floor(self.num_lane/2)

    def compute_bke_lane(self):
        if self.net_type in ['PAVED SHOULDER','ON-STREET BIKE LANE','SINGLE BIKE LANE']:
            self.bike_lane =1
    def compute_protected(self):
        if self.net_type in ['MULTI-USE PATH','SIDEWALK CONNECTION','SS MULTI-USE PATH','CONNECTOR']:
            self.protected =1
        else:
            self.protected =0

    def calculate_crossing_me(self,number_of_lanes):
        num_lane = number_of_lanes
        if self.one_way in ["TF","FT"]:
            # street has a median
            if num_lane <= 3:
                if self.speed_limit <35:
                    pass
                elif self.speed_limit <=35:
                    #
                    self.crossing_me =2
                else:
                    
                    self.crossing_me = 3
            elif num_lane in [4,5]:
                if self.speed_limit <= 25:
                    pass
                elif self.speed_limit <=30:
                    
                    self.crossing_me = 2
                elif self.speed_limit <=35:
                    
                    self.crossing_me = 3
                else:
                   
                    self.crossing_me = 4
            else:
                if self.speed_limit<=25:
                   
                    self.crossing_me = 2
                elif self.speed_limit <=30:
                    
                    self.crossing_me = 3
                else:
                    
                    self.crossing_me = 4
        else:
            # no median refuge
            if num_lane <= 3:
                if self.speed_limit <35:
                    pass
                elif self.speed_limit <=35:
                    
                    self.crossing_me = 2
                else:
                   
                    self.crossing_me = 3
            elif num_lane in [4,5]:
                if self.speed_limit <= 25:
                    self.crossing_me = 2
                elif self.speed_limit <=30:
                    self.crossing_me = 2
                elif self.speed_limit <=35:
                    self.crossing_me = 3
                else:
                   
                    self.crossing_me = 4
            else:
                
                self.crossing_me = 4

    def compute_LTS(self):
        ''' Computes level of stress for each link'''

        ##############
        #saving original num lane for crossing calclations
        # orig_num_lane= self.num_lane
        ##############
        skip = False
        if not self.one_way:  #it's 2 way
            self.num_lane = floor(self.num_lane/2)
        #####
        # for now, cl_guess is always none
        if not self.center_line :  # if it's NULL
            self.center_line = self.cl_guess
        
        if self.net_type in ['MULTI-USE PATH','SIDEWALK CONNECTION','SS MULTI-USE PATH','CONNECTOR']:
            self.protected =1
        else:
            self.protected =0
        if self.net_type in ['PAVED SHOULDER','ON-STREET BIKE LANE','SINGLE BIKE LANE']:
            self.bike_lane =1
        else:
            self.bike_lane =0

        if self.cross_LTS != NULL:
            update_LTS(int(self.cross_LTS))

        if self.override != None:
            self.LTS = self.override
            skip = True

        if self.protected:
            self.LTS = 1
            self.crossing_me = 0
            skip = True
        ############################
        if not skip: 
            if self.bike_lane >0: # and NewBikeLnae  in [1,2]
                # it has a bike lane
                if self.park_width >0:
                    # has parking
                    assert self.path_width >= 4
                    reach = self.path_width + self.park_width
                    if self.num_lane >= 2:
                        #overrides the wide lane criteria
                        # self.LTS = max(3,self.LTS)
                        self.update_LTS(3)


                    # if self.f_code in [ local or private]: # 
                    if reach > 14.5:
                        pass # leave LTS unchanged
                    elif reach >= 14 :
                            # self.LTS = max(2, self.LTS)
                        self.update_LTS(2)
                    elif self.speed_limit <=25 or self.f_code in [ "LOCAL STR" ,"PRIVATE ST"]:
                            # self.LTS = max(3, self.LTS)
                        self.update_LTS(2)

                    else: 
                        self.update_LTS(3)

                else: 
                    # it has no parking
                    if self.num_lane <= 1:
                        pass
                    elif self.num_lane ==2 and self.one_way : # each side is two lanes
                        self.update_LTS(2)
                    else:
                        self.update_LTS(3)

                    # if self.f_code in ["RES, LOCAL STR"]: #remove
                    if self.path_width >= 6:
                        pass
                    else:
                        self.update_LTS(2)
                        
                    if self.speed_limit >= 40:
                        self.update_LTS(4)
                    elif self.speed_limit >= 35 :
                        self.update_LTS(3)
                    
                    if self.illegial_parking:
                        self.update_LTS(3)
                ###########################
            else: 
                # There is no bike lane
                if self.speed_limit <= 25:  # ALMOST EVERYTHING ENDS UP HERE
                    
                    if self.num_lane >= 3 :
                        self.update_LTS(4)
                    elif self.num_lane >=2 :
                        self.update_LTS(3)
                    elif self.f_code in [ "LOCAL STR" ,"PRIVATE ST"] and not self.center_line :
                        pass
                    else:
                        self.update_LTS(2)

                elif self.speed_limit <= 30 :
                    if self.num_lane >=2 :
                        self.update_LTS(4)
                    elif self.f_code in [ "LOCAL STR" ,"PRIVATE ST"] and not self.center_line :
                        self.update_LTS(2)
                    else:
                        self.update_LTS(3)
                
                else: 
                    self.update_LTS(4)
            ################################
                if self.right_turn_lane_length in [0 , None]:
                    pass
                elif self.multi_right_turn_lane:
                    self.update_LTS(4)
                elif self.right_turn_lane_length <= 150 and not self.pocket_lane_shift:
                    if self.right_turn_speed <= 15 :
                        self.update_LTS(2)
                    elif self.right_turn_speed <= 20:
                        self.update_LTS(3)
                    else:
                        self.update_LTS(4)
                elif self.right_turn_speed <= 15 :
                    self.update_LTS(3)
                else:
                    self.update_LTS(4)
            # return True

            ####################### Added on Apr 24. #######################################
        _temp = self.LTS
        _temp2 = max(self.LTS,self.raw_cross_stress)
        if self.cross_treat not in [11,12,13]:
            self.lts11 = _temp2
            self.lts12 = _temp2
            self.lts13 = _temp2
        elif self.cross_treat == 11:
            self.lts11 = _temp;
            self.lts12 = _temp
            self.lts13 = _temp
        elif self.cross_treat == 12:
            self.lts11 = _temp2;
            self.lts12 = _temp
            self.lts13 = _temp
        elif self.cross_treat == 13:
            self.lts11 = _temp2;
            self.lts12 = _temp2
            self.lts13 = _temp
    #############################################################################################################