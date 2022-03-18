from mailmerge import MailMerge
import pandas as pd
from datetime import date
import os
import shutil
import glob
import numpy as np
from colored import fg


def proc_MOP(template):


  '''
  The function is used to process the MOP with the spesific template, based on the SOW 
  '''


  #To load the template
  document = MailMerge(base_temp+'/'+str(template[0])+".docx") #filterTemplate[0] -> The list is already unique, to call the first index of numpy array (so it can convert to text value) 

  today = date.today() #Today's date written on the first page
  title = str(nameMOP) #MOP Title
  num_impact = len(filterTable.index) #The number of DUID list
   
  #Parsing process with dictionary for creating table
  tableRows = []
  j=0

  while j < num_impact:
      
    region_name = filterTable['NE Region'].iloc[j] #To exctract the spesific region
    exec_date = filterTable['Execution Date'].iloc[j] #To extract the spesific date
    exec_time = filterTable['Time'].iloc[j] #To extract the spesific time
      
    filterDUID = filterTable['Relative NE '].iloc[j] #Parsing each DUID
    filterQty = filterTable['Dependency Qty'].iloc[j] #Parsing each qty
    filterDependency = filterTable['Site Dependency'].iloc[j] #Parsing the dependency list
    filterDataSource = filterTable['Impact Data Source'].iloc[j] #Parsing data source

    #Merging list of 'tableRows' with the dictionary from each parsed item
    tableRows.append({'duid' : str(filterDUID), 
                      'qty' : str(filterQty), 
                      'list' : str(filterDependency), 
                      'source' : str(filterDataSource)})

    j +=  1

  #To merge the table  
  document.merge_rows('duid',tableRows)

  document.merge(predate = str(today.strftime("%B %d, %Y")), 
                   titlemop = title,
                   linknum = str(num_impact),
                   region = str(region_name),
                   date = str(exec_date.strftime("%d %B %Y")),
                   time = str(exec_time),        
                   duid = tableRows)

  #Export to output folder
  document.write((base_out+'/{0}.docx' .format(title)))  


def proc_DEP(name):

    '''
    The function is used to create the .xlsx for the impacted sites

    '''

    db = data[["Relative NE ", "Site Dependency", 'MOP File Name']]

    filMOP = db[db['MOP File Name'] == str(name)][["Relative NE ", "Site Dependency", 'MOP File Name']]
    filMOP.rename({"Site Dependency" : "Site Id"}, axis = 1, inplace = True) #Rename the column name "Site dependancy" into "Site Id"
    filMOP["Site Id"] = filMOP["Site Id"].astype("str") #Need to convert into string data type, to fix the bugs
    filMOP["Site Id"] = filMOP["Site Id"].str.split(",") #Seperate values from commas
    filMOP = filMOP["Site Id"].explode()
    filMOP = filMOP.reset_index(drop = True) #To reset index
    filMOP = pd.DataFrame(filMOP) #Convert from Series to Dataframe
    filMOP = filMOP[filMOP["Site Id"] != "-"] #Remove the value "-"

    filMOP.insert(1, "NE Name", '') #Insert blank name entitled "NE Name" after column "Site Id"
      
    filMOP.to_excel(base_out+'/{}.xlsx'.format(name), sheet_name = "Site Impact", index = False)


def CreateFolder(name):

    '''
    Create the folder
    '''

    newfolder = base_out+"/{0}/{1}/".format(str(filterRegion[0]),str(filterSOW[0]))
    files_mop = base_out+'/{}.docx'.format(name)
    files_dep = base_out+'/{}.xlsx'.format(name)

    try:
      os.makedirs(newfolder) #Creating folder /Output/[Region]/[SOW]
      shutil.move(files_mop, newfolder) #Move MOP .docx
      shutil.move(files_dep, newfolder) #Move dependency site .xlsx

    except FileExistsError: #Exception if the folder already exists. No need to create new folder
      shutil.move(files_mop, newfolder)
      shutil.move(files_dep, newfolder)



'''
EXECUTION PART {THE PROGRAM STARTS HERE}
'''

#Template folder
base_temp = os.path.basename("Template")

#Output folder
base_out = os.path.basename("Output")

#Load data
data = pd.read_excel('db.xlsx',parse_dates = True)

#Template folder
base_temp = os.path.basename("Template")

#Output folder
base_out = os.path.basename("Output")

#Colouring
tcolor = fg("green") 
fcolor = fg("red")
dcolor = fg("white")


#To return the list of MOP file name
filterMOP = data["MOP File Name"].unique()

for nameMOP in filterMOP:

  #Select the column
  filterTable = data[data["MOP File Name"] == str(nameMOP)][['Relative NE ','Scope', 'NE Region','Time', 'Execution Date', 'Dependency Qty', 'Site Dependency', 'Impact Data Source', 'Template']]
  
  #Filter based on region for creating folder
  filterRegion = filterTable['NE Region'].unique()

  #Filter based on date for creating folder
  filterDate = filterTable['Execution Date'].unique()

  #Filter based on the scope
  filterSOW = filterTable['Scope'].unique()

  #Filter based on the template
  filterTemplate = filterTable['Template'].unique()


  proc_MOP(filterTemplate)
  proc_DEP(nameMOP)
  CreateFolder(nameMOP)
  print(tcolor+str(nameMOP)+" generated")
  print(dcolor+"")


  