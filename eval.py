"""
eval.py
evaluation of the climate data
"""

import pandas as pd
import numpy as np
import requests
import json
import matplotlib.pyplot as plt

plt.close("all")

X = requests.get("http://device32/cgi-bin/present_cgi.py?drq=X")
Temps = pd.DataFrame(X.json()['rows'])
D = requests.get("http://device32/cgi-bin/present_cgi.py?drq=D")
Gas = pd.DataFrame(D.json()['rows'])
Comb = Temps.merge(Gas, on=0)
Comb.plot.scatter('1_x', '2_y')
plt.show()
