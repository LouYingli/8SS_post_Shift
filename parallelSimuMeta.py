   # -*- coding: utf-8 -*-
"""
Created on Tue Nov  7 10:50:32 2017

@author: yunyangye
"""

import multiprocessing as mp
import time
import math
import csv
import subprocess
from shutil import copyfile,rmtree
import pandas as pd
import os.path
from bs4 import BeautifulSoup

######################################################
#run models and get the results in parallel
######################################################

######################################################
#run models
######################################################
#climate is the climate zone; weather file name is [climate].epw and baseline model file name is CZ[climate].osm
#param_values is the name of measures, name of arguments and values are used in each case (two-dimension list)
#num_model is the NO. of the model
#round_num is the number of the round times


def modifyIDF(climate,param_name,param_value,order_model):
    f = open('./Model/'+climate+'.idf','rb')
    lines=f.readlines()
    f.close()
    
    f = open('./results/scheduleInformation/'+climate+'schedule.csv','rb')
    schedule=f.readlines()
    f.close()
    
    newlines = []
    modify_lines = []
    modify_id = []
    modify_lines_id = 0
    
    for i in range(len(param_name)):
        # how many 15-min interval need to be changed
        shift = int(float(param_value[0])*60/15)
        
        # get schedule value (96)
        for j in range(len(schedule)):
            if param_name[i] in schedule[j].split(',')[0]:
                ind_schedule = j
                
        # get schedule id in idf file   
        id_start = []
        id_end = []
        for j in range(len(lines)):
             if lines[j].split(',')[0].replace(' ','').lower() == 'schedule:day:interval'and param_name[i] == lines[j+1].split(',')[0].replace(' ',''):
                id_start.append(j+6) #time2 00:30
                id_end.append(j+194) #time96 24:00
        
        # schedule ahead 
        if shift < 0:
            for j in range(0,len(id_start)):
                k=2
                for l in range(id_start[j]+1,id_end[j]+shift*2,2):
                    modify_lines.append(lines[l].replace(schedule[ind_schedule].split(',')[k],schedule[ind_schedule].split(',')[k-shift]))
                    modify_id.append(l)
                    k +=1
                id_endValue = k-shift
                for l in range(id_end[j]+shift*2+1,id_end[j],2):
                    modify_lines.append(lines[l].replace(schedule[ind_schedule].split(',')[k],schedule[ind_schedule].split(',')[id_endValue]))
                    modify_id.append(l)
                    k +=1
        # schedule postpone
        if shift > 0:
            for j in range(0,len(id_start)):
                k=2
                for l in range(id_start[j]+1,id_start[j]+1+shift*2,2):
                    modify_lines.append(lines[l].replace(schedule[ind_schedule].split(',')[k],schedule[ind_schedule].split(',')[2]))
                    modify_id.append(l)
                    k +=1
                for l in range(id_start[j]+1+shift*2,id_end[j],2):
                    modify_lines.append(lines[l].replace(schedule[ind_schedule].split(',')[k],schedule[ind_schedule].split(',')[k-shift]))
                    modify_id.append(l)
                    k +=1 
                    
    for i in range (len(lines)):
        if i in modify_id:
            modify_lines_id = modify_id.index(i)
            newlines.append(modify_lines[modify_lines_id])
        else:
            newlines.append(lines[i])

    f = open('./Model/update_models/'+climate+str(order_model)+'.idf','w')
    for i in range(len(newlines)):
        f.writelines(newlines[i])
    f.close()       
    return str(order_model)+'.idf'     


######################################################
#2.modify IDF file and run model, get model output (site EUI)
#run models and read htm file to get site EUI and source EUI
#save the model input and output into './results/energy_data.csv'
def runModel(climate,eplus_path,weather_file,eplus_file,param_value,output_file,output):
    #run model
    df = subprocess.Popen([eplus_path, "-w",weather_file, "-d",'./results/'+climate+output_file+eplus_file.split('.')[0], "-r", './Model/update_models/'+climate+eplus_file],stdout=subprocess.PIPE)
    output_eplus, err = df.communicate()
    print(output_eplus.decode('utf_8'))
    if not err is None:
        print(err.decode('utf_8'))
        
    if os.path.isfile('./results/'+climate+output_file+eplus_file.split('.')[0]+'/eplustbl.htm'):
         #get model input
        data = []
        data.append(eplus_file.split('.')[0]) #the name of idf file
        data.append(climate) #the name of climate
        data.append(param_value[0])
        
        #get output(site EUI and source EUI)
        path='./results/'+climate+output_file+eplus_file.split('.')[0]+'/eplustbl.htm'
        with open(path) as fp:
            soup = BeautifulSoup(fp)

        energy_table = soup.find_all('table')[0]
        rows = energy_table.find_all('tr')
        total_site_energy_data = rows[1]
        total_source_energy_data = rows[3]
        total_site_energy_per_total_building_area_html = total_site_energy_data.find_all('td')[2]
        total_source_energy_per_total_building_area_html = total_source_energy_data.find_all('td')[2]
        total_site_energy_per_total_building_area = float(total_site_energy_per_total_building_area_html.text)*0.088055066
        total_source_energy_per_total_building_area= float(total_source_energy_per_total_building_area_html.text)*0.088055066
        data.append(total_site_energy_per_total_building_area)
        data.append(total_source_energy_per_total_building_area)
    
        #record the data in the './results/energy_data.csv'
        with open('./results/energy_data.csv', 'ab') as csvfile:
            energy_data = csv.writer(csvfile, delimiter=',')
            energy_data.writerow(data)

    else:
        with open('./results/energy_data_err.csv', 'ab') as csvfile:
            energy_data_err = csv.writer(csvfile, delimiter=',')
            energy_data_err.writerow(climate+eplus_file)
    
    copyfile('./results/'+climate+output_file+eplus_file.split('.')[0]+'/eplustbl.htm','./results/results/'+climate+eplus_file.split('.')[0]+'.htm')    
    rmtree('./results/'+climate+output_file+eplus_file.split('.')[0])
    #rmtree('./Model/update_models/'+climate+eplus_file)
    output.put([])

#################################################################################
#2.modify IDF file and run model, get model output (site EUI)
#run models in parallel for sensitivity analysis
#Climate is the list of climate zone; weather file name is [climate].epw and baseline model file name is CZ[climate].osm
#round_num is the number of the round times
def parallelSimu(climate,round_num):
    #record the start time
    start = time.time()
    #eplus_path ='/usr/EnergyPlus/energyplus-8.7.0'
    eplus_path ='energyplus'
    weather_file ='./Model/'+climate+'.epw'
    output_file = 'temp'
    # get parameter name and parameter value    
    f = open('./variable.csv')
    lines = f.readlines()
    f.close()
    param_name = []
    param_value = []
    for i in range(1,len(lines)):
        param_name.append(lines[i].split(',')[0])
        
    with open('./results/samples/param_values.csv', 'rb') as csvfile:
        data = csv.reader(csvfile, delimiter=',')
        for row in data:
            param_value.append(row)

    # modify the idf file
    order_idf = 1
    for i in range(len(param_value)):
        modifyIDF(climate,param_name,param_value[i],order_idf)
        order_idf += 1
   
    
    # idf file name    
    order_model = 1    
    eplus_files = []
    for i in range(len(param_value)):
        eplus_files.append(str(order_model)+'.idf')
        order_model +=1
    
            
    #multi-processing
    output = mp.Queue()
    processes = [mp.Process(target=runModel,args=(climate,eplus_path,weather_file,eplus_files[i],param_value[i],output_file,output)) for i in range(len(eplus_files))]
    
    #count the number of cpu
    cpu = mp.cpu_count()#record the results including inputs and outputs
    print cpu
    
    model_results = []
    
    run_times = math.floor(len(processes)/cpu)
    if run_times > 0:
        for i in range(int(run_times)):
            for p in processes[i*int(cpu):(i+1)*int(cpu)]:
                p.start()
            
            for p in processes[i*int(cpu):(i+1)*int(cpu)]:
                p.join()
    
            #get the outputs
            temp = [output.get() for p in processes[i*int(cpu):(i+1)*int(cpu)]]
            
            for x in temp:
                model_results.append(x)
    
    for p in processes[int(run_times)*int(cpu):len(processes)]:
        p.start()
            
    for p in processes[int(run_times)*int(cpu):len(processes)]:
        p.join()    
        
    #get the outputs
    temp = [output.get() for p in processes[int(run_times)*int(cpu):len(processes)]]
    for x in temp:
        model_results.append(x)
            
    #record the end time
    end = time.time()
    
    return model_results,end-start