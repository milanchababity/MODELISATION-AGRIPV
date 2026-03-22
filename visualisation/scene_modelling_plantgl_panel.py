#### importation des modules #############################
import math 
import os.path
import numpy as np
from openalea.caribu.CaribuScene import CaribuScene
from openalea.caribu.plantgl_adaptor import scene_to_cscene
from openalea.plantgl.all import *
import recup_meteo
from openalea.caribu.visualisation.saveImage import saveImage
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap,ListedColormap
from recup_meteo import coordinate_extraction
from recup_meteo import fonction_cvt_light,calcul_azimut_elev,separate_date_hour,coordon_x_y_z,coordinate_extraction,z_caribu

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
    "longueur_sol":12,
    "largeur_sol":18,
    "epaisseur_sol":0.01,
}

def maillage_centre_sol(params_sol):
        # Parametres d'entree
    resolution_p=params_sol.get("resolution_p")
    longueur_sol=params_sol.get("longueur_sol")
    largeur_sol=params_sol.get("largeur_sol")
    epaisseur_sol=params_sol.get("epaisseur_sol")
        # 1. Résolution
    step_x = resolution_p
    step_y = resolution_p
        # 2. Calcul du nombre de carreaux
    nb_carre_sol_x = math.ceil(longueur_sol / step_x)
    nb_carre_sol_y = math.ceil(largeur_sol / step_y)
    
        # 3. Définition du pixel (légère épaisseur pour Caribu)
    carreau_geom = Box(resolution_p, resolution_p,epaisseur_sol)
    
        # initiation de maillage au sol 
    maillage_soil = []
        # --- CENTRAGE DU SOL ---
    # On calcule le décalage pour le sol
    offset_s_x = -((nb_carre_sol_x - 1) * step_x) / 2
    offset_s_y = -((nb_carre_sol_y - 1) * step_y) / 2
    for i in range(nb_carre_sol_x):
            for j in range(nb_carre_sol_y):
                pos_x = offset_s_x + (i * step_x)
                pos_y = offset_s_y + (j * step_y)
            # On place le sol légèrement sous Z=0 pour éviter les conflits
                temp_2 = Shape(Translated(Vector3(pos_x, pos_y, -0.005), carreau_geom))
                maillage_soil.append(temp_2)
    return maillage_soil


# maillage du panneau en rectangulaire 
def maillage_panneau(longueur_p,largeur_p,resolution_p=0.001):
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


sky_po=calcul_azimut_elev(data_met)
sky_po=separate_date_hour(sky_po)
sky_po=coordon_x_y_z(sky_po)
sky_po=coordinate_extraction(sky_po)
light_final=z_caribu(sky_po,1)
print(len(sky_po))

light_car=recup_meteo.selection(10,light_final)
print(len(light_car))

light_1=[light_car[1]]
light_2=[light_car[2]]
light_3=[light_car[3]]
light_4=[light_car[4]]
light_5=[light_car[5]]


#### Fragmentation de données 
panneau = type_panneau_orient(params=params_panel)
scene_panel=Scene(panneau)
Viewer.display(scene5)



sol =maillage_centre_sol(params_sol=params_sol) 
socle =Scene(sol)
scene_panel.add(socle) 
   

cs1= CaribuScene(scene_panel,light=light_1)
raw1,agr1=cs1.run(simplify=True,infinite=False)
scene1,value =cs1.plot(raw1["Ei"],0,1,0.2,display=True)
 
cs2= CaribuScene(scene_panel,light=light_2)
raw2,agr2=cs2.run(simplify=True,infinite=False)
scene2,value2 =cs2.plot(raw1["Ei"],0,1,0.2,display=True)

cs3= CaribuScene(scene_panel,light=light_3)
raw3,agr3=cs3.run(simplify=True,infinite=False)
scene3,value3 =cs3.plot(raw1["Ei"],0,1,0.2,display=True)

cs4= CaribuScene(scene_panel,light=light_4)
raw4,agr4=cs4.run(simplify=True,infinite=False)
scene4,value4 =cs4.plot(raw1["Ei"],0,1,0.2,display=True)

cs5= CaribuScene(scene_panel,light=light_5)
raw5,agr5=cs5.run(simplify=True,infinite=False)
scene5,value5 =cs5.plot(raw5["Ei"],0,1,0.2,display=True)
testa=cs5.scene.keys()
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


    
    

    


                

                
    