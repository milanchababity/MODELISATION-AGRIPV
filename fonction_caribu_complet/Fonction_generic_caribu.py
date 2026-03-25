#### importation des modules #############################
import math 
import os.path
import numpy as np
from openalea.caribu.CaribuScene import CaribuScene
from openalea.caribu.plantgl_adaptor import scene_to_cscene
from openalea.plantgl.all import *
import recup_meteo
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap,ListedColormap
from recup_meteo import coordinate_extraction
from recup_meteo import fonction_cvt_light,calcul_azimut_elev,separate_date_hour,coordon_x_y_z,coordinate_extraction,z_caribu
from tqdm import tqdm

### fonctions geometriques
## maillage version 2 operationelle 
"""
creation de maillage sol centre (0,0,0)
resolution=resolution du maillage 
longueur = longueur du sol
largeur= largeur du sol

"""
## maillage version 2 operationelle 
def maillage_sol_fonct(resol,longueur, largeur,ep=0.001):
    res_x=resol
    res_y=resol
    ep=ep
    nb_pixel_x=math.ceil(longueur/resol)
    nb_pixel_y=math.ceil(largeur/resol)
    careau_unit=Box(Vector3(res_x/2,res_y/2,ep))
    maillage=[]
    idx=0
    ### centralisation du maillage 
    pos_x_depart= -((nb_pixel_x-1)*res_x)/2
    pos_y_depart= -((nb_pixel_y-1)*res_y)/2
    ## maillage totaux
    for i in range(nb_pixel_x):
        for j in range(nb_pixel_y):
            x_final = pos_x_depart + (res_x * i)
            y_final = pos_y_depart + (res_y * j)
            objet=Shape(Translated(Vector3(x_final,y_final,0),careau_unit),id=idx)
            maillage.append(objet)
            idx+=1
    return maillage
"""
def maillage_sol_centre(resol,longueur, largeur,ep=0.001):
    res_x=resol
    res_y=resol
    ep=ep
    nb_pixel_x=math.ceil(longueur/resol)
    nb_pixel_y=math.ceil(largeur/resol)
    careau_unit=Box(Vector3(res_x/2,res_y/2,ep))
    maillage=[]
    idx=0
    ### centralisation du maillage 
    pos_x_depart= -((nb_pixel_x-1)*res_x)/2
    pos_y_depart= -((nb_pixel_y-1)*res_y)/2
    ## maillage totaux
    for i in range(nb_pixel_x):
        for j in range(nb_pixel_y):
            x_final = pos_x_depart + (res_x * i)
            y_final = pos_y_depart + (res_y * j)
            objet=Shape(Translated(Vector3(x_final,y_final,0),careau_unit),id=idx)
            maillage.append(objet)
            idx+=1
    return maillage
""" 

### maillage panneau operationnel (version 2)
def maillage_panneau(longueur_p, largeur_p, resolution_p=0.01,epais_p=0.001):
    maillage_panel = []
    
    # 1. Résolution
    step_x = resolution_p
    step_y = resolution_p

    # 2. Calcul du nombre de carreaux
    nb_carre_long = math.ceil(longueur_p / step_x)
    nb_carre_larg = math.ceil(largeur_p / step_y)

    # 3. Définition du pixel
    # On garde la Box standard (centrée par défaut)
    carreau_geom = Box(step_x/2, step_y/2, epais_p/2)

    # 4. Calcul du décalage global pour centrer le panneau sur (0,0)
    # On divise la dimension totale par 2
    offset_p_x = -(nb_carre_long * step_x) / 2
    offset_p_y = -(nb_carre_larg * step_y) / 2
    for i in range(nb_carre_long):
        for j in range(nb_carre_larg):
            # CALCUL CRUCIAL :
            # On part du bord (offset) + l'avancée (i * step)
            # + la DEMI-LARGEUR (step/2) pour que le CENTRE de la box soit au bon endroit.
            pos_x = offset_p_x + (i * step_x) + (step_x / 2)
            pos_y = offset_p_y + (j * step_y) + (step_y / 2)
            
            # On place le panneau (Translation)
            temp = Shape(Translated(Vector3(pos_x, pos_y, 0), carreau_geom))
            maillage_panel.append(temp)
    return maillage_panel

senario=maillage_panneau(2,3,0.1,0.001)

senario=Scene (senario)
Viewer.display(senario)

def creation_panel(longueur_p, largeur_p, resolution_p, nb_panel, nb_rangee, ecart_panel, ecart_rangee, hauteur_p, angle_p=0):
    # 1. On récupère les pixels centrés sur (0,0,0) via ta fonction de maillage
    panel_base = maillage_panneau(longueur_p, largeur_p, resolution_p)
    panel_mesh = []
    angle_radian = math.radians(angle_p)
    
    # Offsets pour centrer la GRILLE de panneaux dans la scène
    offset_x_global = -((nb_panel - 1) * ecart_panel) / 2
    offset_y_global = -((nb_rangee - 1) * ecart_rangee) / 2
    idx=1
    for i in range(nb_panel):
        for j in range(nb_rangee):
            pos_x_grille = offset_x_global + (i * ecart_panel)
            pos_y_grille = offset_y_global + (j * ecart_rangee)
            for pixel in panel_base:
                # A. Décalage de bord (Pivot) : On déplace le pixel pour que le bord du panneau soit à Y=0
                # On utilise .geometry car 'pixel' est une Shape
                pixel_au_bord = Translated(Vector3(0, -largeur_p/2, 0), pixel.geometry)
                # B. Inclinaison : Le pivot est maintenant sur le bord (Y=0)
                pixel_incline = AxisRotated(Vector3(1, 0, 0), angle_radian, pixel_au_bord)
                # C. Placement Final : On le monte à 'hauteur_p' et on le place dans la grille
                pixel_final = (Translated(Vector3(pos_x_grille, pos_y_grille, hauteur_p), pixel_incline))
                # On enregistre en tant que Shape pour Caribu
                panel_mesh.append(Shape(pixel_final))
    return panel_mesh

senario=creation_panel(2,3,0.1,3,3,3,3,2,30)

panel =type_panneau_orient(params_panel)
ob=Scene(panel)
Viewer.display(scene)
## ### creation des panneaux en parapluie et orientation exacte 
def type_panneau_orient(params):
    ### params dicco
    orientation=params.get("orientation")
    type_panneau=params.get("type_panneau")
    longueur_p=params.get("longueur_p")
    largeur_p=params.get("largeur_p")
    resolution_p=params.get("resolution_p")
    nb_panel=params.get("nb_panel")
    nb_rangee=params.get("nb_rangee")
    ecart_panel=params.get("ecart_panel")
    ecart_rangee=params.get("ecart_rangee")
    hauteur_p=params.get("hauteur_p")
    angle_p=params.get("angle_p")
    
    # 1. On génère le premier versant (maillé et déjà placé en grille)
    panneau_init = creation_panel(longueur_p, largeur_p, resolution_p, nb_panel, nb_rangee, ecart_panel, ecart_rangee, hauteur_p, angle_p)
    mapping = {"sud": 0, "nord": math.pi, "est": math.pi/2, "ouest": -math.pi/2}
    angle_rot = mapping.get(orientation.lower(), 0)
    if type_panneau == "chapeau":
        # 2. On crée le versant opposé par rotation de 180° (PI)
        # On extrait .geometry de chaque pixel de panneau_init
        panneau_oppose = [Shape(AxisRotated(Vector3(0,0,1), math.pi, p.geometry)) for p in panneau_init]
        # 3. On fusionne les deux listes pour avoir le chapeau complet (tous les pixels)
        chapeau_complet = panneau_init + panneau_oppose
        # 4. On applique la rotation globale (Orientation Sud/Nord/...) à chaque pixel
        return [Shape(AxisRotated(Vector3(0,0,1), angle_rot, p.geometry)) for p in chapeau_complet]
    # Si ce n'est pas un chapeau, on oriente juste le premier versant
    return [Shape(AxisRotated(Vector3(0,0,1), angle_rot, p.geometry)) for p in panneau_init]

################################################# module annexe ##########################################
## fonction annexe 
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
def coordinate_extraction(data_test):
    data_angle= calcul_azimut_elev(data_test)
    data_date_heure=separate_date_hour(data_angle)
    data_frame_xyz=coordon_x_y_z(data_date_heure)
    dataframe=data_frame_xyz[data_frame_xyz["z"]>0]
    datafinal=dataframe[["date_heure","hour","min","x","y","z"]]
    return datafinal
"""
def scene_illumination(objet_scene,data_date,plot=False):
    raw,aggr=[],[]
    scene_3D,values_3D =[],[]
    data_frame=pd.DataFrame()
    for index,row in tqdm(data_date.iterrows()):
        x,y,z=row["x"],row["y"],row["z"]
        light=[(1,(x,y,-z))]
        cs=CaribuScene(objet_scene,light)
        mes,cum=cs.run(simplify=True,infinite=False)
        agregate=list(cum["Ei"].values())
        pas_de_temps=row["date_heure"]
        data=data_frame.concat({pas_de_temps:agregate})
        raw.append(mes)
        aggr.append(cum)
        if plot:   
           plot_3d,value=cs.plot(mes["Ei"],0,1,0.2,display=False)
           scene_3D.append(plot_3d)
           values_3D.append(value)
    if plot:
        return raw,aggr,scene_3D,values_3D
    else:
        return raw,aggr
""" 

#### automatisation de caribu
###" fonction de lancement automatisé de CARIBU avec un objet scene creer "

from tqdm import tqdm
import pandas as pd
# methode d'extraction des données en tableau pandas 
def scene_carbi_run(caribuscene,data_date):
    count=0
    for index, row in tqdm(data_date.iterrows(), total=len(data_date)):
        x, y, z = row["x"], row["y"], row["z"]
        light = [(1, (x, y, -z))]
        cs = CaribuScene(caribuscene, light)
        _,aggregate=cs.run(simplify=True, infinite=False)
        triangles=list(aggregate["Ei"].keys())
        values=list(aggregate["Ei"].values())
        dict_values={"Triangles":triangles,row["hour"]:values}
        if count==0:
            data_fix=pd.DataFrame.from_dict(dict_values)
            data_fix.set_index("Triangles",inplace=True)
            count+=1
        else:
            data2=pd.DataFrame.from_dict(dict_values)
            data2.set_index("Triangles",inplace=True)
            data_fix=data_fix.merge(data2,"outer","Triangles")
    return data_fix
            
 #####################################       
    
    
    
    
    
    
    
    
    

def scene_illumination(objet_scene, data_date, plot=False):
    raw, aggr = [], []
    scene_3D, values_3D = [], []
    # Récupérer les IDs fixes depuis la première exécution
    premier_row = data_date.iloc[0]
    x, y, z = premier_row["x"], premier_row["y"], premier_row["z"]
    light = [(1, (x, y, -z))]
    cs = CaribuScene(objet_scene, light)
    _, cum = cs.run(simplify=True, infinite=False)
    id_shape = list(cum["Ei"].keys())  # IDs fixes

    # Liste pour stocker les lignes du DataFrame
    data_lignes = []
    for index, row in tqdm(data_date.iterrows(), total=len(data_date)):
        x, y, z = row["x"], row["y"], row["z"]
        light = [(1, (x, y, -z))]
        cs = CaribuScene(objet_scene, light)
        mes, cum = cs.run(simplify=True, infinite=False)
        agregate = list(cum["Ei"].values())
        # Ajouter une ligne avec date_heure + valeurs
        ligne = {"date_heure": row["date_heure"]}
        ligne.update({id_shape[i]: agregate[i] for i in range(len(id_shape))})
        data_lignes.append(ligne)
        raw.append(mes)
        aggr.append(cum)
        if plot:
            plot_3d, value = cs.plot(mes["Ei"], 0, 1, 0.2, display=False)
            scene_3D.append(plot_3d)
            values_3D.append(value)
    # Construire le DataFrame final
    data = pd.DataFrame(data_lignes)

    if plot:
        return raw, aggr, scene_3D, values_3D, data
    else:
        return raw, aggr, data

data_met={
    "start":"2025-05-06",
    "end":"2025-05-07",
    "tz":"Europe/Paris",
    "latitude":47.23,
    "longitude":3.30,
}
data=coordinate_extraction(data_met)
print(data)

params_panel={
    "orientation":"sud",
    "type_panneau":"normal",
    "longueur_p":1.7,
    "largeur_p":1.5,
    "resolution_p":0.4,
    "nb_panel":4,
    "nb_rangee":4,
    "ecart_panel":2,
    "ecart_rangee":4,
    "hauteur_p":3,
    "angle_p":30
}
panel =type_panneau_orient(params_panel)
ob=Scene(panel)
Viewer.display(scene)


params_sol={
    "resolution_p":0.1,
    "longueur_sol":6,
    "largeur_sol":10,
    "epaisseur_sol":0.01,
}

maillage_sol=maillage_sol_fonct(resol=0.2,longueur=8, largeur=10,ep=0.001)
sol=Scene(maillage_sol)
scene=Scene()
scene.add(sol)
scene.add(ob)

print(data.head)
data_panda_doc=scene_carbi_run(caribuscene=scene,data_date=data)
print(data_panda_doc.columns)

data_panda_doc.to_csv("valeur_energie.csv",sep=",")
#extraction dans dataframe



raw,agg,data=scene_illumination(scene,data,plot=False)
print((agg[0]["Ei"].values()))
keys=list(agg[0]["Ei"].keys())
print(keys[1])
values=list(agg[0]["Ei"].values())
col1="shape_id"
col2="value_id"
col3="date_heure"
datapanda=pd.DataFrame({col1:keys,col2:values})


data.mean(axis=1)


################################################################################################