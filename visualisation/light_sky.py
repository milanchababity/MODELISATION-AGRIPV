import math
import numpy as np
import pandas as pd
import pvlib as pv

# -------------------------------
# Fonctions de traitement météo
# -------------------------------

def convert_panda_datemine(data_met):
    """Crée un DatetimeIndex pandas à partir du dictionnaire de paramètres."""
    start = data_met["start"]
    end = data_met["end"]
    tz = data_met["tz"]
    times = pd.date_range(start, end, freq="1h", tz=tz)
    return times 

def calcul_azimut_elev(data_met):
    """Calcule azimuth et élévation solaire avec pvlib."""
    latitude = data_met["latitude"]
    longitude = data_met["longitude"]
    times = convert_panda_datemine(data_met)
    data_angle = pv.solarposition.get_solarposition(times, latitude, longitude)
    return data_angle

def separate_date_hour(dataframe):
    """Sépare la colonne datetime en date et heure."""
    dataframe = dataframe.reset_index()
    dataframe.rename(columns={"index":"date_heure"}, inplace=True)
    dataframe["date"] = dataframe["date_heure"].dt.date
    dataframe["time"] = dataframe["date_heure"].dt.time
    return dataframe

def coordon_x_y_z(dataframe):
    """Calcule les coordonnées cartésiennes (x, y, z) du soleil à partir de l'azimut et élévation."""
    elevation = np.radians(dataframe["apparent_elevation"])
    azimuth = np.radians(dataframe["azimuth"])
    dataframe["x"] = np.cos(elevation) * np.sin(azimuth)
    dataframe["y"] = np.cos(elevation) * np.cos(azimuth)
    dataframe["z"] = np.sin(elevation)
    return dataframe

def coordinate_extraction(dataframe):
    """Extrait les vecteurs (x, y, z) du soleil avec z>0 pour Caribu."""
    dataframe = dataframe[dataframe["z"] > 0]
    coords = list(zip(dataframe["x"], dataframe["y"], dataframe["z"]))
    return coords

def selection(nb, coord):
    """Sélectionne les nb premiers vecteurs de la liste coord."""
    return coord[:nb]

def fonction_cvt_light(intensity, coord):
    """Crée le format attendu par Caribu : liste de tuples (direction, intensity)."""
    light = [(c, intensity) for c in coord]
    return light