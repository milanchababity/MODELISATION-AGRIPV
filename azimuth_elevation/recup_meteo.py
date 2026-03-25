import math

import numpy as np
import pandas as pd
import pvlib as pv

#### get parameter azimuth and sun angulaire 

def convert_panda_datemine(data_test):
    ### extraction parameters
    start=data_test.get("start")
    end=data_test.get("end")
    tz=data_test.get("tz")
    ### creation datetime table with pandas
    times=pd.date_range(start,end,freq="15min",tz=tz)
    return times 


def calcul_azimut_elev(data_test):
    # extraction parameters
    latitude=data_test.get("latitude")
    longitude=data_test.get("longitude")
    start=data_test.get("start")
    end=data_test.get("end")
    tz=data_test.get("tz")
    ### datetime creation
    times = convert_panda_datemine(data_test)
    ### calcul solar_position
    data_angle=pv.solarposition.get_solarposition(times,latitude,longitude)
    return data_angle

##### create day and hour in panda dataframe
def separate_date_hour(dataframe):
    dataframe=dataframe.reset_index()
    dataframe.rename(columns={"index":"date_heure"},inplace=True)
    dataframe["date"]=dataframe["date_heure"].dt.date
    dataframe["hour"]=dataframe["date_heure"].dt.time
    dataframe["min"]=dataframe["date_heure"].dt.minute
    return dataframe

###calculation cartesians points
def coordon_x_y_z(dataframe):
    elevation=np.radians(dataframe["apparent_elevation"])
    azimuth=np.radians(dataframe["azimuth"])
    dataframe["x"] = np.cos(elevation) * np.sin(azimuth)
    dataframe["y"] = np.cos(elevation) * np.cos(azimuth)
    dataframe["z"] = np.sin(elevation)
    return dataframe

### computation of coordinates 
def coordinate_extraction(dataframe):
    dataframe=dataframe[dataframe["z"]>0]
    date=dataframe[["date_heure","hour","min","x","y","z"]]
    return date

## Z caribu 
def z_caribu(coordo_z,intens):
    ajus=[]
    for i in range (len(coordo_z)):
        inter=(intens,(coordo_z[i][0],coordo_z[i][1],-coordo_z[i][2]))
        ajus.append(inter)
    return ajus
        
###### little test selection 
def selection (nb,coord):
    doc=[]
    for ls in range(nb):
        doc.append(coord[ls])
    return doc

##### creation format light
def fonction_cvt_light(intensity,coord):
    light=[]
    for i in range(len(coord)):
        cod=(intensity,coord[i])
        light.append(cod)
    return light





        
        

