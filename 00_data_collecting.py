#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Apr 26 18:00:37 2020

@author: kevinossner
"""
#load libraries
import pandas as pd
import os
import zipfile
import sqlite3
import glob
import shutil

cmd = 'python apple_health_data_parser.py Data/apple_health_export/Export.xml'
os.system(cmd)

#unzip files
with zipfile.ZipFile('./Data/Exports/MFP_Export.zip', 'r') as zipObj:
    listOfFileNames = zipObj.namelist()
    for fileName in listOfFileNames:
        if fileName.startswith('Nutrition'):
            zipObj.extract(fileName, './Data')
            
# load data
workout = pd.read_csv('./Data/apple_health_export/Workout.csv')
activeEnergy = pd.read_csv('./Data/apple_health_export/ActiveEnergyBurned.csv')
restEnergy = pd.read_csv('./Data/apple_health_export/BasalEnergyBurned.csv')
weight = pd.read_csv('./Data/apple_health_export/BodyMass.csv')
standing = pd.read_csv('./Data/apple_health_export/AppleStandTime.csv')
heartRate = pd.read_csv('./Data/apple_health_export/HeartRate.csv')
restingHeartRate = pd.read_csv(
    './Data/apple_health_export/RestingHeartRate.csv')
steps = pd.read_csv('./Data/Exports/activity-export.csv', sep=';')
steps.columns = steps.columns.str.split(' ').str[0]
files = os.listdir('./Data')
for fileName in files:
    if fileName.startswith('Nutrition'):
        filePath = './Data/'+fileName
        nutrition = pd.read_csv(filePath, parse_dates=[2])
        
# store data in sqlite
conn = sqlite3.connect('./Data/Health.db')
activeEnergy.to_sql('ActiveEnergy', conn, index=False, if_exists='replace')
restEnergy.to_sql('RestEnergy', conn, index=False, if_exists='replace')
workout.to_sql('Workout', conn, index=False, if_exists='replace')
weight.to_sql('Bodyweight', conn, index=False, if_exists='replace')
steps.to_sql('Steps', conn, index=False, if_exists='replace')
standing.to_sql('Standing', conn, index=False, if_exists='replace')
heartRate.to_sql('HeartRate', conn, index=False, if_exists='replace')
restingHeartRate.to_sql('RestingHeartRate', conn, index=False,
                        if_exists='replace')
nutrition.to_sql('Nutrition', conn, index=False, if_exists='replace')
print()
print('Tables successfully stored in "./Data/Health.db"')

# only keep necessary files
fileList = glob.glob('./Data/*.*')
for filePath in fileList:
    if filePath.endswith('.csv'):
        try:
            os.remove(filePath)
        except:
            print("Error while deleting file : ", filePath)

shutil.rmtree('./Data/apple_health_export')