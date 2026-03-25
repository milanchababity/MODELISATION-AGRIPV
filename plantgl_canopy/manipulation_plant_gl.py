import math 
from openalea.caribu.CaribuScene import CaribuScene
from openalea.caribu.plantgl_adaptor import scene_to_cscene
from openalea.plantgl.all import *

##################################### code marche 
def creation_panneau(longueur_p, largeur_p, epaisseur_p, hauteur_p, angle_p):
    angle_radian = math.radians(angle_p)
    # 1. Création de la boîte
    # On divise l'épaisseur par 2 pour que le centre Z soit correct
    dimension_p = Box(Vector3(longueur_p/2, largeur_p/2, epaisseur_p/2))
    
    # 2. ALIGNEMENT : On déplace le panneau pour que son bord "HAUT" soit à Y=0
    # Puisque la Box fait 'largeur_p', son bord est à largeur_p/2 du centre.
    decalage_bord = Translated(Vector3(0, -largeur_p/2, 0), dimension_p)
    
    # 3. INCLINAISON : Le pivot (0,0,0) est maintenant sur le bord du panneau
    inclinaison = AxisRotated(Vector3(1,0,0), angle_radian, decalage_bord)
    
    # 4. ÉLÉVATION
    return Translated(Vector3(0, 0, hauteur_p), inclinaison)

def type_panneau_orient(geometry, orientation, type_panneau):
    # Avec la correction ci-dessus, le bord haut est TOUJOURS à Y=0
    # Donc Translation = 0 ! Les panneaux sont déjà prêts à être joints.
    
    if type_panneau == "chapeau":
        # Le versant opposé est juste une rotation de 180° du premier
        geometry_int = AxisRotated(Vector3(0,0,1), math.pi, geometry)
        geoms_locales = [geometry, geometry_int]
        
        # Rotation globale (Sud, Nord, Est, Ouest)
        mapping = {"sud": 0, "nord": math.pi, "est": -math.pi/2, "ouest": math.pi/2}
        angle_rot = mapping.get(orientation, 0)
        
        return [AxisRotated(Vector3(0,0,1), angle_rot, g) for g in geoms_locales]
    
    return [geometry] # Cas "normal" simplifié pour l'exemple


#### coloration des panneaux 
def couleur_panneau (geometry,R,G,B):

    panneau_colore=Shape(geometry,Material(Color3(R,G,B)))
    return panneau_colore

####### generer un objet shape et colorer à partir des donnees de sorties geometriques
def fonction_scene (geometry,R,G,B):
    shapes = []
    for g in geometry:
        shapes.append(g)
    return shapes

### type et orientation des panneaux et ajouts des nombres et rangées des panneaux
def fonction_spatiale(shapes,ecart_p,ecart_rangee,nombre_p,nombre_rangee):
    panneau_tot = []
    panneau_scene =[]
    for panneau in range(nombre_p):
        for panel in shapes:
            panneau_tot.append(Translated(Vector3(0,panneau*ecart_p,0),panel))
    for rang in range(nombre_rangee):
        for pan in panneau_tot:
            panneau_scene.append(Translated(Vector3(rang*ecart_rangee,0,0),pan))
    return panneau_scene
        
## fonction maillage panneaux et sol
def maillage_sol(longueur_p,largeur_p,resolution_p,largeur_sol,longueur_sol):
    #1#resolution du maillages step_x*step_y
    step_x=resolution_p
    step_y=resolution_p
    #2 on calcule le nombre de carreaux
      ### pour les panneaux
    nb_carre_long= math.ceil(longueur_p/step_x)
    nb_carre_larg=math.ceil(largeur_p/step_y)
      ### pour la surface du sol
    nb_carre_sol_x=math.ceil(longueur_sol/step_x)
    nb_carre_sol_y=math.ceil(largeur_sol/step_y)

    # 3 on definit le pixel
    carreau_geom=Box(Vector3(resolution_p,resolution_p,0.001))

    ##############################
    maillage_panel=[]
    maillage_soil=[]
    ### creation maillage des panneaux
    for i in range (nb_carre_long):
        for j in range(nb_carre_larg):
            pos_x= i*step_x
            pos_y=j*step_y
            temp= Translated(Vector3(pos_x,pos_y,0),carreau_geom)
            maillage_panel.append(temp)
    ## creation maillage sol
    for i in range(nb_carre_sol_x):
        for j in range (nb_carre_sol_y):
            pos_x=i*step_x
            pos_y=j*step_y
            temp_2= Translated(Vector3(pos_x,pos_y,0),carreau_geom)
            maillage_soil.append(temp_2)
    return maillage_panel,maillage_soil            
            
pan,mail=maillage_sol(longueur_p =1.45,largeur_p=1.25,resolution_p=0.02,largeur_sol=6,longueur_sol=8)
socle= Scene(mail)


### test de création de panneau   
panneau = creation_panneau(longueur_p=1.75,largeur_p=1.5,epaisseur_p=0.05,hauteur_p=2,angle_p=45) # création de panneau 3D
geoms = type_panneau_orient(panneau,orientation="est",type_panneau="normal",largeur_p=1.5,angle_p=45) ## ajustement des orientations et types de strucutures 
fnc_scene=fonction_scene(geoms,51,8,34)
scene_final=fonction_spatiale(fnc_scene,ecart_p=2,ecart_rangee=6,nombre_p=4,nombre_rangee=4)
scenario_final=Scene(scene_final)
Viewer.display(scenario_final)
scenario_final.add(socle)
Viewer.display(scenario_final)

### 


###### test caribu
cs= CaribuScene(scenario_final)
raw,agr=cs.run(simplify=True,infinite=False)
print(raw.keys())
scene,values=cs.plot(raw["Ei"],0,1,0.2,display=False)
Viewer.display(scene)
    
Viewer.display(scene_final)      


### documentation sur caribu
"""
Trois fonction de calcul principal
Raycasting = calcul de prémier ordre (uniquement les rayonnement incidents)
Radiosite= calcul de tout ordre (incident et reflechie)
Radisity_mixte= avec une scene optimisee à l'infinie 
CaribuScene= objet classée qui sert de l'instance pour classer. Il s'agit de point d'entrée pour la plus part des utilisateurs 
   argument 1= scene importée de plantgl ou de maillage de triangle
   argument 2= optical propriété sous forme de dictionnaire { "id":{"reflectance":r,"transmittance":t}}
   argument 3= turtle / objet servant à carractériser la discréditation du ciel (direction de la lumière)
Les méthodes de la classe CaribuScene
   methode 1: run (sky=none or true) provenance du rayonnement,simplify=True pour simplification de la vitesse des calculs , infinite =true pour rendre la scène infinie
   
les fonctions de bas niveaux 
  Raycsting(triangles,materials,lights)
  Radiosity(traingles, materials,lights)
  
sky.GenSky(latitude, longitude,day,hour)= génère une distrubistion lumineuse sur un point précis à un moment donné
  
"""

from openalea.caribu.plantgl_adaptor import scene_to_cscene
### caribu test
scene_caribu=scene_to_cscene(scenario)
vertical_light=(100,(0,0,-1))
light= [vertical_light]
cs=CaribuScene(scenario)
raw,agr=cs.run(simplify=True,infinite=False)
print(raw,agr)
print(list(raw.keys())[:10])
scene,values = cs.plot(raw['default_value']['Ei'], 0, 1, 0.2,display=False)
### 
     
###### manipulation objet scene
"""
creation objet scene= Scene() si l'objet créer n'est pas listée= ajouter une liste
pour ajouter un objet dans la scene==> objet.add(objet2)
# combiner deux scene = scene_1 + scene_2
ajouter un objet dans une scene = scene.add(objet)

_summary_
"""
objet_1=Box(Vector3(1,0.5,2))
objet_2=Translated(Vector3(1,0,0),objet_1)
objet_3=Translated(Vector3(1,1,2),objet_2)

scene_1=Scene([objet_1])
scene_2=Scene([objet_3])
scene_totale=scene_1 + scene_2
scene_1.merge(scene_2)

### Création de scène visualisable dans plantGl 
# création de shape 

"""
Pour afficher dans Viewer.display, il faudrait que les geometries soient sous forme d'objet 
ou Scene
la manipulation se limite aux objets geometriques et par consequent, appliquer toutes les 
fonctions translation et rotation avant de convertir en shape

"""

panneau_nit= creation_panneau(longueur_p=1.75,largeur_p=1.5,epaisseur_p=0.05,hauteur_p=2,angle_p=20)
panneau_2=type_panneau_orient(panneau_nit,orientation="sud",type_panneau="chapeau",largeur_p=1.5,angle_p=20)
shapes = [Shape(g,Material(Color3(120,140,25))) for g in panneau_2]
scene = Scene(shapes)
Viewer.display(scene)


####################### panneaux centrés par rapport au plan x y et z
import math
from openalea.plantgl.all import *

def generer_champ_photovoltaique(nb_rangs, nb_p_par_rang, dist_rang, dist_p, geom_panneau):
    """
    Crée une grille de panneaux centrée sur (0,0,0).
    geom_panneau: peut être une Shape ou une liste de Shapes (le chapeau)
    """
    # 1. Calcul des dimensions totales pour le centrage
    largeur_totale_Y = (nb_rangs - 1) * dist_rang
    longueur_totale_X = (nb_p_par_rang - 1) * dist_p
    
    # Points de départ (moitié de la dimension en négatif)
    start_y = -largeur_totale_Y / 2
    start_x = -longueur_totale_X / 2
    
    champ = []
    
    for r in range(nb_rangs):
        y = start_y + (r * dist_rang)
        for p in range(nb_p_par_rang):
            x = start_x + (p * dist_p)
            
            # On crée une copie translatée de la géométrie de base
            # Si geom_panneau est une liste (cas du chapeau)
            if isinstance(geom_panneau, list):
                for g in geom_panneau:
                    champ.append(Shape(Translated(Vector3(x, y, 0), g)))
            else:
                champ.append(Shape(Translated(Vector3(x, y, 0), geom_panneau)))
                
    return champ

### maillage centrés aux sol 
def maillage_sol_centre(longueur_p, largeur_p, resolution_p, largeur_sol, longueur_sol):
    # 1. Résolution
    step_x = resolution_p
    step_y = resolution_p

    # 2. Calcul du nombre de carreaux
    nb_carre_long = math.ceil(longueur_p / step_x)
    nb_carre_larg = math.ceil(largeur_p / step_y)
    nb_carre_sol_x = math.ceil(longueur_sol / step_x)
    nb_carre_sol_y = math.ceil(largeur_sol / step_y)

    # 3. Définition du pixel (légère épaisseur pour Caribu)
    carreau_geom = Box(resolution_p, resolution_p, 0.001)

    maillage_panel = []
    maillage_soil = []

    # --- CENTRAGE DES PANNEAUX ---
    # On calcule le décalage pour que le bloc de maillage soit centré sur 0,0
    offset_p_x = -((nb_carre_long - 1) * step_x) / 2
    offset_p_y = -((nb_carre_larg - 1) * step_y) / 2

    for i in range(nb_carre_long):
        for j in range(nb_carre_larg):
            pos_x = offset_p_x + (i * step_x)
            pos_y = offset_p_y + (j * step_y)
            temp = Shape(Translated(Vector3(pos_x, pos_y, 0), carreau_geom))
            maillage_panel.append(temp)
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

    return maillage_panel, maillage_soil

# Test
pan, mail = maillage_sol_centre(1.45, 1.25, 0.1, 20,10) # Résolution 0.1 pour test rapide
print(type(pan))
### Panneaux maillé


# --- APPLICATION ---

# On crée le panneau de base avec tes fonctions précédentes
p_base = creation_panneau(2, 1, 0.05, 1, 30)
# On génère les deux versants (le chapeau)
chapeau_geoms = type_panneau_orient(p_base, orientation="sud",type_panneau="chapeau")

# On génère 3 rangées de 3 panneaux, parfaitement centrées
mon_champ = generer_champ_photovoltaique(3, 3, 5, 2.5, chapeau_geoms)



# Création de panneaux maillé 
def panneau_maille_centre(longueur_p,largeur_p,resolution_p,longueur_sol,largeur_sol,hauteur_p,dist_p,dist_rangee,nb_panneau,nb_rangee):
    panneau,sol=maillage_sol_centre(longueur_p, largeur_p, resolution_p, largeur_sol, longueur_sol)
    panneau_maille=[]
    for p in range(nb_panneau):
        for i in range(nb_rangee):
            pos_ligne=p*dist_p
            pos_rang= i*dist_rangee
            for panel in panneau:
                panneau_maille.append(Translated(Vector3(pos_ligne,pos_rang,hauteur_p),panel.geometry))
    return panneau_maille,sol



test_panneau,sol= panneau_maille_centre(longueur_p=1.75,largeur_p=1.50,resolution_p=0.1,longueur_sol=8,largeur_sol=12, hauteur_p=2.6,dist_p=2,dist_rangee=3.5,nb_rangee=3,nb_panneau=4)
centragege_panneau =generer_champ_photovoltaique(nb_rangs=3, nb_p_par_rang=4, dist_rang=3.5, dist_p=2, geom_panneau=test_panneau)
socle_x=Scene(sol)
tiso= Scene(centragege_panneau)   
tiso.add(socle_x)  
Viewer.display(tiso)   

cs= CaribuScene(tiso) 
raw,agg= cs.run(simplify="True",infinite=False)
scene,value=cs.plot(raw["Ei"],0,1,0.2,display=True)

            
