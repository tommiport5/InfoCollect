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

zVal = 0.9374
HeatVal = 11.5

dest = Path("C:\\temp")

plt.close("all")

X = requests.get("http://device32/cgi-bin/present_cgi.py?drq=X")
Temps = pd.DataFrame(X.json()['rows'])
D = requests.get("http://device32/cgi-bin/present_cgi.py?drq=D")
Gas = pd.DataFrame(D.json()['rows'])
Comb = Temps.merge(Gas, on=0, suffixes=('_Temp', '_Gas'))
Comb['1_Gas'] *= HeatVal * zVal
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
plt.text(0, 162, "gas [kWh] = %.0f + temp [°C] * %.2f [kWh/°C]" % (model.intercept_[0], model.coef_[0][0]))
plt.savefig(dest / "eval.png")
plt.show()
