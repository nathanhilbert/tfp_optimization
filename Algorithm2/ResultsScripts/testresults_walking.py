# -*- coding: utf-8 -*-
"""
Created on Fri Nov 09 13:51:43 2012

@author: hilbert.34
"""

import sqlite3
import pickle
import csv

def calcOtherCosts(conn, transtotcost, transothercosts, storetransIndex, parcel,stores, ANATYPE):
    c = conn.cursor()
    transcost = float(0)
    travelcost = float(0)
    timecost = float(0)
        
    if (ANATYPE == "driving"):
        c.execute("SELECT totcost, travelcost, timecost FROM transcosts WHERE orig=? AND dest=?", (parcel, stores[0]))
        tempvalues = c.next()
        transcost += float(tempvalues[0])
        travelcost += float(tempvalues[1])
        timecost += float(tempvalues[2])
        c.execute("SELECT totcost, travelcost, timecost FROM transcosts WHERE orig=? AND dest=?", (parcel, stores[-1]))
        tempvalues = c.next()
        transcost += float(tempvalues[0])
        travelcost += float(tempvalues[1])
        timecost += float(tempvalues[2])
    else:
        c.execute("SELECT totcost, totbus, tottime FROM transcosts WHERE orig=? AND dest=?", (parcel, stores[0]))
        tempvalues = c.next()
        transcost += float(tempvalues[0])
        travelcost += float(tempvalues[1])
        timecost += float(tempvalues[2])
        c.execute("SELECT totcost, totbus, tottime FROM transcosts WHERE orig=? AND dest=?", (parcel, stores[-1]))
        tempvalues = c.next()
        transcost += float(tempvalues[0])
        travelcost += float(tempvalues[1])
        timecost += float(tempvalues[2])
    #now do store to store
    for storeindex in range(1, len(stores)):
        transcost += float(transtotcost[storetransIndex[stores[storeindex-1]]][storetransIndex[stores[storeindex]]])
        travelcost += float(transothercosts["cost1"][storetransIndex[stores[storeindex-1]]][storetransIndex[stores[storeindex]]])
        timecost += float(transothercosts["cost2"][storetransIndex[stores[storeindex-1]]][storetransIndex[stores[storeindex]]])
    return transcost, travelcost, timecost




def getKeyValue(thelist,value):
    return [k for k, v in thelist.iteritems() if v == value][0]

OUTPUTDIR = "D:/GIS Project Data/Food Optimization/Nov14-driving/Output/"
BASEDIR = "D:/GIS Project Data/Food Optimization/Nov14-driving/basefiles/"


ANATYPE = "walking"


resultsconn = sqlite3.connect(OUTPUTDIR + ANATYPE + "_results.db")
resultscursor = resultsconn.cursor()

#resultscursor.execute("""CREATE TABLE results (parcel TEXT, totcost REAL, picklestores TEXT, picklefoodcost TEXT, picklefoodstores TEXT)""")
 
with open(OUTPUTDIR + ANATYPE + "_foodindex.pickle", 'rb') as f:
    foodindex = pickle.load(f)

#with open(OUTPUTDIR + ANATYPE + "_storeindex.pickle", 'rb') as f:
#    freqstorevisits = pickle.load(f)
#    for key in freqstorevisits:
#        freqstorevisits[key] = 0
        
foodclassed = {"fruits":[], "vegetables":[], "other":[], "grains":[], "dairy":[], "meatsbeans":[]}
with open(BASEDIR + "foodclassification.csv", 'rb') as f:
    reader = csv.reader(f)
    for row in reader:
        #now has the index of the food index 
        foodclassed[row[1]].append(foodindex[row[0]])
ANATYPE = "driving"

#get transportation matrix for the parcels and stores
import numpy as np

with open(BASEDIR + ANATYPE + "_transcosts.pickle", 'rb') as f:
    dataset = pickle.load(f)
    transtotcost = np.squeeze(np.asarray(dataset['totcost']))
    if (ANATYPE == "driving"):
        #transothercosts = {"costtot":dataset['travelcost'], "timecost":dataset['timecost']}
        transothercosts = {"cost1":np.squeeze(np.asarray(dataset['travelcost'])), "cost2":np.squeeze(np.asarray(dataset['timecost']))}
    else:
        #transothercosts = {"totbus":dataset['totbus'], "timecost":dataset['timecost']}
        transothercosts = {"cost1":np.squeeze(np.asarray(dataset['totbus'])), "cost2":np.squeeze(np.asarray(dataset['timecost']))}
    storetransIndex = {}
    freqstorevisits = {}
    for thestore, myindex in zip(dataset['theindex'], range(len(dataset['theindex']))):
        storetransIndex[thestore] = myindex
        freqstorevisits[thestore] = 0

#this outputs transtotcost, transothercosts, storetransIndex


conn = sqlite3.connect(BASEDIR + "parcelstoretrans_" + ANATYPE + ".txt")



 
resultscursor.execute('SELECT parcel,totcost, picklestores, picklefoodcost,picklefoodstores FROM results GROUP BY parcel ORDER BY parcel') 

limit = None
counterlimit = 0


outputarray = []
for row in resultscursor:
    
    temparray = []
    parcel = row[0]
    print "doing ", parcel
    totcost = row[1]
    stores = pickle.loads(str(row[2]))
    foodcosts = pickle.loads(str(row[3]))
    foodstores = pickle.loads(str(row[4]))
    
    temparray.append(parcel)
    temparray.append(totcost)
    temparray.append(str(stores))
    
    #now building the other costs
    totaltrans, travelcost, timecost = calcOtherCosts(conn, transtotcost, transothercosts, storetransIndex, parcel,stores, ANATYPE)
    temparray.append(totaltrans)
    temparray.append(travelcost)
    temparray.append(timecost)
    
    temparray.append(np.sum(foodcosts))
    
    temparray.append(np.sum(foodcosts[foodclassed['fruits']]))
    temparray.append( np.sum(foodcosts[foodclassed['vegetables']]))
    temparray.append(np.sum(foodcosts[foodclassed['other']]))
    temparray.append(np.sum(foodcosts[foodclassed['grains']]))
    temparray.append(np.sum(foodcosts[foodclassed['dairy']]))
    temparray.append(np.sum(foodcosts[foodclassed['meatsbeans']]))
    

    for foodstore in foodstores:
        freqstorevisits[foodstore] +=1
        

    outputarray.append(temparray)
    counterlimit +=1
    if counterlimit > limit and limit != None:
        break
print "writing the files"
with open(OUTPUTDIR + ANATYPE + "_final_results.csv", 'wb') as f:
    outputwriter = csv.writer(f)
    if ANATYPE == "walking":
        outputwriter.writerow(["parcel", "totcost", "storeroute", "transcost", "travelcost", "timecost", "foodcosts", "fruits",\
            "vegetables", "other", "grains", "dairy", "meatsbeans"])
    else:
        outputwriter.writerow(["parcel", "totcost", "storeroute", "transcost", "buscost", "timecost", "foodcosts", "fruits",\
            "vegetables", "other", "grains", "dairy", "meatsbeans"])
    for outputrow in outputarray:
        outputwriter.writerow(outputrow)

with open(OUTPUTDIR + ANATYPE + "_final_freqstores.csv", 'wb') as f:
    outputwriter = csv.writer(f)
    outputwriter.writerow(["Store", "freqitemsbought"])
    for storevisitsindex, storevisitsval in freqstorevisits.iteritems():
        outputwriter.writerow([storevisitsindex, storevisitsval])
print "finished"

    
#output everythign to csv