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
 This script initializes the plugin, making it known to QGIS.
"""

def classFactory(iface):
    # load Test class from file Test
    from test import Test
    return Test(iface)
