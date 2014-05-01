# -*- coding: utf-8 -*-
"""
Created on Wed Oct 31 09:53:12 2012

@author: hilbert.34
"""


    
def calcParcel(parcel, storeindex, foodindex, pricematrix, transtotcost, transothercosts, storetransIndex, \
                parcelstoretransindex, parcelstoreTransCost, lastresult):
                    
                    
    DEBUG = 0                    
                    
    
    import numpy as np
    from tsp import tspfunction
    from copy import deepcopy
    from random import shuffle
    from random import randint


        
        
        
    #good past this
    
    def getKeyValue(thelist,value):
        return [k for k, v in thelist.iteritems() if v == value][0]
        

    
    def initializeLastResult(lastresult):
        return
    
    def initializeNew(parcelstoreTransCost, parcelstoretransindex,storetransIndex, transtotcost, pricematrix, foodindex, storeindex):
        #first find closest store
        #print DEBUG

        npTransCost = np.array(parcelstoreTransCost).transpose()
        parceltransminindex = np.argmin(npTransCost[0])
        foodsetprices = np.zeros(len(foodindex))
        foodsetstores = []
        for p in range(len(foodsetprices)):
            foodsetstores.append("")
        currentstore = getKeyValue(parcelstoretransindex, parceltransminindex)
        
        #get all food items that are nonzero
        nonzerofooditemsindex = np.squeeze(np.nonzero(pricematrix[storeindex[currentstore]]))
        if (DEBUG):
            print "going to ", currentstore, storeindex[currentstore]
            print nonzerofooditemsindex
            print pricematrix[storeindex[currentstore]]
        #place those food items in the proper indices of the foodset with the store indicies
        for fooditemsindex in nonzerofooditemsindex:
            if (DEBUG > 1):
                print fooditemsindex, storeindex[currentstore], fooditemsindex
            foodsetprices[fooditemsindex] = pricematrix[storeindex[currentstore]][fooditemsindex]
            foodsetstores[fooditemsindex] = currentstore
        if DEBUG > 1:
            print zip(foodsetprices, foodsetstores)
            print storetransIndex
        visitedtransindex = [storetransIndex[currentstore]]
        visitedstorename = [currentstore]
        while (len(foodsetprices[foodsetprices==0]) != 0):
            #get next closest store sture

            sortedtrans = np.argsort(transtotcost[storetransIndex[currentstore]])
            if (DEBUG>1):
                print sortedtrans
            for thetrans in sortedtrans:
                if (thetrans not in visitedtransindex and storetransIndex[currentstore] != thetrans):
                    nextstorename = getKeyValue(storetransIndex, thetrans)
                    break
            visitedtransindex.append(storetransIndex[nextstorename])
            visitedstorename.append(nextstorename)
            if (DEBUG> 1):
                print "have visited", visitedtransindex
            
            for currentprice, index in zip(foodsetprices, range(len(foodsetprices))):
                
                if (currentprice == 0 or (pricematrix[storeindex[nextstorename]][index] < currentprice and pricematrix[storeindex[nextstorename]][index] > 0)):
                    foodsetprices[index] = pricematrix[storeindex[nextstorename]][index]
                    foodsetstores[index] = nextstorename
            currentstore=nextstorename
            
        return foodsetprices, foodsetstores, visitedstorename
        
    def runTSP(visitedstorelist, storetransIndex, transtotcost, parcelstoreTransCost, parcelstoretransindex, parcel):
        while (parcel in visitedstorelist):
            visitedstorelist.remove(parcel)
    
        tspstoreindex = {parcel:0}
        for astore, anindex in zip(visitedstorelist, range(1,len(visitedstorelist)+1)):
            tspstoreindex[astore] = anindex
        
    
        storematrix = {}

        for thestore in visitedstorelist:
            storematrix[tspstoreindex[thestore], tspstoreindex[parcel]] = parcelstoreTransCost[parcelstoretransindex[thestore]][0]
            storematrix[tspstoreindex[parcel], tspstoreindex[thestore]] = parcelstoreTransCost[parcelstoretransindex[thestore]][0]
        
        
        for orig in visitedstorelist:
            for dest in visitedstorelist:
                if orig == dest:
                    continue
                storematrix[tspstoreindex[orig], tspstoreindex[dest]] = transtotcost[storetransIndex[orig]][storetransIndex[dest]]
        optimalset = tspfunction(storematrix, tspstoreindex.values(), DEBUG)
        
        #upon return need to do values to keys
        
        while optimalset[0] != 0:
            tempholder = optimalset.pop(0)
            optimalset.append(tempholder)
        optimalnames = []
        for theindex in optimalset:
            optimalnames.append(getKeyValue(tspstoreindex,theindex))
        
        return optimalnames
            
    

    def floorPrices(foodsetprices,visitedstorelist, pricematrix, foodindex, storeindex):
        #cehck if we have the lowest price for the product 
        # if not exchange
        for foodprice, theindex in zip(foodsetprices, range(len(foodsetprices))):
            for possiblestore in visitedstorelist:
                if (foodprice > pricematrix[storeindex[possiblestore]][theindex] and foodprice != 0 and pricematrix[storeindex[possiblestore]][theindex] != 0):
                    #print "switched one"
                    #print foodprice, "sitched out for", pricematrix[storeindex[possiblestore]][theindex], "at", possiblestore 
                    foodsetprices[theindex] = pricematrix[storeindex[possiblestore]][theindex]
                    foodsetstores[theindex] = possiblestore 
            
        return foodsetprices, foodsetstores
        
    def calcFoodPrices(thefoodpriceset):
        nummissingitems = len(thefoodpriceset) - len(thefoodpriceset[thefoodpriceset>0])
        #incure a 2 dollar penalty for each missing item to find the best suited removal
        foodsetsum = np.sum(thefoodpriceset)
        return foodsetsum + (nummissingitems*30)  
        
        
        
    def getStoretoRemove(optimaltransnames, parcel, transtotcost, storetransIndex, parcelstoreTransCost, \
                parcelstoretransindex, currentfoodsetprices, currentsetstores, storesremoved):
        #this will be in [price savings, price] increase
        possibledropsprice = []
        #print optimaltransnames
        for potdropstore, theindex in zip(optimaltransnames, range(len(optimaltransnames))):
            #calc trans cost savings of dropping a store
            #print theindex, potdropstore
            if (potdropstore.split("-")[0] == "PARCEL"):
                continue
            
            elif (theindex+1 == len(optimaltransnames) ):
                transcostdiff = (transtotcost[storetransIndex[optimaltransnames[theindex-1]]][storetransIndex[potdropstore]] + \
                                parcelstoreTransCost[parcelstoretransindex[optimaltransnames[theindex]]][0]) - \
                                parcelstoreTransCost[parcelstoretransindex[optimaltransnames[theindex-1]]][0]
            
            elif (theindex == 1):
                transcostdiff = (transtotcost[storetransIndex[optimaltransnames[theindex+1]]][storetransIndex[potdropstore]] + \
                                parcelstoreTransCost[parcelstoretransindex[optimaltransnames[theindex]]][0]) - \
                                parcelstoreTransCost[parcelstoretransindex[optimaltransnames[theindex+1]]][0]
            else:
                transcostdiff = (transtotcost[storetransIndex[optimaltransnames[theindex-1]]][storetransIndex[potdropstore]] + \
                                transtotcost[storetransIndex[potdropstore]][storetransIndex[optimaltransnames[theindex+1]]]) - \
                                transtotcost[storetransIndex[optimaltransnames[theindex-1]]][storetransIndex[optimaltransnames[theindex+1]]] 
            
            #calc the price increase for dropping a store
                #set the food items of the removed store as 0 
                #send to floorPrices
                #check to make sure this is a feasible solution                                            
                                
            
            potfoodsetprices = deepcopy(currentfoodsetprices)
            potcurrentsetstores = deepcopy(currentsetstores)
            potvisitedstores = deepcopy(optimaltransnames)
            
            potvisitedstores.remove(potdropstore)
            if parcel in potvisitedstores:
                potvisitedstores.remove(parcel)
            
            for potindex in range(len(potfoodsetprices)):
                if (potcurrentsetstores[potindex] == potdropstore):
                    potfoodsetprices[potindex] = 0
                    potcurrentsetstores[potindex] = 0
                    
            potfoodsetprices, potcurrentsetstores = floorPrices(potfoodsetprices,potvisitedstores, pricematrix, foodindex, storeindex)
            
            potfoodsetprices = np.array(potfoodsetprices)
            
            priceincrease = calcFoodPrices(potfoodsetprices) - calcFoodPrices(currentfoodsetprices)

            possibledropsprice.append([priceincrease - transcostdiff, [potdropstore, potfoodsetprices, potcurrentsetstores, potvisitedstores]])
        #print possibledropsprice
        sorted(possibledropsprice, key=lambda a_entry: a_entry[0], reverse=True)
        #possibledropsprice.sort(reverse=True)
        storetoremove = None
        for tempdataset in possibledropsprice:
            if (tempdataset[1][0] not in storesremoved):
                storetoremove = tempdataset[1][0]
                potfoodsetprices = tempdataset[1][1]
                potcurrentsetstores = tempdataset[1][2]
                potvisitedstores = tempdataset[1][3]
                break        
        if (storetoremove == None):
            if (DEBUG>1):
                print "removed nothing do one last insert then quit"
            randindex = randint(0,len(possibledropsprice)-1)
            
            return possibledropsprice[randindex][1][0], possibledropsprice[randindex][1][1], possibledropsprice[randindex][1][2],possibledropsprice[randindex][1][3], True
        else :
            return storetoremove, potfoodsetprices, potcurrentsetstores,potvisitedstores, False
        
    def getTotalTransCost(optimaltransnames, transtotcost, storetransIndex, \
        parcelstoreTransCost, parcelstoretransindex,\
        parcel):
        
        totalcost = 0
        if parcel in optimaltransnames:
            while (parcel in optimaltransnames):
                optimaltransnames.remove(parcel)
            totalcost += parcelstoreTransCost[parcelstoretransindex[optimaltransnames[0]]][0]
            totalcost += parcelstoreTransCost[parcelstoretransindex[optimaltransnames[-1]]][0]
        else:
            totalcost += parcelstoreTransCost[parcelstoretransindex[optimaltransnames[0]]][0]
            totalcost += parcelstoreTransCost[parcelstoretransindex[optimaltransnames[-1]]][0]            

        
        for potdropstore, theindex in zip(optimaltransnames, range(len(optimaltransnames))):
            #calc trans cost savings of dropping a store
            #print theindex, potdropstore
#            if (potdropstore.split("-")[0] == "PARCEL"):
#                totalcost += parcelstoreTransCost[parcelstoretransindex[optimaltransnames[theindex+1]]][0]
#            
            if (theindex+1 == len(optimaltransnames) ):
                break
                                
            else:
                totalcost += transtotcost[storetransIndex[optimaltransnames[theindex]]][storetransIndex[optimaltransnames[theindex+1]]] 
        #print "the total cost is", totalcost
        return totalcost
             
    
        
    def insertStores(newstorenameslist, parcel, transtotcost, storetransIndex, parcelstoreTransCost, \
        parcelstoretransindex, newfoodsetprices, newsetstores, tabustoreset, storetoremove, temptranscost):
        

        
        #find the 15 closes stores to the removed store that is not in the feasible solution and not in storetoremove
        #maybe this should be randomized?
        storecandidates = np.argsort(transtotcost[storetransIndex[storetoremove]])
        finalstorecansnames = []
        counter = 0
        MAXSTORES = 30
        for storecandidate in storecandidates:
            tempstorecandidatename = getKeyValue(storetransIndex,storecandidate)
            if tempstorecandidatename in newstorenameslist or storetoremove == tempstorecandidatename:
                continue
            else:
                finalstorecansnames.append(tempstorecandidatename)
                counter +=1
                if counter == MAXSTORES:
                    break
        shuffle(finalstorecansnames)
        
            
                
        
        lasttranscost = temptranscost
        lastfoodcost = calcFoodPrices(newfoodsetprices)
        
        
        for storecandidatename in finalstorecansnames:
            tempfeasiblestorelist = deepcopy(newstorenameslist)
            tempfeasiblestorelist.append(storecandidatename)
            sortedoptimaltransnames = deepcopy(tempfeasiblestorelist)
            sortedoptimaltransnames.sort()
            if (sortedoptimaltransnames in tabustoreset):
                continue
            #print tempfeasiblestorelist
            tempoptimal = runTSP(tempfeasiblestorelist, storetransIndex, transtotcost, parcelstoreTransCost, parcelstoretransindex, parcel)
            #print tempoptimal
            temptranscost = getTotalTransCost(tempoptimal, transtotcost, storetransIndex, \
                    parcelstoreTransCost, parcelstoretransindex,\
                    parcel)
            
            #now calculate the floored prices
            tempfoodsetprices, tempfoodsetstores = floorPrices(foodsetprices,visitedstorelist, pricematrix, foodindex, storeindex)
            tempfoodcost = calcFoodPrices(tempfoodsetprices)
            temptotdifference = temptranscost - lasttranscost + tempfoodcost - lastfoodcost 
            #print "the difference is", temptotdifference, "adding a store", storecandidatename
            
            if temptotdifference < 0:
                
                lasttranscost = temptranscost
                lastfoodcost=tempfoodcost
                newstorenameslist = tempoptimal
                newfoodsetprices = tempfoodsetprices
                newsetstores = tempfoodsetstores
        
        #return feasible solution
        return newfoodsetprices, newsetstores, newstorenameslist
        

                   
                    

            
        

    
    def consecutiveExchange(transtotcost, storetransIndex, \
        storeindex, foodindex, pricematrix, \
        optimaltransnames,\
        foodsetprices, foodsetstores, \
        parcelstoreTransCost, parcelstoretransindex,\
        parcel):
            
        currentfoodsetprices = deepcopy(foodsetprices)
        currentsetstores = deepcopy(foodsetstores)
        
        #this will be in a [storeset, totalcost, changed price]
        sortedoptimaltransnames = deepcopy(optimaltransnames)
        sortedoptimaltransnames.sort()
        tabustoreset = [sortedoptimaltransnames]
        temptranscost = getTotalTransCost(optimaltransnames, transtotcost, storetransIndex, \
                parcelstoreTransCost, parcelstoretransindex,\
                parcel)
        temptotalcost = calcFoodPrices(foodsetprices) +  temptranscost
        print "the initial cost", temptotalcost
        tabutotcost = [temptotalcost]
        
        lasttotalcost = temptotalcost

        storesremoved = []        
        
        thecounter = 0
        killit = False
        while (thecounter < 500 and not killit):
       
        
            storetoremove, newfoodsetprices, newsetstores, newstorenameslist, killit = getStoretoRemove(optimaltransnames, parcel, transtotcost, storetransIndex, parcelstoreTransCost, \
                    parcelstoretransindex, currentfoodsetprices, currentsetstores, storesremoved)
            storesremoved.append(storetoremove)
                    
            newfoodsetprices, newsetstores, newstorenameslist = insertStores(newstorenameslist, parcel, transtotcost, storetransIndex, parcelstoreTransCost, \
                    parcelstoretransindex, newfoodsetprices, newsetstores, tabustoreset, storetoremove, temptranscost)
            sortedoptimaltransnames = deepcopy(newstorenameslist)
            sortedoptimaltransnames.sort()
            tabustoreset.append(sortedoptimaltransnames)
            
            temptranscost = getTotalTransCost(newstorenameslist, transtotcost, storetransIndex, \
                    parcelstoreTransCost, parcelstoretransindex,\
                    parcel)
            temptotalcost = calcFoodPrices(newfoodsetprices) +  temptranscost
            tabutotcost.append(temptotalcost)
            #print newstorenameslist
            #print temptotalcost
            if (temptotalcost < lasttotalcost):
                #print "updating the set from", lasttotalcost, "to", temptotalcost
                lasttotalcost = temptotalcost
                currentsetstores = newsetstores
                currentfoodsetprices = newfoodsetprices
                optimaltransnames = newstorenameslist
                
            thecounter +=1
            
        return lasttotalcost, currentfoodsetprices, currentsetstores, optimaltransnames
        
        


    
    # the arguments you can work with
    #parcel, 
    #storeindex, foodindex, pricematrix, 
    #transtotcost, transothercosts, storetransIndex,
    #parcelstoretransindex, parcelstoreTransCost, 
    #lastresult
    

    
#    
#    if lastresult:
#        #lastresult = [foodsetprices, foodsetstores, optimaltransnames]
#        foodsetprices = lastresult[0]
#        foodsetstores = lastresult[1]
#        visitedstorelist = lastresult[2]
#    else:

    foodsetprices, foodsetstores, visitedstorelist = initializeNew(parcelstoreTransCost, parcelstoretransindex,storetransIndex, \
        transtotcost, pricematrix, foodindex, storeindex)
    

    optimaltransnames = runTSP(visitedstorelist, storetransIndex, transtotcost, parcelstoreTransCost, parcelstoretransindex, parcel)
        
    foodsetprices, foodsetstores = floorPrices(foodsetprices, visitedstorelist, pricematrix, foodindex, storeindex)
    
    totalprice, foodsetprices, foodsetstores, optimaltransnames = consecutiveExchange(transtotcost, storetransIndex, \
        storeindex, foodindex, pricematrix, \
        optimaltransnames,\
        foodsetprices, foodsetstores,\
        parcelstoreTransCost, parcelstoretransindex,\
        parcel)

        
    return totalprice, foodsetprices, foodsetstores, optimaltransnames
        
    
