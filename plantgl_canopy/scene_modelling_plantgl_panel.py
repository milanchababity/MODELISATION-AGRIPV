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

data_met={
    "start":"2026-01-01",
    "end":"2026-01-02",
    "tz":"Europe/Paris",
    "latitude":47.23,
    "longitude":3.30,
}
### fonction de creation de maillage au sol et des panneaux 

#### 1 maillage du sol en rectangulaire 
params_sol={
    "resolution_p":0.1,
    "longueur_sol":1,
    "largeur_sol":3,
    "epaisseur_sol":0.01,
}

### mailla version 1
def maillage_centre_sol(params_sol):
        # Parametres d'entree
    resolution_p=params_sol.get("resolution_p")
    longueur_sol=params_sol.get("longueur_sol")
    largeur_sol=params_sol.get("largeur_sol")
    epaisseur_sol=params_sol.get("epaisseur_sol")
        # 1. Résolution
    espace=0.98
    step_x = resolution_p
    step_y = resolution_p
        # 2. Calcul du nombre de carreaux
    nb_carre_sol_x = math.ceil(longueur_sol / step_x)
    nb_carre_sol_y = math.ceil(largeur_sol / step_y)
    
        # 3. Définition du pixel (légère épaisseur pour Caribu)
    carreau_geom = Box(resolution_p*espace, resolution_p*espace,epaisseur_sol)
    
        # initiation de maillage au sol 
    maillage_soil = []
        # --- CENTRAGE DU SOL ---
    # On calcule le décalage pour le sol
    offset_s_x = -((nb_carre_sol_x - 1) * step_x) / 2
    offset_s_y = -((nb_carre_sol_y - 1) * step_y) / 2
    id=0
    for i in range(nb_carre_sol_x):
            for j in range(nb_carre_sol_y):
                pos_x = offset_s_x + (i * step_x)
                pos_y = offset_s_y + (j * step_y)
            # On place le sol légèrement sous Z=0 pour éviter les conflits
                temp_2 = Shape(Translated(Vector3(pos_x, pos_y, 0), carreau_geom),id=id)
                maillage_soil.append(temp_2)
                id+=1
    return maillage_soil


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
##############################

            


# maillage du panneau en rectangulaire 
"""
def maillage_panneau(longueur_p,largeur_p,resolution_p=0.01):
    maillage_panel = []
        # 1. Résolution
    step_x = resolution_p
    step_y = resolution_p

    # 2. Calcul du nombre de carreaux
    nb_carre_long = math.ceil(longueur_p / step_x)
    nb_carre_larg = math.ceil(largeur_p / step_y)
        # 3. Définition du pixel (légère épaisseur pour Caribu)
    carreau_geom = Box(resolution_p, resolution_p, resolution_p)
        # On calcule le décalage pour que le bloc de maillage soit centré sur 0,0
    offset_p_x = -((nb_carre_long - 1) * step_x) / 2
    offset_p_y = -((nb_carre_larg - 1) * step_y) / 2
    for i in range(nb_carre_long):
        for j in range(nb_carre_larg):
            pos_x = offset_p_x + (i * step_x)
            pos_y = offset_p_y + (j * step_y)
            temp = Shape(Translated(Vector3(pos_x, pos_y, 0), carreau_geom))
            maillage_panel.append(temp)
            
    return maillage_panel
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
    idx=0
    for i in range(nb_carre_long):
        for j in range(nb_carre_larg):
            # CALCUL CRUCIAL :
            # On part du bord (offset) + l'avancée (i * step)
            # + la DEMI-LARGEUR (step/2) pour que le CENTRE de la box soit au bon endroit.
            pos_x = offset_p_x + (i * step_x) + (step_x / 2)
            pos_y = offset_p_y + (j * step_y) + (step_y / 2)
            
            # On place le panneau (Translation)
            temp = Shape(Translated(Vector3(pos_x, pos_y, 0), carreau_geom),id=idx)
            maillage_panel.append(temp)
            idx+=1
    return maillage_panel



def creation_panel(longueur_p, largeur_p, resolution_p, nb_panel, nb_rangee, ecart_panel, ecart_rangee, hauteur_p, angle_p=0):
    # 1. On récupère les pixels centrés sur (0,0,0) via ta fonction de maillage
    panel_base = maillage_panneau(longueur_p, largeur_p, resolution_p)
    panel_mesh = []
    angle_radian = math.radians(angle_p)
    
    # Offsets pour centrer la GRILLE de panneaux dans la scène
    offset_x_global = -((nb_panel - 1) * ecart_panel) / 2
    offset_y_global = -((nb_rangee - 1) * ecart_rangee) / 2

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
                pixel_final = Translated(Vector3(pos_x_grille, pos_y_grille, hauteur_p), pixel_incline)
                # On enregistre en tant que Shape pour Caribu
                panel_mesh.append(Shape(pixel_final))
                
    return panel_mesh

############ enter parameter fonction panel creation
params_panel={
    "orientation":"sud",
    "type_panneau":"chapeau",
    "longueur_p":1.7,
    "largeur_p":1.5,
    "resolution_p":0.1,
    "nb_panel":4,
    "nb_rangee":4,
    "ecart_panel":2,
    "ecart_rangee":4,
    "hauteur_p":3,
    "angle_p":30
}

### creation des panneaux en parapluie et orientation exacte
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
    mapping = {"sud": 0, "nord": math.pi, "est": -math.pi/2, "ouest": math.pi/2}
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

##### exemple d'application du code 


data_met={
    "start":"2025-05-06",
    "end":"2025-05-07",
    "tz":"Europe/Paris",
    "latitude":47.23,
    "longitude":3.30,
}

####" sky position 

### computation of coordinates 
def coordinate_extraction(data_test):
    data_angle= calcul_azimut_elev(data_test)
    data_date_heure=separate_date_hour(data_angle)
    data_frame_xyz=coordon_x_y_z(data_date_heure)
    dataframe=data_frame_xyz[data_frame_xyz["z"]>0]
    datafinal=dataframe[["date_heure","hour","min","x","y","z"]]
    return datafinal

    
###" fonction de lancement automatisé de CARIBU avec un objet scene creer "
def scene_illumination(objet_scene,data_date,plot=False):
    raw,aggr=[],[]
    scene_3D,values_3D =[],[]
    for index,row in tqdm(data_date.iterrows()):
        x,y,z=row["x"],row["y"],row["z"]
        light=[(1,(x,y,-z))]
        cs=CaribuScene(objet_scene,light)
        mes,cum=cs.run(simplify=True,infinite=False)
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
    
sol =maillage_sol_centre(resol=0.1,longueur=2,largeur=3)
sol_socle=Scene(sol)
Viewer.display(sol_socle)
test,agg=scene_illumination(sol_socle,data,plot=False)

print((agg[0]["Ei"].values()))



#################################################
## fonction data extract for plotting 
def extract_for_plotting (raw,tr):
    np_table_raw=[]
    np_table_tr=[]
    for obj in tqdm((raw)):
        array=np.array(list(obj["Ei"].values()))
        vect=array.reshape(-1,12)
        np_table_raw.append(vect)
    for j in tqdm(range (len(tr))):
        tria=tr[j]
        array_t=np.array(tria)
        tria_vect=array_t.reshape(-1,3)
        np_table_tr.append(tria_vect)
    return np_table_raw,np_table_tr

table_raw,table_vect=extract_for_plotting(raw,tr)
     
print((table_raw[0].shape))
print((table_vect[0].shape))

### 
don1=table_raw[0]
max_don1=don1.max(axis=1)
min_don1=don1.min(axis=1)
mean_don1=don1.mean(axis=1)
tot_don = np.concatenate((max_don1,min_don1),axis=1)
print(max_don1.shape)




#### demmarrage de Caribu
#### Fragmentation de données 
scene =Scene()
panneau = type_panneau_orient(params=params_panel)
scene_panel=Scene(panneau)
Viewer.display(scene_panel)

sol =maillage_centre_sol(params_sol=params_sol) 
socle =Scene(sol)
scene.add(socle)
scene.add(scene_panel)
Viewer.display(scene)

### test algo

raw,tr,gp,scene_3d,valeur=scene_illumination(light_total,scene,plot=True)


### caribu1########### capturation scene 
cs1= CaribuScene(scene,light=light_1)
raw1,agr1=cs1.run(simplify=True,infinite=False)
triangle,groupe, mater,band,albd=cs1.as_primitive()
print(triangle[0])
##### extraction data Ei


Ei_value=list(raw1["Ei"].values())
Ei_max=[]
Ei_min=[]
Ei_moy=[]
# extraction max or mean data Ei
for ener in Ei_value:
    Ei_max.append(max(ener))
    Ei_min.append(min(ener))
    Ei_moy.append((sum(ener)/len(ener)))
## numpy 
val_max=np.array(Ei_max)
val_min=np.array(Ei_min)
val_mean=np.array(Ei_min)

### triangle
coord_x=[]
coord_y=[]
for obj in triangle:
    for sob in obj:
        coord_x.append(sob[0])
        coord_y.append(sob[1])
        
ligne_x=np.array(coord_x)
ligne_y=np.array(coord_y)
x_panneaux = ligne_x.reshape(-1, 36).mean(axis=1)
y_panneaux = ligne_y.reshape(-1, 36).mean(axis=1)
ener_panneaux = np.array(Ei_max)



import matplotlib.pyplot as plt

plt.figure(figsize=(15, 10))

# 's=45' : taille des points pour qu'ils se touchent presque
# 'cmap='magma' : parfait pour l'énergie solaire (du noir au jaune éclatant)
# 'edgecolors='none' : pour éviter les contours qui brouillent la vue
scatter = plt.scatter(x_panneaux, y_panneaux, c=ener_panneaux, 
                     cmap='magma', s=45, edgecolors='none')

# Barre de légende avec unités
cb = plt.colorbar(scatter, pad=0.02)
cb.set_label('Irradiance Moyenne par Panneau (W/m²)', fontsize=12, fontweight='bold')

# Habillage du graphique
plt.axis('equal') # Garde les proportions réelles (ne pas étirer le champ)
plt.xlabel("Coordonnée X (m)", fontsize=10)
plt.ylabel("Coordonnée Y (m)", fontsize=10)
plt.title(f"Analyse d'Ensoleillement : Champ Photovoltaïque ({len(ener_panneaux)} modules)", 
          fontsize=15, pad=20)
plt.grid(True, linestyle=':', alpha=0.4)

plt.show()



# extration x et y coordinate
print(triangle[0])
print(Ei_value[0])
###### calcul des coordonnées X et Y
print(triangle[0])
print(triangle[0][1])
print(len(triangle[0]))
print(len(triangle[0][1]))
### calcul des centroids (x et y)
centr_x=[]
centr_y=[]
for list2 in triangle:
        moy_x=(list2[0][0] + list2[1][0] + list2[2][0])/3
        moy_y=(list2[0][1] + list2[1][1] + list2[2][1])/3
        centr_x.append(moy_x)
        centr_y.append(moy_y)
print(len(centr_x))
print(len(centr_y))


coord_ener=np.ravel(Ei_value)
coord_x=np.array(centr_x)
coord_y=np.array(centr_y)
## crentrage au milieu de x
coord_x_centre = coord_x - coord_x.mean()
print(coord_x.shape)
print(coord_y.shape)
print(coord_ener.shape)
print(coord_x_centre.shape)


import numpy as np

# 1. Calcul de la moyenne pour chaque ligne (panneau)
# On utilise l'axe 1 (les colonnes) pour faire la moyenne
Ei_array = np.array(Ei_value)
ener_moyenne_panneau = np.mean(Ei_array, axis=1) 

# 2. Calcul des coordonnées centrales du PANNEAU complet
# Il nous faut 1 coordonnée (X, Y) par panneau (on en a 29760)
x_panneau = []
y_panneau = []

# On parcourt par bonds de 12 dans la liste des triangles
for i in range(0, len(triangle), 12):
    # On prend les 12 triangles du panneau i
    groupe_triangles = triangle[i:i+12]
    
    # On calcule la moyenne de TOUS les sommets de ces 12 triangles
    x_coords = []
    y_coords = []
    for tri in groupe_triangles:
        for pt in tri:
            x_coords.append(pt[0])
            y_coords.append(pt[1])
            
    x_panneau.append(np.mean(x_coords))
    y_panneau.append(np.mean(y_coords))

# Conversion en Array pour Matplotlib
x_panneau = np.array(x_panneau)
y_panneau = np.array(y_panneau)








scene1,value1 =cs1.plot(raw1["Ei"],0,1,0.2,display=True)
Viewer.camera.setPosition((10, 0, 10))
Viewer.camera.lookAt((0, 0, 0))
Viewer.saveSnapshot("panel.png")
## caribu 2
cs2= CaribuScene(scene,light=light_2)
raw2,agr2=cs2.run(simplify=True,infinite=False)
scene2,value2 =cs2.plot(raw2["Ei"],0,1,0.2,display=True)
Viewer.display(scene2)
Viewer.camera.setPosition((10, 0, 10))
Viewer.camera.lookAt((0, 0, 0))
Viewer.saveSnapshot("panel2.png")

## caribu 3
cs3= CaribuScene(scene,light=light_3)
raw3,agr3=cs3.run(simplify=True,infinite=False)
scene3,value3 =cs3.plot(raw3["Ei"],0,1,0.2,display=True)
Viewer.camera.setPosition((10, 0, 10))
Viewer.camera.lookAt((0, 0, 0))
Viewer.saveSnapshot("panel3.png")

## caribu 4
cs4= CaribuScene(scene,light=light_4)
raw4,agr4=cs4.run(simplify=True,infinite=False)
scene4,value4 =cs4.plot(raw4["Ei"],0,1,0.2,display=True)
Viewer.camera.setPosition((10, 0, 10))
Viewer.camera.lookAt((0, 0, 0))
Viewer.saveSnapshot("panel4.png")

#caribu 5
cs5= CaribuScene(scene,light=light_5)
raw5,agr5=cs5.run(simplify=True,infinite=False)
scene5,value5 =cs5.plot(raw5["Ei"],0,1,0.2,display=True)
Viewer.camera.setPosition((10, 0, 10))
Viewer.camera.lookAt((0, 0, 0))
Viewer.saveSnapshot("panel5.png")

# caribu 6

cs6= CaribuScene(scene,light=light_6)
raw6,agr6=cs6.run(simplify=True,infinite=False)
scene6,value6 =cs6.plot(raw6["Ei"],0,1,0.2,display=True)
Viewer.camera.setPosition((10, 0, 10))
Viewer.camera.lookAt((0, 0, 0))
Viewer.saveSnapshot("panel6.png")

# caribu 7
cs7= CaribuScene(scene,light=light_7)
raw7,agr7=cs7.run(simplify=True,infinite=False)
scene7,value7 =cs7.plot(raw7["Ei"],0,1,0.2,display=True)
Viewer.camera.setPosition((10, 0, 10))
Viewer.camera.lookAt((0, 0, 0))
Viewer.saveSnapshot("panel7.png")

# Caribu 8
cs8= CaribuScene(scene,light=light_8)
raw8,agr8=cs8.run(simplify=True,infinite=False)
scene8,value8 =cs8.plot(raw8["Ei"],0,1,0.2,display=True)
Viewer.camera.setPosition((10, 0, 10))
Viewer.camera.lookAt((0, 0, 0))
Viewer.saveSnapshot("panel8.png")

tri, grou, mater, ban, albd=cs8.as_primitive()

# Caribu 9
cs9= CaribuScene(scene,light=light_9)
raw9,agr9=cs9.run(simplify=True,infinite=False)
scene9,value9 =cs9.plot(raw9["Ei"],0,1,0.2,display=True)
Viewer.camera.setPosition((10, 0, 10))
Viewer.camera.lookAt((0, 0, 0))
Viewer.saveSnapshot("panel9.png")

from openalea.plantgl.all import Viewer
Viewer.camera.resetView()
Viewer.display(scene1)
Viewer.camera.setPerspective(True)
Viewer.camera.setPosition((10, 0, 10))
Viewer.camera.lookAt((0, 0, 0))

Viewer.update()

print(dir(Viewer))





Ei=list(raw1["Ei"].values())
print((Ei))

tot = []
for i in range(len(Ei[0])):
    for row in Ei:
        tot.append(row[i])
        
print(len(tot))
    

print(total)


    
    
print(len(raw1["Ei"].values()))
triangles, groups, materials, bands, albedo=cs1.as_primitive()
print(max(groups))
print(min(groups))
print(max(testa))
print(min(testa))
for ligne in triangles[:10]:
    print(ligne)
for ligne in groups[:10]:
    print(ligne)
testa=raw1["Ei"].keys() 
 
print(raw1["Ei"])
triangle_primitive=triangles
ids_raw=raw1["Ei"].keys()
ids_primitive=groups

print(len(ids_raw))
print(len(ids_primitive))
print(len(triangle_primitive))

print(max(ids_raw))
print(max(triangle_primitive))
print(max(ids_primitive))

print(min(ids_primitive))
print(min(ids_raw))
print(min(triangle_primitive))
print(ids_primitive[0:12])

import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict

# 1. RECONSTRUCTION DU DICTIONNAIRE (Étape manquante)
print("Reconstruction du dictionnaire objet_complet...")
objet_complet = defaultdict(list)
for i in range(len(ids_primitive)):
    obj_id = ids_primitive[i]
    tri = triangle_primitive[i]
    objet_complet[obj_id].append(tri)

# 2. PRÉPARATION DES LISTES POUR LE GRAPHIQUE
x_centers = []
y_centers = []
values = []

print("Extraction des centres et des valeurs...")
for obj_id, triangles in objet_complet.items():
    # Géométrie : on calcule le centre x, y
    all_points = np.array(triangles).reshape(-1, 3)
    x_centers.append(np.mean(all_points[:, 0]))
    y_centers.append(np.mean(all_points[:, 1]))
    
    # Données : on récupère le max dans raw5 (votre dictionnaire actuel)
    valeurs_obj = raw5["Ei"][obj_id]
    values.append(max(valeurs_obj))

# 3. VÉRIFICATION ET AFFICHAGE
print(f"Nombre d'objets prêts pour le graphique : {len(x_centers)}")

if len(x_centers) > 0:
    plt.figure(figsize=(12, 8))
    # 's' est la taille des points, 'cmap' est la couleur
    sc = plt.scatter(x_centers, y_centers, c=values, cmap='magma', s=10)
    plt.colorbar(sc, label='Intensité Max (Données Ei)')
    plt.xlabel('Position X')
    plt.ylabel('Position Y')
    plt.title('Visualisation de la Structure (Heatmap)')
    plt.axis('equal') # Pour ne pas déformer la forme réelle
    plt.show()
else:
    print("Erreur : Toujours aucun point extrait.")

from collections import defaultdict

# Création d'un dictionnaire où la clé est l'ID 
# et la valeur est une liste de ses triangles
objet_complet = defaultdict(list)

for i in range(len(ids_primitive)):
    obj_id = ids_primitive[i]
    tri = triangle_primitive[i]
    objet_complet[obj_id].append(tri)

# Maintenant, pour n'importe quel ID, vous avez ses 12 triangles
print(f"L'objet 140923616 possède {len(objet_complet[140923616])} triangles.")
print(len(groups))
# Vérifier si tous les objets ont bien 12 triangles
counts = [len(triangles) for triangles in objet_complet.values()]
unique_counts = set(counts)

print(f"Nombre de triangles par objet trouvés : {unique_counts}")
scene1,value =cs1.plot(raw1["Ei"],0,1,0.2,display=True)
 


print(testa)
print(cs5.scene.items())
print(len(testa))
print(len(raw5["Ei"]))
triangles, groups, materials, bands, albedo=cs5.as_primitive()



##########output mapping fonction (3 dimension en 2 dimension)
def vectorisation_ax2(triangle,raw):
    triangle_final=[]
    for tri in range(len(triangle)):
        objet=(triangle[tri][0],triangle[tri][1])
        triangle_final.append(objet)

        
    return triangle_final  

#### extractions data essentials 
def extraction_raw(raw,cs):
    triangles, groups, materials, bands, albedo=cs.as_primitive()
    list_triangle=vectorisation_ax2(triangles)

def mapping_output(raw):
    figure,axes=plt.subplot()
    axes.set_xlabel("Axe_X")
    axes.set_ylabel("Axes_Y")
    figure.set_size_inches(7,5)
    figure.set_dpi(800)


import matplotlib.pyplot as plt
import numpy as np
import matplotlib.pyplot as plt
import numpy as np

import matplotlib.pyplot as plt
import numpy as np
##########################################################code visionnage 1##################
x_centers = []
y_centers = []
values = []

# On choisit l'index 10 car il semble avoir beaucoup de variations
INDEX_DONNEE = 10 

for obj_id, triangles in objet_complet.items():
    all_points = np.array(triangles).reshape(-1, 3)
    x_centers.append(np.mean(all_points[:, 0]))
    y_centers.append(np.mean(all_points[:, 1]))
    
    # Extraction de la donnée
    liste_valeurs = raw5["Ei"][obj_id]
    val = liste_valeurs[INDEX_DONNEE]
    values.append(val)

# --- Visualisation optimisée ---
plt.figure(figsize=(12, 8))

# On ajoute vmin/vmax pour ignorer les bruits de fond si nécessaire
# ou simplement laisser scatter gérer l'échelle
sc = plt.scatter(x_centers, y_centers, c=values, cmap='magma', s=8, alpha=0.8)

plt.colorbar(sc, label=f'Valeur (Index {INDEX_DONNEE})')
plt.xlabel('X (Coordonnées)')
plt.ylabel('Y (Coordonnées)')
plt.title(f'Heatmap 2D - Données de la colonne {INDEX_DONNEE}')

# Optionnel : zoomer sur la zone où il y a des données si vous avez beaucoup de vide
# plt.xlim(min(x_centers), max(x_centers)) 
plt.show()


####################################code visionage 1 ci-dessus###################
import numpy as np
import matplotlib.pyplot as plt

# 1. On s'assure que les listes sont prêtes
x_centers = []
y_centers = []
values = []

# 2. La boucle de remplissage (Crucial !)
# On utilise raw5 puisque c'est votre dictionnaire actuel
for obj_id, triangles in objet_complet.items():
    # Géométrie
    all_points = np.array(triangles).reshape(-1, 3)
    x_centers.append(np.mean(all_points[:, 0]))
    y_centers.append(np.mean(all_points[:, 1]))
    
    # Données : on prend le max de la liste pour éviter les colonnes de zéros
    valeurs_obj = raw5["Ei"][obj_id]
    values.append(max(valeurs_obj))

# 3. Vérification immédiate
print(f"Points extraits : {len(x_centers)}")

# 4. Affichage de la Heatmap
if len(x_centers) > 0:
    plt.figure(figsize=(12, 8))
    sc = plt.scatter(x_centers, y_centers, c=values, cmap='magma', s=10)
    plt.colorbar(sc, label='Intensité Max')
    plt.title('Heatmap de la Structure')
    plt.show()
else:
    print("Erreur : Les listes sont toujours vides. Vérifiez 'objet_complet'.")

   # Regardez les 5 premières listes de données
for i, (k, v) in enumerate(raw5["Ei"].items()):
    if i < 5: print(f"ID {k} : {v}") 

    
import matplotlib.pyplot as plt
import numpy as np

x_centers = []
y_centers = []
values = []

for obj_id, triangles in objet_complet.items():
    # 1. Géométrie : Calcul du centre
    all_points = np.array(triangles).reshape(-1, 3)
    x_centers.append(np.mean(all_points[:, 0]))
    y_centers.append(np.mean(all_points[:, 1]))
    
    # 2. Données : On prend la valeur maximale de la liste pour cet ID
    # Cela permet de capturer l'information peu importe l'index où elle se trouve
    liste_valeurs = raw5["Ei"][obj_id]
    values.append(max(liste_valeurs)) # Ou liste_valeurs[10] pour être spécifique

# --- Visualisation ---
plt.figure(figsize=(12, 8))

# Utilisation d'une échelle logarithmique si les écarts sont très grands
# ou d'un simple scatter avec une colormap contrastée
sc = plt.scatter(x_centers, y_centers, c=values, cmap='magma', s=12, edgecolors='none')
# Utilisation de 'hexbin' au lieu de 'scatter' pour lisser les lignes
plt.figure(figsize=(12, 8))
hb = plt.hexbin(x_centers, y_centers, C=values, gridsize=100, cmap='magma', reduce_C_function=np.max)
plt.colorbar(hb, label='Intensité lissée')
plt.title('Visualisation structurelle (Lissage par Hexagones)')
plt.show()

####
import matplotlib.pyplot as plt
import numpy as np

from pykrige.ok import OrdinaryKriging
import numpy as np
import matplotlib.pyplot as plt

# 1. Préparation d'une grille régulière pour l'interpolation
# On crée une grille 100x100 (ajustable) sur l'emprise de vos données
grid_x = np.linspace(min(x_centers), max(x_centers), 100)
grid_y = np.linspace(min(y_centers), max(y_centers), 100)

# 2. Exécution du Krigeage Ordinaire
# Note: On peut limiter à un sous-échantillon si c'est trop lent [::10]
OK = OrdinaryKriging(
    x_centers, 
    y_centers, 
    values, 
    variogram_model='linear', # 'gaussian' ou 'spherical' sont aussi possibles
    verbose=False, 
    enable_plotting=False
)

# 3. Calcul des valeurs sur la grille
z_grid, ss_grid = OK.execute('grid', grid_x, grid_y)

# 4. Affichage du résultat "lissé"
plt.figure(figsize=(12, 10))
plt.imshow(z_grid, extent=(min(x_centers), max(x_centers), min(y_centers), max(y_centers)), 
           origin='lower', cmap='magma', aspect='equal')

plt.colorbar(label='Intensité Krigée')
plt.title('Surface de Contraintes Lissé par Krigeage')
plt.show()



                

                
    