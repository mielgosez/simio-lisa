# -*- coding: utf-8 -*-
"""
Created on Tue Sep 14 15:10:45 2021

@author: alessandro.seri
"""

import pandas as pd
import numpy as np
import datetime
import matplotlib.pyplot as plt
import runpy
import os
import plotly.express as px
from plotly.offline import plot
import time
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
path = r"C:\Users\alessandro.seri\Accenture\MARS Retort MVP - AI - General\02_Data\03_output_data\01_raw_data\scenarios\MicroStops_0"
paths_to_file = [os.path.normpath(path + "/OutputStatus5A.csv"), os.path.normpath(path + "/OutputStatus5B.csv"), os.path.normpath(path + "/OutputStatus6.csv")]
time_axis = 'StatusDate'
y = 'Count'
if type(paths_to_file) is str:
      input_data = pd.read_csv(paths_to_file)
      input_data['source'] = paths_to_file.split(os.sep)[-1]
else:
    input_data=pd.DataFrame()
    for p in paths_to_file:
        aux = pd.read_csv(p)
        aux['source'] = p.split(os.sep)[-1]
        input_data = input_data.append(aux, ignore_index=True)

input_data[time_axis] = pd.to_datetime(input_data[time_axis])
input_data['new'] = input_data[y]+1

# data = pd.read_csv(p)
fig = px.line(input_data, x=time_axis, y=[y, 'new'])
plot(fig)
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
paths_to_file = os.path.normpath(path + "/OutputObjectUtilization.csv")
y = 'Utilization'
x = 'ObjectId'
time_axis = 'DateTime'
object_groups_dict = {
    'Shuttles': ['DropOffShuttle[1]', 'PickUpShuttle[1]'],                  
    'Retorts': ['Retort1', 'Retort2','Retort3', 'Retort4',
                'Retort5', 'Retort6', 'Retort7', 'Retort8',
                'Retort9', 'Retort10']
    }

if type(paths_to_file) is str:
      input_data = pd.read_csv(paths_to_file)
      input_data['source'] = paths_to_file.split(os.sep)[-1]
else:
    input_data=pd.DataFrame()
    for p in paths_to_file:
        aux = pd.read_csv(p)
        aux['source'] = p.split(os.sep)[-1]
        input_data = input_data.append(aux, ignore_index=True)

for k in object_groups_dict.keys():
    input_data_plt = input_data[input_data[x].isin(object_groups_dict[k])]
    
    # Plot Bars Time
    fig3 = px.bar(input_data_plt, x=x, y=y, barmode="group", facet_col="DateTime")
    fig3.show()
    plot(fig3)
    time.sleep(1)


    input_data_plt = input_data_plt.groupby(by = x, as_index=False).mean()
    
    # Plot Pie
    fig1 = px.pie(input_data_plt, values = y, names = x, title = x + ' utilization quantified in terms of ' + y + ', group '+ k)
    fig1.show()
    plot(fig1)
    time.sleep(1) # Sleep

    # Plot Bars
    fig2 = px.bar(input_data_plt, x=x, y=y, barmode="group")
    fig2.show()
    plot(fig2)
    time.sleep(1) # Sleep

 # Sleep
                 #, facet_row="time", facet_col="day",
       # category_or#ders={"day": ["Thur", "Fri", "Sat", "Sun"], "time": ["Lunch", "Dinner"]})
