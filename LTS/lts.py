# -*- coding: utf-8 -*-
"""
/***************************************************************************
 LTS
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
# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import QtCore, QtGui
from qgis.core import *
from qgis.utils import iface
# Initialize Qt resources from file resources.py
import resources_rc

# Import the code for the dialog
from ltsdialog import LTSDialog
from ui_lts import Ui_Dialog
import os.path
from os.path import expanduser
from math import floor,ceil
import networkx as nx 
from collections import OrderedDict
import os 
import processing
import random
import time 
import csv
import cPickle as pickle

############## read or write shapefiles
"""
*********
Shapefile
*********
####

Edited read write, added file name option

#####
Generates a networkx.DiGraph from point and line shapefiles.

"The Esri Shapefile or simply a shapefile is a popular geospatial vector
data format for geographic information systems software. It is developed
and regulated by Esri as a (mostly) open specification for data
interoperability among Esri and other software products."
See http://en.wikipedia.org/wiki/Shapefile for additional information.
"""
#    Copyright (C) 2004-2010 by
#    Ben Reilly <benwreilly@gmail.com>
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.

__author__ = """Ben Reilly (benwreilly@gmail.com)"""
__all__ = ['read_shp', 'write_shp']


def read_shp(path):
    """Generates a networkx.DiGraph from shapefiles. Point geometries are
    translated into nodes, lines into edges. Coordinate tuples are used as
    keys. Attributes are preserved, line geometries are simplified into start
    and end coordinates. Accepts a single shapefile or directory of many
    shapefiles.

    "The Esri Shapefile or simply a shapefile is a popular geospatial vector
    data format for geographic information systems software [1]_."

    Parameters
    ----------
    path : file or string
       File, directory, or filename to read.

    Returns
    -------
    G : NetworkX graph

    Examples
    --------
    >>> G=nx.read_shp('test.shp') # doctest: +SKIP

    References
    ----------
    .. [1] http://en.wikipedia.org/wiki/Shapefile
    """
    try:
        from osgeo import ogr
    except ImportError:
        raise ImportError("read_shp requires OGR: http://www.gdal.org/")

    net = nx.DiGraph()

    def getfieldinfo(lyr, feature, flds):
            f = feature
            return [f.GetField(f.GetFieldIndex(x)) for x in flds]

    def addlyr(lyr, fields):
        for findex in xrange(lyr.GetFeatureCount()):
            f = lyr.GetFeature(findex)
            flddata = getfieldinfo(lyr, f, fields)
            g = f.geometry()
            attributes = dict(zip(fields, flddata))
            attributes["ShpName"] = lyr.GetName()
            if g.GetGeometryType() == 1:  # point
                net.add_node((g.GetPoint_2D(0)), attributes)
            if g.GetGeometryType() == 2:  # linestring
                attributes["Wkb"] = g.ExportToWkb()
                attributes["Wkt"] = g.ExportToWkt()
                attributes["Json"] = g.ExportToJson()
                last = g.GetPointCount() - 1
                net.add_edge(g.GetPoint_2D(0), g.GetPoint_2D(last), attributes)

    if isinstance(path, str):
        shp = ogr.Open(path)
        lyrcount = shp.GetLayerCount()  # multiple layers indicate a directory
        for lyrindex in xrange(lyrcount):
            lyr = shp.GetLayerByIndex(lyrindex)
            flds = [x.GetName() for x in lyr.schema]
            addlyr(lyr, flds)
    return net


def write_shp(G, outdir,edges_name):
    """Writes a networkx.DiGraph to two shapefiles, edges and nodes.
    Nodes and edges are expected to have a Well Known Binary (Wkb) or
    Well Known Text (Wkt) key in order to generate geometries. Also
    acceptable are nodes with a numeric tuple key (x,y).

    "The Esri Shapefile or simply a shapefile is a popular geospatial vector
    data format for geographic information systems software [1]_."

    Parameters
    ----------
    outdir : directory path
       Output directory for the two shapefiles.

    Returns
    -------
    None

    Examples
    --------
    nx.write_shp(digraph, '/shapefiles') # doctest +SKIP

    References
    ----------
    .. [1] http://en.wikipedia.org/wiki/Shapefile
    """
    try:
        from osgeo import ogr
    except ImportError:
        raise ImportError("write_shp requires OGR: http://www.gdal.org/")
    # easier to debug in python if ogr throws exceptions
    ogr.UseExceptions()

    def netgeometry(key, data):
        if 'Wkb' in data:
            geom = ogr.CreateGeometryFromWkb(data['Wkb'])
        elif 'Wkt' in data:
            geom = ogr.CreateGeometryFromWkt(data['Wkt'])
        elif type(key[0]).__name__ == 'tuple':  # edge keys are packed tuples
            geom = ogr.Geometry(ogr.wkbLineString)
            _from, _to = key[0], key[1]
            try:
                geom.SetPoint(0, *_from)
                geom.SetPoint(1, *_to)
            except TypeError:
                # assume user used tuple of int and choked ogr
                _ffrom = [float(x) for x in _from]
                _fto = [float(x) for x in _to]
                geom.SetPoint(0, *_ffrom)
                geom.SetPoint(1, *_fto)
        else:
            geom = ogr.Geometry(ogr.wkbPoint)
            try:
                geom.SetPoint(0, *key)
            except TypeError:
                # assume user used tuple of int and choked ogr
                fkey = [float(x) for x in key]
                geom.SetPoint(0, *fkey)

        return geom

    # Create_feature with new optional attributes arg (should be dict type)
    def create_feature(geometry, lyr, attributes=None):
        feature = ogr.Feature(lyr.GetLayerDefn())
        feature.SetGeometry(g)
        if attributes != None:
            # Loop through attributes, assigning data to each field
            for field, data in attributes.iteritems():
                feature.SetField(field, data)
        lyr.CreateFeature(feature)
        feature.Destroy()

    drv = ogr.GetDriverByName("ESRI Shapefile")
    shpdir = drv.CreateDataSource(outdir)
    # delete pre-existing output first otherwise ogr chokes
    # try:
    #     shpdir.DeleteLayer(nodes_name)
    # except:
    #     pass
    # nodes = shpdir.CreateLayer(nodes_name, None, ogr.wkbPoint)
    # for n in G:
    #     data = G.node[n] or {}
    #     g = netgeometry(n, data)
    #     create_feature(g, nodes)
    try:
        shpdir.DeleteLayer(edges_name)
    except:
        pass
    edges = shpdir.CreateLayer(edges_name, None, ogr.wkbLineString)

    # New edge attribute write support merged into edge loop
    fields = {}      # storage for field names and their data types
    attributes = {}  # storage for attribute data (indexed by field names)

    # Conversion dict between python and ogr types
    OGRTypes = {int: ogr.OFTInteger, str: ogr.OFTString, float: ogr.OFTReal}

    # Edge loop
    for e in G.edges(data=True):
        data = G.get_edge_data(*e)
        g = netgeometry(e, data)
        # Loop through attribute data in edges
        for key, data in e[2].iteritems():
            # Reject spatial data not required for attribute table
            if (key != 'Json' and key != 'Wkt' and key != 'Wkb'
                and key != 'ShpName'):
                  # For all edges check/add field and data type to fields dict
                    if key not in fields:
                  # Field not in previous edges so add to dict
                        if type(data) in OGRTypes:
                            fields[key] = OGRTypes[type(data)]
                        else:
                            # Data type not supported, default to string (char 80)
                            fields[key] = ogr.OFTString
                        # Create the new field
                        newfield = ogr.FieldDefn(key, fields[key])
                        edges.CreateField(newfield)
                        # Store the data from new field to dict for CreateLayer()
                        attributes[key] = data
                    else:
                     # Field already exists, add data to dict for CreateLayer()
                        attributes[key] = data
        # Create the feature with, passing new attribute data
        create_feature(g, edges, attributes)

    nodes, edges = None, None


# fixture for nose tests
def setup_module(module):
    from nose import SkipTest
    try:
        import ogr
    except:
        raise SkipTest("OGR not available")






















###########################################################
###########################################################
class LTS:

    def __init__(self, iface):
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value("locale/userLocale")[0:2]
        localePath = os.path.join(self.plugin_dir, 'i18n', 'lts_{}.qm'.format(locale))

        if os.path.exists(localePath):
            self.translator = QTranslator()
            self.translator.load(localePath)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg = LTSDialog()
        self.update_ui()
        



    def initGui(self):
        # Create action that will start plugin configuration
        self.action = QAction(
            QIcon(":/plugins/LTS/icon.png"),
            u"LTS Toolbox", self.iface.mainWindow())
        # connect the action to the run method
        self.action.triggered.connect(self.run)

        # Add toolbar button and menu item
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu(u"&LTS Toolbox", self.action)

        # QtCore.QObject.connect(self.dlg.ui.find_cc, QtCore.SIGNAL("clicked()"), self.find_connected_components)
        
        QtCore.QObject.connect(self.dlg.ui.process_Button,QtCore.SIGNAL("clicked()"), self.process)
        # QtCore.QObject.connect(self.dlg.ui.layerCombo,QtCore.SIGNAL("currentIndexChanged(int)"), self.update_lts_field)
        QtCore.QObject.connect(self.dlg.ui.layerCombo,QtCore.SIGNAL("activated (int)"), self.update_lts_field)
        QtCore.QObject.connect(self.dlg.ui.road_combo, QtCore.SIGNAL("activated (int)"), self.update_conn_lts_field)

        QtCore.QObject.connect(self.dlg.ui.find_cc_Button,QtCore.SIGNAL("clicked()"), self.find_connected_components)
        QtCore.QObject.connect(self.dlg.ui.find_connectivity_btn,QtCore.SIGNAL("clicked()"), self.compute_connectivity)



        self.update_ui()
        self.layers = self.iface.legendInterface().layers()  # store the layer list 
        # self.dlg.ui.layerCombo.clear()  # clear the combo 
        # for layer in self.layers:    # foreach layer in legend 
        #     self.dlg.ui.layerCombo.addItem( layer.name() )    # add it to the combo 

    def unload(self):
        # Remove the plugin menu item and icon
        self.iface.removePluginMenu(u"&LTS Toolbox", self.action)
        self.iface.removeToolBarIcon(self.action)

    def update_ui(self):
        # self.dlg.ui.lineEdit_in.clear()
        self.dlg.ui.progress_bar.setValue(0)

    
    def make_column(self,layer,name):
        index = layer.fieldNameIndex(str(name))
        if index == -1: # field doesn't exist
            caps = layer.dataProvider().capabilities()
            if caps & QgsVectorDataProvider.AddAttributes:
              res = layer.dataProvider().addAttributes( [ QgsField(str(name), \
                QVariant.Int) ] )
            layer.updateFields()
            return 0  # so I know if the column already existed or did I create it for the first time
        return 1

    def remove_column(self,layer,name,did_it_existed):
        #did_it_existed is number; if 1 means it was there before, so column should not be deleted.
        index = layer.fieldNameIndex(str(name))
        if index != -1 and did_it_existed==0 :  # field exists and wasn't there before
            layer.dataProvider().deleteAttributes( [index]  )            
            layer.updateFields()

    def update_lts_field(self):
        index = self.dlg.ui.layerCombo.currentIndex() 
        if index < 0: 
            # it may occur if there's no layer in the combo/legend 
            pass
        else: 
            layer = self.dlg.ui.layerCombo.itemData(index) 
        try:
            self.dlg.ui.lts_combo.clear()
            for attr in layer.dataProvider().fieldNameMap().keys(): # dict with column names as keys
                # if layer.type() == QgsMapLayer.VectorLayer and layer.geometryType() == QGis.Line:
                self.dlg.ui.lts_combo.addItem(str(attr), attr) 
        except:
            pass

    def update_conn_lts_field(self):
        index = self.dlg.ui.road_combo.currentIndex() 
        if index < 0: 
            # it may occur if there's no layer in the combo/legend 
            pass
        else: 
            layer = self.dlg.ui.road_combo.itemData(index) 
        try:
            self.dlg.ui.LtsColumn.clear()
            for attr in layer.dataProvider().fieldNameMap().keys(): # dict with column names as keys
                # if layer.type() == QgsMapLayer.VectorLayer and layer.geometryType() == QGis.Line:
                self.dlg.ui.LtsColumn.addItem(str(attr), attr) 
        except:
            pass

    def process(self):
        """ Calculates Level of Traffic Stress for the selected layer"""


        index = self.dlg.ui.layerCombo.currentIndex() 
        if index < 0: 
            # it may occur if there's no layer in the combo/legend 
            pass
        else: 
            layer = self.dlg.ui.layerCombo.itemData(index) 
        # layer = QgsVectorLayer(self.fileName, "layer_name", "ogr")
 

        nFeat = layer.featureCount()
        layer.startEditing()

        

        # Should really put these in a function

        # index = layer.fieldNameIndex("qLts")
        # if index == -1: # field doesn't exist
        #     caps = layer.dataProvider().capabilities()
        #     if caps & QgsVectorDataProvider.AddAttributes:
        #       res = layer.dataProvider().addAttributes( [ QgsField("qLts", \
        #         QVariant.Int) ] )
        #     layer.updateFields()
        index = layer.fieldNameIndex("qNum_lane")
        if index == -1: # field doesn't exist
            caps = layer.dataProvider().capabilities()
            if caps & QgsVectorDataProvider.AddAttributes:
              res = layer.dataProvider().addAttributes( [ QgsField("qNum_lane", \
                QVariant.Int) ] )
            layer.updateFields()

        index = layer.fieldNameIndex("qProtected")
        if index == -1: # field doesn't exist
            caps = layer.dataProvider().capabilities()
            if caps & QgsVectorDataProvider.AddAttributes:
              res = layer.dataProvider().addAttributes( [ QgsField("qProtected", \
                QVariant.Int) ] )
            layer.updateFields()
        index = layer.fieldNameIndex("qBike_lane")
        if index == -1: # field doesn't exist
            caps = layer.dataProvider().capabilities()
            if caps & QgsVectorDataProvider.AddAttributes:
              res = layer.dataProvider().addAttributes( [ QgsField("qBike_lane", \
                QVariant.Int) ] )
            layer.updateFields()
        index = layer.fieldNameIndex("CROSSINGME")
        if index == -1: # field doesn't exist
            caps = layer.dataProvider().capabilities()
            if caps & QgsVectorDataProvider.AddAttributes:
              res = layer.dataProvider().addAttributes( [ QgsField("CROSSINGME", \
                QVariant.Int) ] )
            layer.updateFields()
        index = layer.fieldNameIndex("qLts11")
        if index == -1: # field doesn't exist
            caps = layer.dataProvider().capabilities()
            if caps & QgsVectorDataProvider.AddAttributes:
              res = layer.dataProvider().addAttributes( [ QgsField("qLts11", \
                QVariant.Int) ] )
            layer.updateFields()
        index = layer.fieldNameIndex("qLts12")
        if index == -1: # field doesn't exist
            caps = layer.dataProvider().capabilities()
            if caps & QgsVectorDataProvider.AddAttributes:
              res = layer.dataProvider().addAttributes( [ QgsField("qLts12", \
                QVariant.Int) ] )
            layer.updateFields()
        index = layer.fieldNameIndex("qLts13")
        if index == -1: # field doesn't exist
            caps = layer.dataProvider().capabilities()
            if caps & QgsVectorDataProvider.AddAttributes:
              res = layer.dataProvider().addAttributes( [ QgsField("qLts13", \
                QVariant.Int) ] )
            layer.updateFields()
        index = layer.fieldNameIndex("qLts_woX")
        if index == -1: # field doesn't exist
            caps = layer.dataProvider().capabilities()
            if caps & QgsVectorDataProvider.AddAttributes:
              res = layer.dataProvider().addAttributes( [ QgsField("qLts_woX", \
                QVariant.Int) ] )
            layer.updateFields()
        # index = layer.fieldNameIndex("LTS")
        # if index == -1: # field doesn't exist
        #     caps = layer.dataProvider().capabilities()
        #     if caps & QgsVectorDataProvider.AddAttributes:
        #       res = layer.dataProvider().addAttributes( [ QgsField("LTS", \
        #         QVariant.Int) ] )
        #     layer.updateFields()



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
            street.raw_cross_stress = feature['qRawCrossS']
            street.cross_treat = feature['CrossTreat']

            street.calculate_crossing_me(street.num_lane) # has to always be before computing lts
            street.compute_LTS()
            if street.LTS != None :
                i+=1
                j=ceil(i/(nFeat/100))
                self.dlg.ui.progress_bar.setValue(j)
            feature["qLts_woX"] = street.LTS
            # feature["qLts"] = street.LTS
            feature["qLts11"] = street.lts11
            feature["qLts12"] = street.lts12
            feature["qLts13"] = street.lts13
            feature["qNum_lane"] = street.num_lane
            feature["qBike_lane"] = street.bike_lane
            feature["qProtected"] = street.protected
            feature["CROSSINGME"] = street.crossing_me
            layer.updateFeature(feature)
        # layer.updateFields()
        # QMessageBox.information(self.dlg, ("WAIT"), ("Please wait!"))
        layer.commitChanges()
            # layer.commitChanges()
        QMessageBox.information(self.dlg, ("Successful"), ("LTS has been computed!"))  

        self.dlg.close()


    def find_connected_components(self):
        """finds "islands" in the network """
        index = self.dlg.ui.layerCombo.currentIndex() 
        if index < 0: 
            # it may occur if there's no layer in the combo/legend 
            pass
        else: 
            layer = self.dlg.ui.layerCombo.itemData(index) 
        # layer = QgsVectorLayer(self.fileName, "layer_name", "ogr")


        index = self.dlg.ui.lts_combo.currentIndex() 
        if index < 0: 
            # it may occur if there's no layer in the combo/legend 
            pass
        else: 
            lts_column = self.dlg.ui.lts_combo.itemData(index) 
        # with open("C:\Users\Peyman.n\Dropbox\Boulder\Plugin\LTS\log.txt","w")as file:
        #     file.write(lts_column +"\n")
            
        lts1_existed = self.make_column(layer,"qIsl_lts1")
        lts2_existed = self.make_column(layer,"qIsl_lts2")
        lts3_existed = self.make_column(layer,"qIsl_lts3")
        lts4_existed = self.make_column(layer,"qIsl_lts4")
        # path = "C:/Users/Peyman.n/Dropbox/Boulder/BoulderStreetsRating_20140407_Peter/for_test.shp"
        # out_path = "C:/Users/Peyman.n/Dropbox/Boulder/BoulderStreetsRating_20140407_Peter"
        # get the path from selected layer
        myfilepath= os.path.dirname( unicode( layer.dataProvider().dataSourceUri() ) ) ;
        layer_name = layer.name()
        path2 = myfilepath +"/"+layer_name+".shp"
        out_path = myfilepath
        # with open("C:\Users\Peyman.n\Dropbox\Boulder\Plugin\LTS\log.txt","a")as file:
        #     file.write(path2 +"\n")
        # ##
        # path3="C:/Users/Peyman.n/Dropbox/Boulder/BoulderStreetsRating_20140407_Peter/BoulderStreetsWProjection_20140407_Joined.shp"
        layer2 = nx.read_shp(str(path2))
        self.dlg.ui.progressBar.setValue(5)
        G=layer2.to_undirected()
        self.dlg.ui.progressBar.setValue(10)
        lts_threshs = [(1,"qIsl_lts1"),(2,"qIsl_lts2"),(3,"qIsl_lts3"),(4,"qIsl_lts4")]
        field = str(lts_column)
        # with open("C:\Users\Peyman.n\Dropbox\Boulder\Plugin\LTS\log.txt","a")as file:
        #     file.write(field +"\n")
        prog =0
        for lts_thresh,attr in (lts_threshs):
            prog +=1
            temp = [(u,v,d) for u,v,d in G.edges_iter(data=True) if d[field] <= lts_thresh]  # set the edges numbers to zero
            g2 = nx.Graph(temp)
            H=nx.connected_component_subgraphs(g2)

            for idx, cc in enumerate(H):
                for edge in cc.edges(data=True):
                    G[edge[0]][edge[1]][attr]=idx+1 # zero means it was filtered out
            j= prog * 20
            self.dlg.ui.progressBar.setValue(j)

        # order attributes table
        for index, edge in enumerate (G.edges(data=True)):
            edge = list(edge)
            edge[2] = OrderedDict(sorted(edge[2].items()))
            edge=tuple(edge)
            G[edge[0]][edge[1]] = edge[2] 


        self.remove_column(layer,"qIsl_lts1",lts1_existed)
        self.remove_column(layer,"qIsl_lts2",lts2_existed)
        self.remove_column(layer,"qIsl_lts3",lts3_existed)
        self.remove_column(layer,"qIsl_lts4",lts4_existed)


        out_name =str(layer_name+"_with islands")
        write_shp(G,out_path,out_name)
        self.dlg.ui.progressBar.setValue(99)

        QMessageBox.information(self.dlg, ("Successful"), ("A new shapefile "+ out_name+" has been created in your folder")) 
        self.dlg.ui.progressBar.setValue(100)

        # Add to TOC
        vlayer = QgsVectorLayer(out_path +"/"+out_name+".shp",out_name,"ogr")
        #get crs of project
        actual_crs = iface.mapCanvas().mapRenderer().destinationCrs()
        #change crs of layer
        vlayer.setCrs(actual_crs)

        QgsMapLayerRegistry.instance().addMapLayer(vlayer)
        
        self.dlg.close()
################################################################################

















    def compute_connectivity(self):
        #################################### Inputs and Initiaizations#######################################
        '''
        Should get lts_column from a combobox
        Networkx doesn't return a length if there is no path between the two points; it simply ignores it
        '''
        self.dlg.ui.progress_text.setText("Start")

        index = self.dlg.ui.LtsColumn.currentIndex() 
        if index < 0: 
            # it may occur if there's no layer in the combo/legend 
            pass
        else: 
            lts_column = self.dlg.ui.LtsColumn.itemData(index)
        
        

        index = self.dlg.ui.road_combo.currentIndex() 
        if index < 0:  
            pass
        else: 
            rd_layer = self.dlg.ui.road_combo.itemData(index) 

        index = self.dlg.ui.taz_combo.currentIndex() 
        if index < 0:  
            pass
        else: 
            tz_layer = self.dlg.ui.taz_combo.itemData(index) 

        myfilepath= os.path.dirname( ( rd_layer.dataProvider().dataSourceUri() ) ) ;
        layer_name = rd_layer.name()
        path = myfilepath +"/"+layer_name+".shp"
        # Get street network
        road_layer = nx.read_shp(str(path))
        
        # Get TAZ layer
        myfilepath= os.path.dirname( ( tz_layer.dataProvider().dataSourceUri() ) ) ;
        layer_name = tz_layer.name()
        path = myfilepath +"/"+layer_name+".shp" # or instead of all this: layer.source()
        # taz_layer = nx.read_shp(path)
        qgis_taz_layer = tz_layer

        total_pop = 0.0; total_emp = 0.0
        for g in qgis_taz_layer.getFeatures():
            total_pop += g['taz2010_Po']
            total_emp += g['taz2010_Em']

        maximum_distance = int(self.dlg.ui.maxDist.text())       # 1000 #in ft
        minimum_distance = int(self.dlg.ui.minDist.text())       # 15 # in ft
        detour_coeff = float(self.dlg.ui.Detour_coeff.text())      # 1.33 # if lts2.length <= 1.33 lts4.length : connected Detour_coeff

        disconnected_pop = {}
        disconnected_emp = {}
        employment_connectivity = {}
        population_connectivity = {}
        for i in range(1,5): # for LTS 1:4
            employment_connectivity.setdefault(i,0.0)
            population_connectivity.setdefault(i,0.0)
            disconnected_pop.setdefault(i,0.0)
            disconnected_emp.setdefault(i,0.0)

        time_1 = time.time()
        self.dlg.ui.progress_text.append("done Initiaizations")
        # print "done Initiaizations",time_1 - start
        ####################################################################################

        # c=processing.runalg("saga:convertpolygonlineverticestopoints",rd_layer,'C:/Users/Peyman.n/Dropbox/Boulder/Shapefies from internet/points') # get intersection points
        destination_file = str(myfilepath) + '/points.shp'
        c=processing.runalg("saga:convertpolygonlineverticestopoints",rd_layer, destination_file) # get intersection points
        
        # self.dlg.ui.progress_text.append(destination_file)

        vlayer = QgsVectorLayer(destination_file, "points", "ogr")

        destination_file = str(myfilepath) + '/points1.shp'
        c=processing.runalg("saga:addpolygonattributestopoints",vlayer,
            qgis_taz_layer,"taz2010_PO",destination_file)
        vlayer = QgsVectorLayer(destination_file, "points1", "ogr")

        # self.dlg.ui.progress_text.append(destination_file)

        destination_file = str(myfilepath) + '/points2.shp'
        c=processing.runalg("saga:addpolygonattributestopoints",vlayer,
            qgis_taz_layer,"taz2010_EM",destination_file)
        vlayer = QgsVectorLayer(destination_file, "points2", "ogr")

        # self.dlg.ui.progress_text.append(destination_file)

        destination_file = str(myfilepath) + '/points3.shp'
        c=processing.runalg("saga:addpolygonattributestopoints",vlayer,
            qgis_taz_layer,"TAZ_ID",destination_file)
        vlayer = QgsVectorLayer(destination_file, "points3", "ogr")

        # self.dlg.ui.progress_text.append(destination_file)

        # REMOVE DUPLICATES
        destination_file = str(str(myfilepath) + '/points44.shp')
        c=processing.runalg("saga:removeduplicatepoints",vlayer,"ID_SHAPE",0,0,destination_file)
        # self.dlg.ui.progress_text.append(destination_file)
        vlayer = QgsVectorLayer(destination_file, "points44", "ogr")



        node_layer = nx.read_shp(destination_file)
        ### make a graph out of nodes and street layer
        # Node graph with attributes
        node_graph = node_layer.to_undirected()
        # Street graph
        street_graph = road_layer.to_undirected()
        try:
            del vlayer
            del c
            del node_layer
            del destination_file

        except Exception, e:
            pass
        time_2 = time.time()
        self.dlg.ui.progress_text.append("done intersections")

        ##################################################################
        ### Select a subset of nodes for analysis ########################
        taz_dic = {}
        # list_of_random_nodes = []
        for node, attr in node_graph.nodes_iter(data=True):
            taz_dic.setdefault(attr['TAZ_ID'],[]).append(node) 
        try:
            del taz_dic[0.0]
        except:
            pass
        # self.dlg.ui.progress_text.append(str(len(taz_dic)))

        # selected_nodes = []
        # with open("C:\Users\Peyman.n\Dropbox\Boulder\Shapefies from internet\\taz_dic.txt","w") as file:
        #     pickle.dump(taz_dic,file)
        # with open("C:\Users\Peyman.n\Dropbox\Boulder\Shapefies from internet\\street_graph.txt","w") as file:
        #     pickle.dump(street_graph,file)
        # with open("C:\Users\Peyman.n\Dropbox\Boulder\Shapefies from internet\\node_graph.txt","w") as file:
        #     pickle.dump(node_graph,file)
        def sample_geo_nodes(list_of_nodes, number_of_points_wanted, street_graph = street_graph):
            ''' returns a list,samples nodes that are m apart'''
            number_of_given_nodes = len(list_of_nodes)
            number_of_points = 0
            if number_of_given_nodes <= number_of_points_wanted:
                return list_of_nodes
            items = random.sample(list_of_nodes, number_of_points_wanted)
            number_of_red_nodes = 0
            sampled = [node for node in items if node  in street_graph.nodes()]
            remainder = [node for node in list_of_nodes if node not in items]
            sampled_length = len(sampled)
            remainder_length = len(remainder)
            number_needed = number_of_points_wanted - sampled_length
            if number_needed > 0:
                if number_needed <= remainder_length:
                    new_items = sample_geo_nodes(remainder, number_needed)
                    items.extend(new_items)
                else:
                    new_items = remainder
                    items.extend(new_items)
                return items 
            else:
                return items    

        selected_nodes = {}
        number_tobe_sampled = 5
        for taz, list_of_nodes in taz_dic.iteritems():
            items = sample_geo_nodes(list_of_nodes, number_tobe_sampled)
            selected_nodes[taz] = (items, len(items)) 


        # for taz, list_of_nodes in taz_dic.iteritems():
        #     number_of_points = min(5,len(list_of_nodes) )
        #     passed_nodes = 0
        #     for i in range( number_of_points*5 ): # check 5 times more points
        #         if passed_nodes >= number_of_points: 
        #             break
        #         item = random.sample(list_of_nodes, 1) #choose 10 features
        #         if item[0] in street_graph.nodes():
        #             passed_nodes += 1
        #             selected_nodes.extend(item)


        time_3 = time.time()
        # self.dlg.ui.progress_text.append("length of selected_nodes")
        # self.dlg.ui.progress_text.append(str(len(selected_nodes)))

        self.dlg.ui.progress_text.append("done subset")

        # with open("C:\Users\Peyman.n\Dropbox\Boulder\Shapefies from internet\\selected_nodes.txt","w") as file:
        #     pickle.dump(selected_nodes,file)
        #####
        # some analysis of average network connectivity
        # node_info1 = {}; node_info2 = {}; node_info3 = {}; node_info4 = {}; 
        # all_cons_nodes = {} # node: population
        ### do the SP analysis
        # missing_nodes1=0; missing_nodes2=0; missing_nodes3=0; missing_nodes4=0;
        # runLTS4 = False; runLTS3 = False; runLTS2 = False; runLTS1 = False; 

        
        ##################################################################

        ### make a graph for each level of lts
        lts_threshs = [1,2,3]
        graph_lts1=[]; graph_lts2=[]; graph_lts3=[]
        graph_names = [graph_lts1, graph_lts2, graph_lts3]
        field = str(lts_column)

        # another approach might be to create one graph at a time and do the analysis for that; more memory efficient???
        for index,lts_thresh in enumerate(lts_threshs ): #fix this
            temp = [(u,v,d) for u,v,d in street_graph.edges_iter(data=True) if d[field] <= lts_thresh]  # set the edges numbers to zero
            graph_names[index] = nx.Graph(temp)
            
        time_4 = time.time()
        self.dlg.ui.progress_text.append("done making graphs")

        counter = 0
        

        ### do the SP analysis
        for taz, ll  in selected_nodes.iteritems():
            list_of_nodes = ll[0]
            num_of_nodes = ll[1]
            for node in list_of_nodes:

            ###########
                # all_cons_nodes[node] = node_graph.node[node]['TAZ2010_PO']/total_pop
                ###########
                pnts1 = 0; pnts2 = 0; pnts3 = 0; pnts4 = 0;
                runLTS4 = False; runLTS3 = False; runLTS2 = False; runLTS1 = False; 

                counter += 1
                if counter == 100 : print "100", time.time() - time_4
                if counter == 300 : print "300", time.time() - time_4
                if counter == 600 : print "600", time.time() - time_4
                if counter == 900 : print "900", time.time() - time_4
                if counter == 1100 : print "1100", time.time() - time_4
                if counter == 1500 : print "1500", time.time() - time_4




                # Dictionary of shortest lengths keyed by target.{0: 0, 1: 1, 2: 2, 3: 3, 4: 4}
                if pnts4 < 5 : # this is just to make sure that the selected node is not one of the 89 nodes that are "extra" in node layer
                    try:
                        length_lts4=nx.single_source_dijkstra_path_length(street_graph, node, weight='LEN', cutoff=maximum_distance)
                        # node_info4[node] = len (length_lts4.keys())
                        pnts4 += 1
                        runLTS4 = True
                    except Exception, e: # node not in that LTS network -> not connected
                        # missing_nodes4 += 1                                                 
                        continue  # if it's not in LTS4 graph, then it is not in the others either, so just "continue" to the next one

                if pnts3 < 5 :
                    try:
                        length_lts3=nx.single_source_dijkstra_path_length(graph_names[2], node, weight='LEN', cutoff=maximum_distance) 
                        # node_info3[node] = len (length_lts3.keys())
                        pnts3 += 1
                        runLTS3 = True
                    except Exception, e: # node not in that LTS network -> not connected
                        # missing_nodes3 += 1  
                        pass
                         
                if pnts2 < 5 :
                    try:
                        length_lts2=nx.single_source_dijkstra_path_length(graph_names[1], node, weight='LEN', cutoff=maximum_distance) 
                        # node_info2[node] = len (length_lts2.keys())
                        pnts2 += 1
                        runLTS2 = True

                    except Exception, e:
                        pass
                        # missing_nodes2 += 1                                                 
                         
                if pnts1 < 5 :  
                    try:
                        length_lts1=nx.single_source_dijkstra_path_length(graph_names[0], node, weight='LEN', cutoff=maximum_distance) 
                        # node_info1[node] = len (length_lts1.keys())
                        pnts1 += 1
                        runLTS1 = True

                    except Exception, e:
                        # missing_nodes1 += 1 
                        pass                                                
                        
                    

                origin_pop = node_graph.node[node]['TAZ2010_PO'] /total_pop/num_of_nodes # how long is it gonna take to find these nodes?
                assert origin_pop >= 0, "negative Origin Population"

                if runLTS1:
                    # try:
                    for taz2, ll2  in selected_nodes.iteritems():
                        list_of_nodes2 = ll2[0]
                        num_of_nodes2 = ll2[1]

                        for dest in list_of_nodes2:
                            if node != dest:
                                try :
                                    distance = length_lts1[dest]
                                    if length_lts4[dest] >= minimum_distance and distance <= detour_coeff * length_lts4[dest] :

                        
                                        dest_pop = node_graph.node[dest]['TAZ2010_PO']/total_pop/num_of_nodes
                            # temp += origin_pop * dest_pop
                                        assert dest_pop >= 0, "negative Population"

                                        dest_emp = node_graph.node[dest]['TAZ2010_EM']/total_emp/num_of_nodes
                            # if distance >= minimum_distance :
                                
                                # origin_pop = node_graph.nodes()[node]['Pop'] # how long is it gonna take to find these nodes?
                                # dest_pop = node_graph.node[dest]['TAZ2010_PO']/total_pop
                                # dest_emp = node_graph.node[dest]['TAZ2010_EM']/total_emp
                                        if dest_emp < 0: dest_emp =0
                                        assert dest_emp >= 0, "negative employment"

                                # tempDEL.append(origin_pop * dest_pop)
                                # destDEL.append(dest_pop)
                                # orgDEL.append(origin_pop)

                                # file.write(str(origin_pop * dest_pop))
                                        population_connectivity[1] += origin_pop * dest_pop
                                        employment_connectivity[1] += origin_pop * dest_emp
                                    else: 
                                        disconnected_pop[1] += origin_pop * dest_pop
                                        disconnected_emp[1] += origin_pop * dest_emp
                                except Exception,e :
                                    pass 
                    

                if runLTS2:
                    # try:
                    for taz2, ll2  in selected_nodes.iteritems():
                        list_of_nodes2 = ll2[0]
                        num_of_nodes2 = ll2[1]

                        for dest in list_of_nodes2:
                            if node != dest:
                                try :
                                    distance = length_lts2[dest]
                                    if length_lts4[dest] >= minimum_distance and distance <= detour_coeff * length_lts4[dest] :

                        
                                        dest_pop = node_graph.node[dest]['TAZ2010_PO']/total_pop/num_of_nodes
                            # temp += origin_pop * dest_pop
                                        assert dest_pop >= 0, "negative Population"

                                        dest_emp = node_graph.node[dest]['TAZ2010_EM']/total_emp/num_of_nodes
                            # if distance >= minimum_distance :
                                
                                # origin_pop = node_graph.nodes()[node]['Pop'] # how long is it gonna take to find these nodes?
                                # dest_pop = node_graph.node[dest]['TAZ2010_PO']/total_pop
                                # dest_emp = node_graph.node[dest]['TAZ2010_EM']/total_emp
                                        if dest_emp < 0: dest_emp =0
                                        assert dest_emp >= 0, "negative employment"

                                # tempDEL.append(origin_pop * dest_pop)
                                # destDEL.append(dest_pop)
                                # orgDEL.append(origin_pop)

                                # file.write(str(origin_pop * dest_pop))
                                        population_connectivity[2] += origin_pop * dest_pop
                                        employment_connectivity[2] += origin_pop * dest_emp
                                    else: 
                                        disconnected_pop[2] += origin_pop * dest_pop
                                        disconnected_emp[2] += origin_pop * dest_emp
                                except Exception,e :
                                    pass 
                    
                if runLTS3:
                    # try:
                    for taz2, ll2  in selected_nodes.iteritems():
                        list_of_nodes2 = ll2[0]
                        num_of_nodes2 = ll2[1]

                        for dest in list_of_nodes2:
                            if node != dest:
                                try :
                                    distance = length_lts3[dest]
                                    if length_lts4[dest] >= minimum_distance and distance <= detour_coeff * length_lts4[dest] :

                        
                                        dest_pop = node_graph.node[dest]['TAZ2010_PO']/total_pop/num_of_nodes
                            # temp += origin_pop * dest_pop
                                        assert dest_pop >= 0, "negative Population"

                                        dest_emp = node_graph.node[dest]['TAZ2010_EM']/total_emp/num_of_nodes
                            # if distance >= minimum_distance :
                                
                                # origin_pop = node_graph.nodes()[node]['Pop'] # how long is it gonna take to find these nodes?
                                # dest_pop = node_graph.node[dest]['TAZ2010_PO']/total_pop
                                # dest_emp = node_graph.node[dest]['TAZ2010_EM']/total_emp
                                        if dest_emp < 0: dest_emp =0
                                        assert dest_emp >= 0, "negative employment"

                                # tempDEL.append(origin_pop * dest_pop)
                                # destDEL.append(dest_pop)
                                # orgDEL.append(origin_pop)

                                # file.write(str(origin_pop * dest_pop))
                                        population_connectivity[3] += origin_pop * dest_pop
                                        employment_connectivity[3] += origin_pop * dest_emp
                                    else: 
                                        disconnected_pop[3] += origin_pop * dest_pop
                                        disconnected_emp[3] += origin_pop * dest_emp
                                except Exception,e :
                                    pass 
                    
                if runLTS4:
                    # try:
                    for taz2, ll2  in selected_nodes.iteritems():
                        list_of_nodes2 = ll2[0]
                        num_of_nodes2 = ll2[1]
                    # if node != dest:
                        for dest in list_of_nodes2:

                            try :
                                distance = length_lts4[dest]
                                if distance >= minimum_distance :
       
                                    dest_pop = node_graph.node[dest]['TAZ2010_PO']/total_pop/num_of_nodes
                        # temp += origin_pop * dest_pop
                                    assert dest_pop >= 0, "negative Population"

                                    dest_emp = node_graph.node[dest]['TAZ2010_EM']/total_emp/num_of_nodes
                        # if distance >= minimum_distance :
                            
                            # origin_pop = node_graph.nodes()[node]['Pop'] # how long is it gonna take to find these nodes?
                            # dest_pop = node_graph.node[dest]['TAZ2010_PO']/total_pop
                            # dest_emp = node_graph.node[dest]['TAZ2010_EM']/total_emp
                                    if dest_emp < 0: dest_emp =0
                                    assert dest_emp >= 0, "negative employment"

                            # tempDEL.append(origin_pop * dest_pop)
                            # destDEL.append(dest_pop)
                            # orgDEL.append(origin_pop)

                            # file.write(str(origin_pop * dest_pop))
                                    population_connectivity[4] += origin_pop * dest_pop
                                    employment_connectivity[4] += origin_pop * dest_emp
                                else: 
                                    disconnected_pop[4] += origin_pop * dest_pop
                                    disconnected_emp[4] += origin_pop * dest_emp
                            except Exception,e :
                                pass 



        time_5 = time.time()
        self.dlg.ui.progress_text.append("Done!")
        self.dlg.ui.progress_text.append("employment_connectivity[4] is " + str(employment_connectivity[4]))
        self.dlg.ui.progress_text.append("population_connectivity[4] is " + str(population_connectivity[4]))


        # SHOULD SAVE OUTPUT TO EXCEL FILE
        import time 
        a = time.strftime("%H:%M:%S")
        c = a.replace(":","_")
        writefile = myfilepath+'\\results '+ c+'.csv'
        fieldnames = ['LTS level','population_connectivity', 'employment_connectivity']
        fieldnames2 = ['LTS level','population_disqualified', 'employment_disqualified']

        with open( writefile, 'w' ) as f:
            writer = csv.writer(f)
            writer.writerow(fieldnames)
            for i in range(1,5):
                writer.writerow((i,population_connectivity[i] , employment_connectivity[i]))
            writer.writerow(fieldnames2)
            for i in range(7,11):
                writer.writerow((i,disconnected_pop[i-6] , disconnected_emp[i-6]))


        try :
            del street_graph
            del node_graph
            del node_layer
            del destination_file
        except:
            pass 
        # delete new files
        for i in ["\\points.shp","\\points1.shp","\\points2.shp","\\points3.shp","\\points4.shp",
            "\\points.shx","\\points1.shx","\\points2.shx","\\points3.shx","\\points4.shx",
            "\\points.dbf","\\points1.dbf","\\points2.dbf","\\points3.dbf","\\points4.dbf",
            "\\points.prj","\\points1.prj","\\points2.prj","\\points3.prj","\\points4.prj"]:
            try:
                target = str( myfilepath + i)
                os.remove(target)
            except:
                pass

        try:
            os.remove( str( myfilepath + "\\points.shp"))
        except:
            pass 


##########################


    # run method that performs all the real work
    def run(self):
        # show the dialog
        self.dlg.show()
        self.dlg.ui.progress_text.clear()
        self.dlg.ui.progressBar.setValue(0)
        self.dlg.ui.progress_bar.setValue(0)
        self.dlg.ui.layerCombo.clear()
        self.dlg.ui.lts_combo.clear()
        self.dlg.ui.road_combo.clear()
        self.dlg.ui.taz_combo.clear()
        self.dlg.ui.LtsColumn.clear()

        layers = QgsMapLayerRegistry.instance().mapLayers().values()
        for layer in layers:
            if layer.type() == QgsMapLayer.VectorLayer and layer.geometryType() == QGis.Line:
                self.dlg.ui.layerCombo.addItem( layer.name(), layer ) 
                self.dlg.ui.road_combo.addItem( layer.name(), layer ) 
            if layer.type() == QgsMapLayer.VectorLayer and layer.geometryType() == QGis.Polygon:
                self.dlg.ui.taz_combo.addItem( layer.name(), layer ) 
                




        self.update_lts_field()
        self.update_conn_lts_field()
        # Run the dialog event loop
        result = self.dlg.exec_()
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
        if (not self.one_way) or (self.one_way == "None"):  #it's 2 way 
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

        # if self.cross_LTS != NULL: # what is this?
        #     update_LTS(int(self.cross_LTS))

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
    ##################### End of Street Class #####################
    #############################################################################################################

