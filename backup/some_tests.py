layer = qgis.utils.iface.activeLayer()

for feature in layer.getFeatures():
    numberOfLane = feature['NUMLANE']
    lts = feature ['_lts12']
    islLTS_1 = feature['_isl_lts1']
    islLTS_2 = feature['_isl_lts2'] 
    islLTS_3 = feature['_isl_lts3'] 
    islLTS_4 = feature['_isl_lts4'] 
    if lts ==1 : assert islLTS_1 > 0
    elif lts ==2 :
        assert islLTS_1 == 0
        assert islLTS_2 > 0
    elif lts ==3 :
        assert islLTS_1 == islLTS_2 == 0
        assert islLTS_3 > 0
    elif lts ==4 :
        assert islLTS_1 == islLTS_2 == islLTS_3 == 0
        assert islLTS_4 > 0