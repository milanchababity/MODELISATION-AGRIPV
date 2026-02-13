
#################bloc de fonction####################
#1- Chargement des librairies
import numpy as np
import pandas as pd
from datetime import datetime
import math

#            2- fonction d'importation de données (dates et heures)##
"""
Cette fonction permet d'automatiser l'import des données datées et 
de stocker date, heure, année colonne par colonne
"""
def importation_donnees (fichier):
  donnees_meteo = pd.read_csv(fichier,encoding="utf-8") # importation du fihcier csv avec le module pd
   ## conversion en date_time
  donnees_meteo["Date"]= pd.to_datetime(donnees_meteo["date_heure"])
   #conversion en jour de l'année
  donnees_meteo["day_of_year"]=donnees_meteo["Date"].dt.dayofyear
   #conversion en heure 
  donnees_meteo["heure"]=donnees_meteo["Date"].dt.hour
  return donnees_meteo
    
#             3- fonction de calcul de declinaison solaire (equation 1)
"""
Cette fonction permet  de calculer la déclinaison solaire 
l'angle entre le plan equatoriale et le rayonnement solaire 
"""
def declinaison_solaire(jour):
   return math.radians(23.45 * (math.sin(2*math.pi*(jour+284)/365))) 

#         4- fonction de calcul de la durée du jour (equation 2)
"""
cette fonction permet de calculer la durée du jour durant toute l'année
selon la saison, elle varie
elle depend dela declinaison solaire, le jour et la lattitude

"""
def duree_du_jour(jour, lattitude_site):
  alpha= declinaison_solaire(jour)
  phie = math.radians(lattitude_site)
  omega = math.acos(-math.tan(phie)* math.tan (alpha)) 
  duree =(2* 24 * omega)/(2 * math.pi) 
  return duree

#            5-fonction de calcul de l'equation temporelle (equation 3)
"""
Cette fonction permet de calculer l'ajustement temporel selon 
la lattitute et longitude
"""
def equation_ajust(jour):
  return (2 * math.pi*(jour-81)/365)

def equation_temp(jour):
    ajust = equation_ajust(jour)
    return(7.53 * (math.cos(ajust))) + (1.5*(math.sin(ajust)))-(9.87 * math.sin(2*ajust)) # 
#equation du temps Kalogorou il existe aussi la méthode de DUffie et Beckman
 

  ##        6- fonction temps solaire vrai (equation 4) 
"""
Calcul du temps solaire vrai
decalage entre l'heure solaire et l'heure moyenne des montres 
"""
def temps_solaire_vrai(jour,heure,longitude_ref,longitude_site):
  eqt = equation_temp(jour)/60 # conversion en minute en heure 
  tsv = heure + ((longitude_ref - longitude_site)/15)+ eqt
  return tsv

##         7- fonction de calcul d'angle horaire en radian (equation 5)
"""
Cette fonction permet de calculer l'angle horaire par rapport 
au meridien de référence

"""
def angle_horaire(jour,heure,longitude_ref,longitude_site):
  temps_solaire = temps_solaire_vrai(jour, heure,longitude_ref, longitude_site)
  return math.pi/12 * (temps_solaire-12)

###        8-fonction de calcul de hauteur du soleil (equation 6)
"""
calcul de la hauteur angulaire du soleil (donnée à calculer)
"""
def hauteur_soleil(jour,heure,lattitude_site,longitude_ref, longitude_site):
  gamma = declinaison_solaire(jour)
  phie= math.radians(lattitude_site)
  angle_h = angle_horaire(jour, heure, longitude_ref,longitude_site)
  alpha_s= (math.sin(gamma) * math.sin(phie)) + (math.cos(gamma)* math.cos(phie)*math.cos(angle_h))
  return math.asin(alpha_s) if math.asin(alpha_s) >0 else 0

##          9 - fonction de calcul de l'angle azimuthal (equation 7)
"""
fonction de calcul de l'angle azimutal
"""
def angle_azimutal(jour,heure,lattitude_site,longitude_ref,longitude_site):
  gamma = declinaison_solaire(jour)
  angle_h = angle_horaire(jour,heure,longitude_ref,longitude_site)
  hauteur = hauteur_soleil(jour,heure,lattitude_site,longitude_ref,longitude_site)
  sin_angle_az = math.cos(gamma)* math.sin(angle_h)/(math.cos(hauteur))
  cos_angle_az = (math.sin(hauteur)*math.sin(lattitude_site)-math.sin(gamma))/(math.cos(hauteur)*math.cos(lattitude_site))
  return math.atan2(sin_angle_az,cos_angle_az)

##          10 - fonction de calul de la hauteur maximale (equation 8)
"""
La hauteur effective depend de la disposition du panneau
si le panneau est en position horizontal = angle d'inclinaiso =0
hauteur effective= hauteur du pieux, sinon, il faudrait calculer la longeur de 
l'inclinaison

_summary_
"""
def hauteur_effec (angle_d_inclinaison,largeur_panneau,hauteur_bas_panneaux):
  if angle_d_inclinaison == 0:
    hauteur_effec= hauteur_bas_panneaux
  else:
    hauteur_effec = hauteur_bas_panneaux +(largeur_panneau * math.sin(math.radians(angle_d_inclinaison)))
  return hauteur_effec   


#            11- calcul de la longueur d'ombrage (equation 10)   
"""
calcul de la longueur de la projection d'ombrage 
la distance maximale entre deux panneaux 

""" 
def longueur_ombrage (angle_d_inclinaison,largeur_panneau,hauteur_bas_panneaux,angle_alpha):
   long_ombrage = hauteur_effec(angle_d_inclinaison,largeur_panneau,hauteur_bas_panneaux)/(math.tan(math.radians(angle_alpha)))
   return long_ombrage

################################################bloc d'execution###################
lattitude_site= 47.23
longitude_site= 3.30
longitude_ref =0
#            Etape 1 # importation de données
data_meteo = importation_donnees("dates_2026.csv")

#            Etape 2 calcul de declinaison solaire 
data_meteo ["declinaison_solaire"]= data_meteo["day_of_year"].apply(
    lambda j:declinaison_solaire(j))
                                   
           #Etape 3 calcul de la durée du jour
data_meteo["duree_du_jour"]=data_meteo["day_of_year"].apply(
    lambda j: duree_du_jour(j,lattitude_site))
 
data_meteo["equation_ajust"]=data_meteo["day_of_year"].apply(
    lambda j: equation_ajust(j))

data_meteo["equation_du_temps"]=data_meteo["day_of_year"].apply(
    lambda j: equation_temp(j))

data_meteo["temps_solaire_vrai"]=data_meteo.apply(
    lambda row: temps_solaire_vrai(
        jour=row["day_of_year"],
        heure= row["heure"],
        longitude_ref=longitude_ref,
        longitude_site=longitude_site), axis=1)
print(data_meteo)

data_meteo["angle_horaire"]=data_meteo.apply(
    lambda row: angle_horaire(
        jour=row["day_of_year"],
        heure=row["heure"],
        longitude_ref=longitude_ref,
        longitude_site=longitude_site
    ),axis =1
)
## calcul de hauteur solaire en radians
data_meteo["hauteur_soleil"]=data_meteo.apply(
    lambda row: hauteur_soleil(
        jour=row["day_of_year"],
        heure= row["heure"],
        lattitude_site=lattitude_site,
        longitude_ref=longitude_ref,
        longitude_site=longitude_site
    ), axis =1
)


data_meteo["angle_azimutal_rad"]=data_meteo.apply(
    lambda row: angle_azimutal(
        jour =row["day_of_year"],
        heure = row["heure"],
        lattitude_site=lattitude_site,
        longitude_ref=longitude_ref,
        longitude_site=longitude_site
    ),axis =1
)
####### calcul de l'angle azimutal en radian [0 à 2pi]
data_meteo["angle_azimutal_rad_pv"]=data_meteo["angle_azimutal_rad"].apply(
    lambda j : (j+math.pi)%(2*math.pi)
)
#### converstion d'angle azimutal rad en degré 
data_meteo["angle_azimutal_pv_degre"]=data_meteo["angle_azimutal_rad_pv"].apply(
    lambda j: j*180/(math.pi)
)
## calcul de la hauteur du soleil en degre 
data_meteo["hauteur_soleil_degre"]=data_meteo["hauteur_soleil"].apply(
    lambda j: j*180/(math.pi)
)

print(data_meteo)
# 
import matplotlib.pyplot as plt
plt.plot(data_meteo["Date"],data_meteo["angle_azimutal_pv_degre"])
plt.xlabel("day of year")
plt.ylabel("azimutale du soleil en degré")
plt.title("angle azimutale solaire ")
plt.show()
print(data_meteo)
for ligne in data_meteo["hauteur_soleil_degre"]:
    print(ligne)

import matplotlib.pyplot as plt
plt.plot(data_meteo["Date"],data_meteo["angle_azimutal"] )

plt.plot(data_meteo["Date"],data_meteo["hauteur_soleil_degre"])
plt.xlabel("hour et heure")
plt.ylabel("hauteur du soleil en degré")
plt.title("Evolution de la hauteur du soleil selon le jour et l'année")
plt.show()




######################################################

#            Calcul d'ombrage 
hauteur_bas_panneau = 3
hauteur_haut_panneau =3.2
largeur_panneau=1
longeur_panneau =2
angle_d_inclinaison=30
angle_alpha=
angle_azimut= 

del data_meteo["longeur_ombrage"]
print(data_meteo)


plt.plot(data_meteo["Date"],data_meteo["longeur_ombrage"] )
plt.xlabel("hour et heure")
plt.ylabel("portée d'ombrage")
plt.title("longeur d'ombrage à l'année")
plt.show()
