"""
 * config.js
 * contains the config object in js (not json!) format.
 + It is loaded vi html script - dircetive because it must be present
 * before the "fetched" data arrive
 * !SYNCHRONIZE THIS WITH config.py IN THE PYTHON DIRECTORY1
"""
 
Config = {"807D3AFDE134": {"name": "Keller", "color": "green"},
            "807D3AFDE135": {"name": "Aussen", "color": "red"},
            "807D3AFDE136": {"name": "Esszimmer", "color": "blue"},
            "VOL": {"name": "Volumen (m³)"},                
            "DTL": {"name": "täglicher Zählerstand"},
            "AVG": {"name": "Temperaturmittelwert (°C)"},
			"DAT": {"name": "Datum"},
			"TME": {"name": "Uhrzeit"}
		}
            