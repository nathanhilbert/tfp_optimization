# -*- coding: utf-8 -*-
"""
Created on Wed Nov 14 09:45:33 2012

@author: hilbert.34
"""

import csv
import numpy as np
from random import random

INPUTDIR = 'C:/Users/hilbert.34/Dropbox/GIS_shared/FoodandStores_final/'



with open(INPUTDIR + 'FoodPrices_intput_random-NLH.csv', 'rb') as f:
    reader = csv.reader(f)
    row = reader.next()
    headerindex = {}
    headerset = []
    foodset = []
    dataset = []
    for items, index in zip(row, range(len(row))):
        headerindex[items] = index
        headerset.append(items)
        dataset.append([])
        if (index > 6):
            foodset.append(items)
            
    #go through each store
    for row in reader:
        for item,index in zip(row, range(len(row))):
            dataset[index].append(item)

dataset = np.array(dataset)
storedataset = dataset.transpose()



            
outputset = []

for storesetrow in storedataset:
    print "currently doing", storesetrow[headerindex['store_name']]
    if (str(storesetrow[headerindex['surveyed']]) == "1"):
        outputset.append(storesetrow)
    else:
        tempout = []
        storetype = storesetrow[headerindex['storetype']]
        for storeitems, index in zip(storesetrow, range(len(storesetrow))):
            if (index < 7):
                tempout.append(storeitems)
            else:
                storesetarray = dataset[headerindex['storetype']]
                storeargs = np.argwhere((dataset[headerindex['storetype']] ==storetype) & (dataset[headerindex['surveyed']] == '1')).flatten()
                pricearray = dataset[index][storeargs].astype(float)
                
                changezero = float(len(pricearray[pricearray>0]))/float(len(pricearray))  
                if random() > changezero:
                    tempout.append(0)
                else:
                    if (np.max(pricearray[pricearray>0]) == np.min(pricearray[pricearray>0])):
                        pricediff = np.min(pricearray[pricearray>0])/2
                    else :
                        pricediff = np.max(pricearray[pricearray>0]) - np.min(pricearray[pricearray>0])
                    itemprice = pricediff * random() + np.min(pricearray[pricearray>0])
                    tempout.append(itemprice)
        outputset.append(tempout)

                #print dataset[index][[dataset[headerindex['storetype']][dataset[headerindex['storetype']] == storetype]]]
                #get percentage of items for this type of store
                    #if passes then give price else give zero
                    
                    

with open(INPUTDIR + 'FoodPrices_output_random-NLH.csv', 'wb') as f:
    writer = csv.writer(f)

            
    writer.writerow(headerset)
    for outrow in outputset:
        writer.writerow(outrow)

            
            
            




#put all data into a matrix

#calc the min and max for each store item

#calc random for that item 

#output to csv