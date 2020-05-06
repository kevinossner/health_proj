#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 27 06:14:38 2020

@author: kevinossner
"""

#
import pandas as pd
import numpy as np
from datetime import datetime
import sqlite3


# process calories burned data
def transform_BurnedEnergy(Rest_df, Active_df):
    '''
    INPUT
    ----------
    Rest_df : dataframe with resting burned calories from apple health.
    Active_df : dataframe with active burned calories from apple health.

    OUTPUT
    -------
    Combined and cleaned dataframe.
    '''
    Rest_df['date'] = pd.to_datetime(Rest_df['startDate']).dt.date
    Rest_df['startTime'] = pd.to_datetime(Rest_df['startDate']).dt.time
    Rest_df['endTime'] = pd.to_datetime(Rest_df['endDate']).dt.time
    Rest_df.drop(['type', 'endDate', 'startDate', 'sourceVersion', 'device',
                  'creationDate'], axis = 1, inplace=True)
    Rest_df['type'] = 'Resting'
    
    Active_df = Active_df.loc[Active_df['sourceName']==
                              'Apple\xa0Watch von Kevin'].copy()
    Active_df['date'] = pd.to_datetime(Active_df['startDate']).dt.date
    Active_df['startTime'] = pd.to_datetime(Active_df['startDate']).dt.time
    Active_df['endTime'] = pd.to_datetime(Active_df['endDate']).dt.time
    Active_df.drop(['type', 'endDate', 'startDate', 'sourceVersion', 'device',
                    'creationDate'], axis = 1, inplace=True)
    Active_df['type'] = 'active'
    return Rest_df.append(Active_df, ignore_index=True).sort_values(by='date')

# process workout data
def transform_workout(df):
    '''
    INPUT
    ----------
    df : dataframe with recorded workouts from apple health.

    OUTPUT
    -------
    Cleaned dataframe with missing values on days without a workout.
    '''
    df['date'] = pd.to_datetime(df['startDate']).dt.date
    df['startTime'] = pd.to_datetime(df['startDate']).dt.time
    df['endTime'] = pd.to_datetime(df['endDate']).dt.time
    df['workoutActivityType'] = df['workoutActivityType'].str \
                                    .split('Type' ,expand=True)[1]
    df.drop(['startDate', 'endDate', 'sourceVersion', 'device',
                    'creationDate'], axis = 1, inplace=True)
    date_today = datetime.now()
    dates = pd.DataFrame(pd.date_range('2019-08-01', date_today,
                                       freq='D'))
    dates['date'] = pd.to_datetime(dates[0]).dt.date
    dates.drop(0, axis=1, inplace=True)    
    return dates.merge(df, how='left', on=['date'])

# process bodyweight data
def transform_weight(df):
    '''
    INPUT
    ----------
    df : dataframe with bodyweight measurements from apple health.

    OUTPUT
    -------
    Cleaned dataframe with missing values on days without a measurement.
    '''
    df['date'] = pd.to_datetime(df['startDate']).dt.date
    df['time'] = pd.to_datetime(df['startDate']).dt.time
    df = df.loc[df['sourceName']=='Health'].copy()
    df.rename(columns={'value': 'bodyweight'}, inplace=True)
    df.drop(['startDate', 'endDate', 'sourceVersion', 'device', 'creationDate',
             'type'], axis = 1, inplace=True)
    date_today = datetime.now()
    dates = pd.DataFrame(pd.date_range('2019-08-01', date_today,
                                       freq='D'))
    dates['date'] = pd.to_datetime(dates[0]).dt.date
    dates.drop(0, axis=1, inplace=True)
    return dates.merge(df, how='left', on=['date'])
    
# process activity data
def transform_activity(standing_df, steps_df):
    '''
    INPUT
    ----------
    standing_df : dataframe with standing minutes from apple health.
    steps_df : dataframe with counted steps from StepsApp.

    OUTPUT
    -------
    Cleaned and combined dataframe with missing values where nothing recorded.
    '''
    standing_df['date'] = pd.to_datetime(standing_df['startDate']).dt.date
    standing_df['hour'] = pd.to_datetime(standing_df['startDate']).dt.hour
    standing_df = (standing_df[['value', 'hour','date']]
                   .groupby(['date', 'hour'], as_index=False)).sum()
    standing_df.rename(columns={'value': 'standing'}, inplace=True)
    steps_df['hour'] = pd.to_datetime(steps_df['date']).dt.hour
    steps_df['date'] = pd.to_datetime(steps_df['date']).dt.date
    steps_df.drop(['duration', 'distance', 'calories'], axis=1, inplace=True)
    activity = standing_df.merge(steps_df, how='outer', on=['date', 'hour'])
    date_today = datetime.now()
    dates = pd.DataFrame(pd.date_range('2019-08-01 00:00:00', date_today,
                                       freq='H'))
    dates['date'] = pd.to_datetime(dates[0]).dt.date
    dates['hour'] = pd.to_datetime(dates[0]).dt.hour
    dates.drop(0, axis=1, inplace=True)
    return dates.merge(activity, how='left', on=['date', 'hour'])

# process health data
def transform_health(hr_df, rest_hr_df):
    '''
    INPUT
    ----------
    hr_df : dataframe with current heart rate recorded from apple health.
    rest_hr_df : dataframe with resting heart rate from apple health.

    OUTPUTs
    -------
    Cleaned and combined dataframe.

    '''
    hr_df['date'] = pd.to_datetime(hr_df['startDate']).dt.date
    hr_df['time'] = pd.to_datetime(hr_df['startDate']).dt.time
    hr_df.drop(['sourceVersion', 'device', 'type', 'creationDate', 'startDate',
                'endDate'], axis=1, inplace=True)
    hr_df.rename(columns={'value': 'heartRate'}, inplace=True)
    rest_hr_df['date'] = pd.to_datetime(rest_hr_df['startDate']).dt.date
    rest_hr_df.rename(columns={'value': 'restingHeartRate'}, inplace=True)
    rest_hr_df.drop(['sourceName', 'sourceVersion', 'device', 'type', 'unit',
                     'creationDate', 'startDate', 'endDate'],
                    axis=1, inplace=True)
    return hr_df.merge(rest_hr_df, how='outer', on='date')

# process nutrition data
def transform_nutrition(df):
    '''
    INPUT
    ----------
    df : dataframe with nutrition data from myfitnesspal.

    OUTPUT
    -------
    Cleaned dataframe with missing values in every meal where nothing was
    recorded.
    '''
    df = df.filter(['Date', 'Meal', 'Time', 'Calories', 'Carbohydrates (g)',
                    'Fat (g)', 'Protein (g)'])
    df['Date'] = pd.to_datetime(df['Date'])
    df['Date'] = df['Date'].dt.date
    df['time'] = pd.to_datetime(df['Time']).dt.time
    df.rename(columns={'Date': 'date', 'Meal': 'meal', 'Calories': 'calories',
                       'Carbohydrates (g)': 'carbs', 'Fat (g)': 'fats',
                       'Protein (g)': 'proteins'}, inplace=True)
    df.drop(['Time'], axis=1, inplace=True)
    date_today = datetime.now()
    dates = pd.DataFrame(np.repeat(pd.date_range('2019-08-01 00:00:00',
                                                 date_today, freq='D'), 6))
    dates['date'] = pd.to_datetime(dates[0]).dt.date
    dates.drop(0, axis=1, inplace=True)
    x = pd.concat([pd.Series(['Meal 1', 'Meal 2', 'Meal 3', 'Meal 4', 'Meal 5',
                              'Meal 6'])]*int(len(dates)/6), axis=0,
                  ignore_index=True)
    dates['meal'] = x
    return dates.merge(df, how='left', on=['date', 'meal'])

# load data from database
conn = sqlite3.connect('./Data/Health.db')
workout = pd.read_sql('SELECT * FROM Workout', conn)
activeEnergy = pd.read_sql('SELECT * FROM ActiveEnergy', conn)
restEnergy = pd.read_sql('SELECT * FROM RestEnergy', conn)
weight = pd.read_sql('SELECT * FROM Bodyweight', conn)
steps = pd.read_sql('SELECT * FROM Steps', conn)
standing = pd.read_sql('SELECT * FROM Standing', conn)
heartRate = pd.read_sql('SELECT * FROM HeartRate', conn)
restingHeartRate = pd.read_sql('SELECT * FROM RestingHeartRate', conn)
nutrition = pd.read_sql('SELECT * FROM Nutrition', conn)

# apply functions
energy = transform_BurnedEnergy(restEnergy, activeEnergy)
workout = transform_workout(workout)
weight = transform_weight(weight)
activity = transform_activity(standing, steps)
heartrate = transform_health(heartRate, restingHeartRate)
nutrition = transform_nutrition(nutrition)

# filter all datasets for date > 2019-07-31 and drop last date
def date_filter(df, date):
    '''
    INPUT
    ----------
    df : dataframe which wants to be filtered by time.
    date : date after which the dataframe can contain observations.

    OUTPUT
    -------
    df : filtered dataframe.
    '''
    last_day = df.iloc[-1:]['date'].values
    df = df.loc[pd.to_datetime(df['date']) > pd.to_datetime(date)]
    df = df.loc[pd.to_datetime(df['date']) < pd.to_datetime(last_day[0])]
    return df
date = '2019-07-31'
energy = date_filter(energy, date)
workout = date_filter(workout, date)
weight = date_filter(weight, date)
activity = date_filter(activity, date)
heartrate = date_filter(heartrate, date)
nutrition = date_filter(nutrition, date)

# handle missing values
## weight
for col in weight.columns:
    if col == 'bodyweight':
        weight[col].interpolate(method='linear', inplace=True)
        weight[col] = round(weight[col], 1)
    elif col == 'sourceName':
        weight[col].fillna('Health', inplace = True)
    elif col == 'unit':
        weight[col].fillna('kg', inplace = True)
    elif col == 'time':
        weight[col].fillna('00:00:00.000000', inplace = True)
    else:
        None

## workout
for col in workout.columns:
    if col == 'workoutActivityType':
        workout[col].fillna('NoWorkout', inplace = True)
    elif col == 'sourceName':
        workout[col].fillna('GymGoal Pro', inplace = True)
    elif col == 'startTime':
        workout[col].fillna('00:00:00.000000', inplace = True)
    elif col == 'endTime':
        workout[col].fillna('00:00:00.000000', inplace = True)
    else:
        None
const_col = ['durationUnit', 'totalDistanceUnit', 'totalEnergyBurnedUnit']
for col in const_col:
    workout[col].fillna(method='ffill', inplace=True)

zero_col = ['duration', 'totalDistance', 'totalEnergyBurned']
for col in zero_col:
    workout[col].fillna(0, inplace=True)

## activity
activity.fillna(0, inplace=True)

## nutrition
daily_cal = nutrition[['date', 'calories']].groupby('date').sum()
nan_days = daily_cal.loc[daily_cal['calories']==0].index
median_cal = daily_cal.median()[0]/6
fats = (median_cal*0.2)/9.3
proteins = (median_cal*0.4)/4.1
carbs = (median_cal*0.4)/4.1
nutrition['calories'] = nutrition.apply(
    lambda row: round(median_cal, 1) if row['date'] in list(nan_days)
    else row['calories'],
    axis=1)
nutrition['fats'] = nutrition.apply(
    lambda row: round(fats, 1) if row['date'] in list(nan_days)
    else row['fats'],
    axis=1)
nutrition['proteins'] = nutrition.apply(
    lambda row: round(proteins, 1) if row['date'] in list(nan_days)
    else row['proteins'],
    axis=1)
nutrition['carbs'] = nutrition.apply(
    lambda row: round(carbs, 1) if row['date'] in list(nan_days)
    else row['carbs'],
    axis=1)
for col in ['calories', 'fats', 'carbs', 'proteins']:
    nutrition[col].fillna(0.0, inplace=True)
def fillna_mealtime(df, meal, time):
    df.loc[df['meal']==meal] = df.loc[df['meal']==meal].fillna(time)
fillna_mealtime(nutrition, 'Meal 1', '7:00:00.000000')
fillna_mealtime(nutrition, 'Meal 2', '10:00:00.000000')
fillna_mealtime(nutrition, 'Meal 3', '13:00:00.000000')
fillna_mealtime(nutrition, 'Meal 4', '16:00:00.000000')
fillna_mealtime(nutrition, 'Meal 5', '19:00:00.000000')
fillna_mealtime(nutrition, 'Meal 6', '21:00:00.000000')

# delete all current tables in database
tables = list(conn.execute(
    "SELECT name FROM sqlite_master WHERE type='table';")
    )
conn.close()
conn = sqlite3.connect('./Data/Health.db')
cursor = conn.cursor()
for name in tables:
    drop = 'DROP Table '+name[0]
    cursor.execute(drop)

# store data in sqlite
conn = sqlite3.connect('./Data/Health.db')
energy.to_sql('EnergyConsumption', conn, index=False, if_exists='replace')
workout.to_sql('Workout', conn, index=False, if_exists='replace')
weight.to_sql('Bodyweight', conn, index=False, if_exists='replace')
activity.to_sql('Activity', conn, index=False, if_exists='replace')
heartrate.to_sql('HeartRate', conn, index=False, if_exists='replace')
nutrition.to_sql('Nutrition', conn, index=False, if_exists='replace')
print()
print('Tables successfully stored in "./Data/Health.db"')