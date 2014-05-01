# -*- coding: utf-8 -*-
"""
Created on Wed Feb 08 15:55:06 2012

@author: hilbert.34
"""

import sqlite3
from dbfpy import dbf

WORKINGDIRECTORY = "D:/GIS Project Data/Food Optimization/Nov14-walking/basefiles/"

analysistype = "walking"
#analysistype = "publictrans"




conn = sqlite3.connect(WORKINGDIRECTORY + "parcelstoretrans_" + analysistype + ".txt")





c = conn.cursor()
try:
    if (analysistype == "driving"):
        c.execute("""CREATE TABLE transcosts (orig TEXT, dest TEXT, totcost REAL, travelcost REAL, timecost REAL)""")
    else:
        c.execute("""CREATE TABLE transcosts (orig TEXT, dest TEXT, totcost REAL, totbus REAL, tottime REAL)""")
    conn.commit()
except:
    print "table already exists continuing"

reader = dbf.Dbf(WORKINGDIRECTORY + "parcel_store_" + analysistype + ".dbf")
        
 

iteration = 0
  
for row in reader:

    thesplit = row[1].split(" - ")

    if (analysistype == "driving"):
        queryvars = {"origin":thesplit[0],"dest":thesplit[1],"totcost":row[5],"travelcost":row[6],"timecost":row[7]}
    else:
        queryvars = {"origin":thesplit[0],"dest":thesplit[1],"totcost":row[5],"totbus":row[6],"tottime":row[7]}
    #print "looking at", thesplit[0], "and", thesplit[1]
    if (analysistype == "driving"):
        c.execute("""INSERT INTO transcosts VALUES ("%(origin)s", "%(dest)s", %(totcost)s, %(travelcost)s, %(timecost)s)"""%queryvars)
    else:
        c.execute("""INSERT INTO transcosts VALUES ("%(origin)s", "%(dest)s", %(totcost)s, %(totbus)s, %(tottime)s)"""%queryvars)
    iteration += 1
    if (iteration%10000 == 0):
        conn.commit()
    
    if (iteration%10000 == 0):
        print "doing iteration ", str(iteration/10000)
        
conn.commit()
            
    