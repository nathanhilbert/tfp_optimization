# -*- coding: utf-8 -*-
"""
Created on Wed Oct 31 08:28:51 2012

@author: hilbert.34
"""

#useage is tspfunction (sets matrix of distance)
from tsp import tspfunction
from TFPalgorithm import calcParcel


import time
import csv  
import pickle
from networkx import nx
import sqlite3






#####good below this    
    
    
    
def getParcelList(conn, picklefile):
    try:
        parcelset = pickle.load(open(picklefile, 'rb'))
    except:
        
        transcursor = conn.cursor()
        parcelset = []
        transcursor.execute('SELECT orig FROM transcosts GROUP BY orig ORDER BY orig') 
        for row in transcursor:
            parcelset.append(row[0])
        pickle.dump(parcelset, open(picklefile,'wb'))
    return parcelset
    
    
    
    
def getList(filename):
    output = []

    f = open(filename, "rb")
    reader = csv.reader(f)
    for row in reader:
        output.append(row[0])

    return output
    







def getPricesFromCSV(thefile):
    with open(thefile, 'rb') as f:
        reader = csv.reader(f)
        headers = reader.next()
        excludelist = ['store_name','storetype','x','y','identnum','newident','surveyed']
        xcounter = 0
        foodindex = {}
        #build the index array for the food items
        for foodval in headers:
            if foodval not in excludelist:    
                foodindex[foodval] = xcounter
                xcounter +=1
        storeindex = {}
        priceArray = []
        counter = 0
        for row in reader:
            storeindex[row[headers.index("newident")]] = counter
            temparray = []
            for headerset, rowset in zip(headers,row):
                if headerset not in excludelist:
                    temparray.append(float(rowset))
            priceArray.append(temparray)
            counter +=1
        return storeindex, foodindex, priceArray 
  

def getParcelStoreTrans(conn, parcel, ANATYPE):

    transcursor = conn.cursor()
    print parcel
    
    if (ANATYPE == "driving"):
        transcursor.execute('SELECT dest, totcost, travelcost, timecost FROM transcosts WHERE orig="'+ parcel +'"')
    else:
        transcursor.execute('SELECT dest, totcost, totbus, tottime FROM transcosts WHERE orig="'+ parcel +'"')
    parcelstoreTrans = []
    parcelstoreIndex = {}
    counter = 0
    for row in transcursor:
        if ANATYPE == "driving":
            parcelstoreIndex[row[0]] = counter
            parcelstoreTrans.append([row[1], row[2],row[3]])
        else:
            parcelstoreIndex[row[0]] = counter
            parcelstoreTrans.append([row[1], row[2], row[3]])
        counter +=1
    transcursor.close() 
    return parcelstoreTrans, parcelstoreIndex
    


            

########Settings
ANATYPE = "driving"





WORKINGDIRECTORY = "D:/GIS Project Data/Food Optimization/Nov26-driving/basefiles/"
OUTPUTDIR = "D:/GIS Project Data/Food Optimization/Nov26-driving/Output/"

pricefilename = "FoodPrices_output_random-NLH.csv"
storeindex, foodindex, pricematrix = getPricesFromCSV(WORKINGDIRECTORY + pricefilename)
with open(OUTPUTDIR + ANATYPE + "_foodindex.pickle", 'wb') as f:
    pickle.dump(foodindex, f)
with open(OUTPUTDIR + ANATYPE + "_storeindex.pickle", 'wb') as f:
    pickle.dump(foodindex, f)
    



#get transportation matrix for the parcels and stores
import numpy as np

with open(WORKINGDIRECTORY + ANATYPE + "_transcosts.pickle", 'rb') as f:
    dataset = pickle.load(f)
    transtotcost = np.squeeze(np.asarray(dataset['totcost']))
    if (ANATYPE == "driving"):
        transothercosts = {"travelcost":dataset['travelcost'], "timecost":dataset['timecost']}
    else:
        transothercosts = {"totbus":dataset['totbus'], "timecost":dataset['timecost']}
    storetransIndex = {}
    for thestore, myindex in zip(dataset['theindex'], range(len(dataset['theindex']))):
        storetransIndex[thestore] = myindex

#this outputs transtotcost, transothercosts, storetransIndex


conn = sqlite3.connect(WORKINGDIRECTORY + "parcelstoretrans_" + ANATYPE + ".txt")





# need to get this running

import pp

#there always needs to be two of them start ppserver.py as
#C:\pypy\pypy.exe ppserver.py -w 2

#myworkers = tuple(("AMP-ARCGIS-VM",))
myworkers = tuple(())

#myworkers = tuple(())
#directories = ["C:/Users/hilbert.34/Desktop/TravelCost.csv", "D:/GIS Project Data/Food Optimization/jan25/TravelCost.csv", "C:/Users/hilbert.34/Desktop/TravelCost.csv"]


jobserver = pp.Server(ppservers=myworkers)
time.sleep(5)






parcellimit = 100
parcelcount = 0


averagetime = 0
averagecount = 0
resultfile = []
errorfile = []

doinsetsof = 36

print "building parcel list"
parcelIndex = getParcelList(conn, WORKINGDIRECTORY + "parcellist_" + ANATYPE + ".pickle")

numsets = int(len(parcelIndex)/doinsetsof)



#read the parcels that already exist in the file
spentparcels = []




resultsconn = sqlite3.connect(OUTPUTDIR + ANATYPE + "_results.db")
resultscursor = resultsconn.cursor()
try:
    resultscursor.execute("""CREATE TABLE results (parcel TEXT, totcost REAL, picklestores TEXT, picklefoodcost TEXT, picklefoodstores TEXT)""")
    resultsconn.commit()
except:
    print "table already exists continuing"
    
resultscursor.execute('SELECT parcel FROM results GROUP BY parcel ORDER BY parcel') 
for row in resultscursor:
    spentparcels.append(row[0])




errorconn = sqlite3.connect(OUTPUTDIR + ANATYPE + "_errors.db")
errorcursor = errorconn.cursor()
try:
    errorcursor.execute("""CREATE TABLE errors (parcel TEXT, errormessage TEXT)""")
    errorconn.commit()
except:
    print "table already exists continuing"






print "Here are my active nodes", str(jobserver.get_active_nodes())
lastresult = None

for x in range(0, len(parcelIndex), doinsetsof):
    chunkstart = time.time()
    try:
        thisset = parcelIndex[x:x+doinsetsof]
    except:
        thisset = parcelIndex[x:len(parcelIndex)-1]
    
    if (parcellimit != None):
        if (x > parcellimit):
            break
    jobs = {}
    actualrun = 0
    lastresult = None
    for parcel in thisset:
        if (parcel not in spentparcels):
            #travelcost, customstores = buildTravelCost(WORKINGDIRECTORY + "TravelCost.csv", parcel, conn)
            actualrun +=1
            parcelstoreTransCost, parcelstoretransindex = getParcelStoreTrans(conn, parcel, ANATYPE)
            #import cProfile
            #cProfile.run("calcParcel(parcel, storeindex, foodindex, pricematrix, transtotcost, transothercosts, storetransIndex, \
            #    parcelstoretransindex, parcelstoreTransCost, lastresult)")
            #totalprice, foodsetprices, foodsetstores, optimaltransnames = calcParcel(parcel, storeindex, foodindex, pricematrix, transtotcost, transothercosts, storetransIndex, \
            #    parcelstoretransindex, parcelstoreTransCost, lastresult)

            
            #for testing            
            jobs[parcel] = jobserver.submit(calcParcel, (parcel, storeindex, foodindex, pricematrix, transtotcost, transothercosts, storetransIndex, \
                parcelstoretransindex, parcelstoreTransCost, lastresult))
        
        


        #mincost, finallist = calcParcel(parcel, foodcostlist, foodcodes, WORKINGDIRECTORY)

    resultfile = []
    errorfile = []
        
    for parcel in jobs.keys():
#        try:
        #finallist is not used, but avaialble for subset analysis
        try:
            totalprice, foodsetprices, foodsetstores, optimaltransnames = jobs[parcel]()
            pickledfoodsetprices = pickle.dumps(foodsetprices,pickle.HIGHEST_PROTOCOL)
            pickledfoodsetstores = pickle.dumps(foodsetstores,pickle.HIGHEST_PROTOCOL) 
            pickledoptimallist = pickle.dumps(optimaltransnames,pickle.HIGHEST_PROTOCOL)
            #parcel TEXT, totcost REAL, picklestores TEXT, picklefoodcost TEXT, picklefoodstores TEXT
            resultscursor.execute('INSERT INTO results VALUES (?, ?, ?, ?, ?)', (parcel, str(totalprice), sqlite3.Binary(pickledoptimallist), sqlite3.Binary(pickledfoodsetprices), sqlite3.Binary(pickledfoodsetstores))) 
            missingitems = len(foodsetprices) - len(foodsetprices[foodsetprices>0])
            print parcel, "finished with", totalprice, "and", optimaltransnames, "with missing items", missingitems
            #except:
            #    print "hit an error with", parcel
            #    continue
        except:
            print "there was an error with", parcel
            errorfile.append(parcel)
            

    resultsconn.commit()        
        
        
#        fintotcost, costtrans, milesbus, tottime, freqstores = postProcessingValue(conn, finalcostlist, mincost, parcel, analysistype)
#        lastresult = freqstores
            

    
#            
#
#        

    if actualrun != 0:   
        averagetime = ((averagetime *averagecount) + (time.time()- chunkstart))/(averagecount + actualrun)
        averagecount += actualrun
        print "this chunk took", str(time.time() - chunkstart)
        print "you have roughly", str(((numsets*doinsetsof) - averagecount) * averagetime), "seconds left"

    

#resultwritefile = open(WORKINGDIRECTORY + "finalresults.csv",'a')
#for resultline in resultfile:
#    resultwritefile.write(resultline + "\n")

#errorwritefile = open(WORKINGDIRECTORY + "errorfile.csv",'a')
#for errorline in errorfile:
#    errorwritefile.write(errorline + "\n")

print "the folliwng were errors", errorfile

