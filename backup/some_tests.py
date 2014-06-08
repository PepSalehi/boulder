layer = qgis.utils.iface.activeLayer()

for feature in layer.getFeatures():
    numberOfLane = feature['NUMLANE']
    lts = feature ['qLts12']
    islLTS_1 = feature['qIsl_lts1']
    islLTS_2 = feature['qIsl_lts2'] 
    islLTS_3 = feature['qIsl_lts3'] 
    islLTS_4 = feature['qIsl_lts4'] 
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
else:
	print "Yoohoo, no errors!"