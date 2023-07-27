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

def isSummer(ind):
    dat = date.fromisoformat(ind)
    if dat.month < 5 or dat.month > 10: return False
    if dat.month == 5 and dat.day < 15: return False
    if dat.month == 10 and dat.day > 15: return False    
    return True
    
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
    text = "gas [kWh] = %.0f + temp [°C] * %.2f [kWh/°C]" % (model.intercept_[0], model.coef_[0][0])
    plt.text((x_right + x_left) * 0.3, (np.amax(g) + np.amin(g)) * 0.9 , text)
    plt.savefig(dest / name)
    # plt.show()



X = requests.get("http://device32/cgi-bin/present_cgi.py?drq=X")
Temps = pd.DataFrame(X.json()['rows'])
SummerTemps = Temps.loc[(isSummer(ind) for ind in Temps[0])]
D = requests.get("http://device32/cgi-bin/present_cgi.py?drq=D")
Gas = pd.DataFrame(D.json()['rows'])
SummerComb = SummerTemps.merge(Gas, on=0, suffixes=('_Temp', '_Gas'))
SummerComb['1_Gas'] *= HeatVal * zVal
showResult(SummerComb, "summer.png")
WinterTemps = Temps.loc[(not isSummer(ind) for ind in Temps[0])]
WinterComb = WinterTemps.merge(Gas, on=0, suffixes=('_Temp', '_Gas'))
WinterComb['1_Gas'] *= HeatVal * zVal
showResult(WinterComb, "winter.png")
