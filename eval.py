"""
eval.py
evaluation of the climate data
"""

import pandas as pd
import numpy as np
import requests
import json
import matplotlib.pyplot as plt
import sklearn.linear_model as lm
from pathlib import Path
from datetime import date

zVal = 0.9374
HeatVal = 11.5

dest = Path("/home/dad/Tools/html")
# dest = Path("C:/Users/Dad/Documents/GitHub/InfoCollect")

def isSummer(ind):
    dat = date.fromisoformat(ind)
    if dat.month < 5 or dat.month > 10: return False
    if dat.month == 5 and dat.day < 15: return False
    if dat.month == 10 and dat.day > 15: return False    
    return True
	
def isWinter(ind):
	return not isSummer(ind)

''' < 19.9.22 oder 20.5.23 ... 11.10.23'''
def isVaillantSummer(ind):
    dat = date.fromisoformat(ind)
    if dat < date(2022, 9, 19): return True
    if dat >= date(2023, 5, 20) and dat < date(2023, 10, 11): return True
    return False

''' 20.9.22 ... 19.5.23'''
def isVaillantWinter(ind):
    dat = date.fromisoformat(ind)
    if dat >= date(2022, 9, 22) and dat < date(2023, 5, 20): return True
    return False

''' > 11.10.23 '''
def isViessmannWinter(ind):
    dat = date.fromisoformat(ind)
    if dat >= date(2023, 10, 11): return True
    return False
   
def showResult(Comb, name):
    plt.close("all")
    Comb.plot.scatter('1_Temp', '1_Gas')
    model = lm.LinearRegression()
    t = np.array(Comb['1_Temp']).reshape(-1,1)
    g = np.array(Comb['1_Gas']).reshape(-1,1)
    model.fit(t,g)
    x_left = np.amin(t)
    x_right = np.amax(t)
    y_left = model.intercept_ + model.coef_[0][0] * x_left
    y_right = model.intercept_ + model.coef_[0][0] * x_right
    plt.plot([x_left, x_right], [y_left, y_right], 'r-')
    plt.ylabel('Gas (kWh)')
    plt.xlabel('Temperatur (°C)')
    text = "gas [kWh] = %.0f - temp [°C] * %.2f [kWh/°C]" % (model.intercept_[0], -model.coef_[0][0])
    plt.text((x_right + x_left) * 0.3, (np.amax(g) + np.amin(g)) * 0.9 , text)
    plt.savefig(dest / name)
    # plt.show()

def storeFile(TempFrame, GasFrame, discr, fname):
	filtTemps = TempFrame.loc[(discr(ind) for ind in TempFrame[0])]
	filtComb = filtTemps.merge(Gas, on=0, suffixes=('_Temp', '_Gas'))
	filtComb['1_Gas'] *= HeatVal * zVal
	showResult(filtComb, fname)

X = requests.get("http://device32/cgi-bin/present_cgi.py?drq=X")
Temps = pd.DataFrame(X.json()['rows'])
D = requests.get("http://device32/cgi-bin/present_cgi.py?drq=D")
Gas = pd.DataFrame(D.json()['rows'])
storeFile(Temps, Gas, isVaillantSummer, "vaillant_summer.png")
storeFile(Temps, Gas, isVaillantWinter, "vaillant_winter.png")
storeFile(Temps, Gas, isViessmannWinter, "viessmann_winter.png")
