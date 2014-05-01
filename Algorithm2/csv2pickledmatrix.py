# -*- coding: utf-8 -*-
"""
Created on Wed Oct 31 13:09:44 2012

@author: hilbert.34
"""


from dbfpy import dbf
import pickle
import networkx as nx



WORKINGDIR = "D:/GIS Project Data/Food Optimization/Nov14-walking/basefiles/"

analysistype = "walking"

reader = dbf.Dbf(WORKINGDIR + "store_store_" + analysistype + ".dbf")


Gtotcost = nx.Graph()    
Gtravelcost = nx.Graph()
Gtimecost = nx.Graph()
firstrun = True
for row in reader:
    if firstrun:
        firstrun = False
        continue
    thesplit = row[1].split(" - ")
    Gtotcost.add_edge(thesplit[0],thesplit[1],weight=row[5])
    Gtravelcost.add_edge(thesplit[0],thesplit[1],weight=row[6])
    Gtimecost.add_edge(thesplit[0],thesplit[1],weight=row[7])
theindex = Gtotcost.nodes()
totcost = nx.to_numpy_matrix(Gtotcost, nodelist=theindex)
travelcost = nx.to_numpy_matrix(Gtotcost, nodelist=theindex)
timecost = nx.to_numpy_matrix(Gtimecost, nodelist=theindex)
if (analysistype == "driving"):
    dataset = {"theindex":theindex, "totcost": totcost,"travelcost":travelcost,"timecost":timecost}
    pickle.dump(dataset, open(WORKINGDIR + "driving_transcosts.pickle", 'wb'))
else:
    
    dataset = {"theindex":theindex, "totcost": totcost,"totbus":travelcost,"timecost":timecost}
    pickle.dump(dataset, open(WORKINGDIR + "walking_transcosts.pickle", 'wb'))        
    

    
        
import sys
sys.exit(1)    
    
    
#to_numpy_matrix
#    
#    
#    
#    headers = reader.next()
#    
#    totcost = []
#    travelcost = []
#    timecost = []
#    
#    
#    xindex = {}
#    yindex = {}
#    xcount = 0
#    ycount = 0
#    lastx = 0
#    
#    
#    
#    for row in reader:
#
#        thesplit = row[1].split(" - ")
#        if (lastx == 0):
#            xindex[thesplit[0]] = xcount
#            xcount +=1
#            temptotcost = []
#            temptravelcost = []
#            temptimecost = []
#            lastx = thesplit[0]
#            
#        if (thesplit[0] != lastx):
#            ycount = 0
#            xindex[thesplit[0]] =  xcount
#            xcount +=1
#            totcost.append(temptotcost)
#            temptotcost = []
#            travelcost.append(temptotcost)
#            temptravelcost = []
#            timecost.append(temptotcost)
#            temptimecost = []
#            lastx = thesplit[0]
#            
#        temptotcost.append(row[5])
#        temptravelcost.append(row[6])
#        temptimecost.append(row[7])
#        yindex[thesplit[1]] = ycount
#    print ycount
#    print xcount
#
#    print len(yindex.keys())
#
#        
#        
#        
#    
#    
