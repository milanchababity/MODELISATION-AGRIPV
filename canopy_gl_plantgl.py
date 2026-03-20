import math 
from openalea.caribu.CaribuScene import CaribuScene
from openalea.caribu.plantgl_adaptor import scene_to_cscene
from openalea.plantgl.all import *

""""
Fonction Box (Vector3(x,y,z))
Fonction Sphere(radius=)
Fonction TriangleSet(sommet, indice/sommet)

"""
#### function leaf creation 
## creation de triangle
def fonction_triangle_sol(x,y):
    triangle1 = [
        (0,0,0),
        (0,y,0),
        (x,0,0)
    ]
    triangle2=[
        (0,0,0),
        (0,-y,0),
        (x,0,0)
    ]
    sommet_1=()
    for n in range(len(triangle1)):
        sommet_1 =sommet_1+(n,)
    sommet_2=()
    for n in range(len(triangle2)):
        sommet_2=sommet_2+(n,)
    return [sommet_1],[sommet_2],triangle1,triangle2

##  coloration 
def color_leaf_tige(leaf_total, R, G, B):
    # On garde R, G, B comme des ENTIERS (int) pour Color3
    # Pas de division par 255 ici d'après ta signature C++ !
    couleur = Color3(int(R), int(G), int(B))
    """
    Shape(obj,Material(Color3(R,G,B)))
    """
    # On crée le matériau avec cette couleur
    vert_ble = Material(couleur) 
    material_color = []
    for obj in leaf_total:
        # Ordre CRITIQUE : 1. La géométrie (obj), 2. L'apparence (vert_ble)
        nouveau_shape = Shape(obj, vert_ble)
        material_color.append(nouveau_shape)  
    return material_color


###############################
def fonction_leaf_sym(x,y):
    sommet_a,sommet_b,triangle_a,triangle_b=fonction_triangle_sol(x,y)
    triangle_set_a=TriangleSet(triangle_a,sommet_a)
    triangle_set_b=TriangleSet(triangle_b,sommet_b)
    return triangle_set_a,triangle_set_b
"""
### def fonction inclinaison folaire
def fonction_leaf_incl(x,y,nb_leaf):
    triangle_g,triangle_d=fonction_leaf_sym(x,y)
    triangle=[triangle_g,triangle_d]
    leaf_total=[triangle_g,triangle_d]
    angle_leaf=2*math.pi/nb_leaf
    for i in range(1,nb_leaf):
        for j in triangle:
            leaf_int=AxisRotated(Vector3(0,0,1),i*angle_leaf,j)
            leaf_rel=Translated(Vector3(0,0,1/i),leaf_int)
            leaf_total.append(leaf_rel)
    return leaf_total
## fonction avec inclinaison 
"""
def fonction_leaf_incl(x, y, nb_leaf, incl_leaf, angle_incl,R=34, G=139, B=34):
    leaf_angle = math.radians(angle_incl)
    triangle_g, triangle_d = fonction_leaf_sym(x, y)
    # On définit nos triangles de base (soit inclinés, soit à plat)
    if incl_leaf == "yes":
        base_triangles = [
            AxisRotated(Vector3(0, 1, 0), -leaf_angle, triangle_g),
            AxisRotated(Vector3(0, 1, 0), -leaf_angle, triangle_d)
        ]
    else:
        base_triangles = [triangle_g, triangle_d]

    leaf_total = []
    angle_step = 2 * math.pi / nb_leaf
    h_step = 0.2  # Hauteur constante entre chaque étage
    
    # Une seule boucle propre
    for i in range(nb_leaf):
        current_angle = i * angle_step
        current_height = i * h_step
        
        for tri in base_triangles:
            # On combine Rotation et Translation
            # Astuce : On tourne d'abord, on déplace après
            obj = Translated(Vector3(0, 0, current_height),
                             AxisRotated(Vector3(0, 0, 1), current_angle, tri))
            leaf_total.append(obj)
    leaf_color=color_leaf_tige(leaf_total, R, G, B)
            
    return leaf_color

#### fonction de creation tige et ramification
def fonction_stem(haut_st,diam_st,nb_ramif=0,R=154, G=205, B=50):
    stem_f=Cylinder(radius=diam_st,height=haut_st)
    stem_obj=[stem_f]
    ### inclinaison des ramifications
    if nb_ramif > 0:
        stem_hor_g=AxisRotated(Vector3(0,1,0),math.pi/2,stem_f)
        stem_hor_d=AxisRotated(Vector3(0,0,1),math.pi,stem_hor_g)
        stem_1=AxisRotated(Vector3(0,1,0),math.radians(-45),stem_hor_g)
        stem_2=AxisRotated(Vector3(0,1,0),math.radians(45),stem_hor_d)
        stem_obj.append(stem_1)
        stem_obj.append(stem_2)
        for i in range(1,nb_ramif):
           stem_obj.append(Translated(Vector3(0,0,1/i),stem_1))
           stem_obj.append(Translated(Vector3(0,0,1/i),stem_2))
    stem_color=color_leaf_tige(stem_obj, R, G, B)
    return stem_color


## feuilles_rampantess
def leaf_prostree(x, y, nb_leaf, incl_leaf, angle_incl,nb_etage,R=34, G=139, B=34):
    leaf_angle = math.radians(angle_incl)
    triangle_g, triangle_d = fonction_leaf_sym(x, y)
    # On définit nos triangles de base (soit inclinés, soit à plat)
    if incl_leaf == "yes":
        base_triangles = [
            AxisRotated(Vector3(0, 1, 0), -leaf_angle, triangle_g),
            AxisRotated(Vector3(0, 1, 0), -leaf_angle, triangle_d)
        ]
    else:
        base_triangles = [triangle_g, triangle_d]

    leaf_total = []
    angle_step = 2 * math.pi / nb_leaf
    # Une seule boucle propre
    for i in range(nb_leaf):
        current_angle = i * angle_step
        for tri in base_triangles:
            # On combine Rotation et Translation
            # Astuce : On tourne d'abord, on déplace après
            obj = AxisRotated(Vector3(0, 0, 1), current_angle, tri)
            leaf_total.append(obj)
    leaf_etage=[]
    if nb_etage >0:
        step=0.2
        for etage in range(nb_etage):
            for leaf in leaf_total:
                ob=Translated(Vector3(0,0,etage*step),leaf)
                leaf_etage.append(ob)
        leaf_color=color_leaf_tige(leaf_etage, R, G, B)
        return leaf_color
    else:
        return color_leaf_tige(leaf_total, R, G, B)

################# multiplication des plantes

# Au lieu de passer 15 arguments, on passe un dictionnaire
params_plante = {
    "x":0.5,
    "y":0.02,
    "nb_leaf": 10,
    "angle_incl":35,
    "incl_leaf": "yes",
    "nb_etage":2,
    "R": 34, "G": 139, "B": 34,
    "haut_st":0.4,
    "diam_st":0.01,
    "nb_ramif":0,
    "ecart_pl":0.5,
    "ecart_rangee":0.5,
    "nb_plant_ligne":5,
    "nb_rangee":4,
    "R":34,
    "G":139,
    "B":34,
}
def semis_plante(params_plante):
    ### extraction des donnees params
    x=params_plante.get("x")
    y=params_plante.get("y")
    nb_leaf=params_plante.get("nb_leaf")
    incl_leaf=params_plante.get("incl_leaf")
    angle_incl=params_plante.get("angle_incl")
    nb_etage=params_plante.get("nb_etage")
    haut_st=params_plante.get("haut_st")
    diam_st=params_plante.get("diam_st")
    nb_ramif=params_plante.get("nb_ramif")
    ecart_pl=params_plante.get("ecart_pl")
    ecart_rangee=params_plante.get("ecart_rangee")
    nb_plant_ligne=params_plante.get("nb_plant_ligne")
    nb_rangee=params_plante.get("nb_rangee")
    R = params_plante.get("R")
    G = params_plante.get("G")
    B = params_plante.get("B")
    ###### lancement de fonction
    leaf_unit=leaf_prostree(x,y,nb_leaf,incl_leaf,angle_incl,nb_etage,R=34,G=139,B=34)
    stem_unit= fonction_stem(haut_st,diam_st,nb_ramif,R,G,B)
    offset_x=-(nb_plant_ligne-1)*ecart_pl/2
    offset_y=-(nb_rangee-1)*ecart_rangee/2
    leaf_total=[]
    stem_total=[]
    for i in range(nb_plant_ligne):
        for j in range(nb_rangee):
            pos_x = offset_x + (i * ecart_pl)
            pos_y = offset_y + (j * ecart_rangee)
            for leaf in leaf_unit:
                obj_leaf=Translated(Vector3(pos_x,pos_y,0),leaf.geometry)
                leaf_total.append(obj_leaf)
            for stem in stem_unit:
                obj_stem= Translated(Vector3(pos_x,pos_y,0),stem.geometry)
                stem_total.append(obj_stem)
    
    return color_leaf_tige(leaf_total,R=34,G=139,B=34),color_leaf_tige(stem_total,R=154, G=205, B=50)
                    
feuille,tige=semis_plante(params_plante)   
scene_1=Scene(feuille)
scene_2=Scene(tige)
scene_1.add(scene_2)
Viewer.display(scene_1)          
                    
    
    
    
            






