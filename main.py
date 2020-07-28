# -*- coding: utf-8 -*-
"""
Created on Sun Jun  3 22:45:50 2018

@author: yunyangye
"""
import os
import csv
import numpy as np
from shutil import rmtree
#0.change the idf file to 15 minute format
#1.sampleing: get different value of model input (LHM)
#2.modify IDF file and run model, get model output (site EUI)

###############################################################################
     

pathway = os.getcwd()
###############################################################################
# list all the inputs which can be modify 
# define the climate zones that need to be considered
climate = ['1A','2A','2B','3A','3B','3C','4A','4B','4C','5A','5B','6A','6B','7A','8A']# define the needed climate zones
# schedule information(15 min intervel) exclude design day schedule

# number of samples for training and testing meta-models
#number of samples in each climate zone = num_sample * number of sensitive model inputs
num_sample = 3
# parameters' library
# list the entire sets of some inputs
climate_lib = ['1A','2A','2B','3A','3B','3C','4A','4B','4C','5A','5B','6A','6B','7A','8A']

###############################################################################
# 0.change the idf file to 15 minute format
#os.chdir(os.path.join(pathway,'sourceFolder'))
import scheduleChange as schedule
#os.chdir(pathway)

## 0.1.get schedule information(15 min intervel) exclude design day schedule
for cz in climate:
    schedule.schedule ('./sourceFolder/'+cz+'.idf',cz)
## 0.2.change the schedule to 15min interval    
for cz in climate:
    schedule.modify('./sourceFolder/'+cz+'.idf','./results/scheduleInformation/'+cz+'schedule.csv',cz)


######################################################################################
#1.sampleing: get different value of model input (LHM)
#os.chdir(os.path.join(pathway,'Meta'))
import sampleMeta as samp
#os.chdir(pathway)

for cz in climate:
    data_set,param_values = samp.sampleMeta(num_sample,cz) 
    # data_set contains variables name, min value, max value in climate zone cz
    #param_values is the sample which contain the vaiables' value
    
    ## record the data in the folder './results/samples'
    ## store the information of data_set
    with open('./results/samples/data_set.csv', 'wb') as csvfile:
        for row in data_set:
            data = csv.writer(csvfile, delimiter=',')
            data.writerow(row)
    
    ## store the information of param_values
    with open('./results/samples/param_values.csv', 'wb') as csvfile:
        for row in param_values:
            data = csv.writer(csvfile, delimiter=',')
            data.writerow(row)
          
###################################################################################
#2.modify IDF file and run model, get model output (site EUI)s
###model inputs and outputs are saved in './results/energy_data.csv'
#os.chdir(os.path.join(pathway,'runModel'))
import parallelSimuMeta as ps
#os.chdir(pathway)
for cz in climate:
    model_results,run_time = ps.parallelSimu(cz,1)
#rmtree('./Model/update_models')
print run_time

