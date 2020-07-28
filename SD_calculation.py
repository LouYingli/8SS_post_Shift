# -*- coding: utf-8 -*-
"""
Created on Sun Jan  5 16:33:10 2020

@author: yunyangye
"""
# importing the statistics module 
import numpy as np
import csv

climate = ['1A','2A','2B','3A','3B','3C','4A','4B','4C','5A','5B','6A','6B','7A','8A']

## get information of energy
temp_energy = []
with open('./results/energy_data.csv', 'rb') as csvfile:
    data = csv.reader(csvfile, delimiter=',')
    for row in data:
        temp_energy.append(row)

energy = [] # climate and site EUI
for row in temp_energy:
    temp = []
    temp.append(row[1])#climate
    temp.append(float(row[-2]))#site EUI
    energy.append(temp)
SD = [] # standard deviation 
for cz in climate:
    energy_cz = []
    for row in energy:
        if row[0] == cz:
            energy_cz.append(row[1])
    temp = []
    temp.append(cz)
    temp.append(np.std(energy_cz))
    SD.append(temp)

with open('./energy_data_SD_shift.csv', 'w') as csvfile:
        for row in SD:
            SD = csv.writer(csvfile, delimiter=',')
            SD.writerow(row)