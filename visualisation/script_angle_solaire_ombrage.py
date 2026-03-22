
#################bloc de fonction####################
#1- Chargement des librairies
import numpy as np
import pandas as pd
from datetime import datetime
import math
import seaborn as sns
from scipy.optimize import newton
from scipy.optimize import bisect
from sympy import symbols,diff,nsolve
import random
import matplotlib.pyplot as plt
import recup_meteo
from recup_meteo import fonction_cvt_light



data_met={
    "start":"2026-01-01",
    "end":"2026-01-02",
    "tz":"Europe/Paris",
    "latitude":47.23,
    "longitude":3.30,
      
}
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
  return math.degrees(math.asin(alpha_s)) if math.asin(alpha_s) >0 else 0

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
  return math.degrees(math.atan2(sin_angle_az,cos_angle_az))


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
    hauteur_effec = hauteur_bas_panneaux +((largeur_panneau/2) * math.sin(math.radians(angle_d_inclinaison)))
  return hauteur_effec   

#            11- calcul de la longueur d'ombrage (equation 10)   
"""
calcul de la longueur de la projection d'ombrage 
la distance maximale entre deux panneaux 

""" 
## calcul de la longueur d'ombrage 
"""
il s'agit d'une fonction applicable aux panneaux orientés sud 
pour les panneaux orientés Est-ouest il faudrait appliquer une 
autre fonction 
la fonction appique la relation entre la tangente(alpha) et la hauteur des panneaux 

"""
def longueur_ombrage (angle_d_inclinaison,largeur_panneau,hauteur_bas_panneaux,angle_alpha):
  if angle_alpha > 1:
     tang_alpha = (math.tan(math.radians(angle_alpha)))
     if abs(tang_alpha)>0.001:
      long_ombrage = hauteur_effec(angle_d_inclinaison,largeur_panneau,hauteur_bas_panneaux)/tang_alpha
      return long_ombrage
     else:
      return None
  else:
    return None
     
# fonction de graphisme
def graphique (x,y,xlabel,ylabel,titre):
  import matplotlib.pyplot as plt
  plt.plot(x,y)
  plt.xlabel(str(xlabel))
  plt.ylabel(str(ylabel))
  plt.title(str(titre))
  plt.grid(True)
  plt.show()


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

# conversion hauteur du soleil en dégré 
data_meteo["hauteur_soleil_degre"]=data_meteo["hauteur_soleil"].apply(
  lambda j: j*180/(math.pi))
# suppression de hauteur 0
#data_meteo2= data_meteo
#data_meteo2 = data_meteo2[data_meteo2["hauteur_soleil"]>0]
#data_meteo=data_meteo2
#hauteur en degré

#calcul de l'angle azimutal 

data_meteo["angle_azimutal_rad"]=data_meteo.apply(
    lambda row: angle_azimutal(
        jour =row["day_of_year"],
        heure = row["heure"],
        lattitude_site=lattitude_site,
        longitude_ref=longitude_ref,
        longitude_site=longitude_site
    ),axis =1
)

#conversion de l'angle azimutal en degre
data_meteo["angle_azimutal_degre"]=data_meteo["angle_azimutal_rad"].apply(
  lambda j: j*180/(math.pi)
)
print(data_meteo.columns)
## filtration par angle azimutal en gardant que les prohections vers le sud 
#data_meteo=data_meteo[(data_meteo["hauteur_soleil_degre"] > 0)]

#data_meteo=data_meteo[data_meteo["angle_azimutal_degre"].between(-85,85)]
#########################

######################################################
#            Calcul d'ombrage 
# carracteristiques des panneaux 




##### FONCTION de caclul du minimum de la fonction
from scipy.optimize import newton
from scipy.optimize import bisect
from sympy import diff
import numpy as np
import math



A = np.sin(math.radians(alpha_sol))
B= np.sin(math.radians(beta_sol))

def fonctiion_f(x):
  return A *math.cos(x)+ B*math.sin(x) + 1

def fonction_fprime(x):
  return - A*math.sin(x) + B*math.cos(x)

test1 = newton(fonctiion_f,x0=0.1,fprime=fonction_fprime)
print(test1)

import numpy as np


root = bisect(fonctiion_f,-1,2)
R = np.sqrt(A**2 + B**2)
print("Amplitude maximale :", R)

print
############construction de la fonctio###########
"""
alpha_s = hauteur_du soleil
beta_s = angle azimutal 
alpha_p= angle azimutal du panneaux fixe = 0
beta_p = inclinaison du panneau à chercher par le minimum 
"""
def fonction_A(alpha_s,beta_s,alpha_p=0):
  return np.sin(alpha_s)*np.sin(beta_s)*np.sin(alpha_p)+np.cos(alpha_s)*np.cos(beta_s)*np.cos(alpha_p)

def fonction_B(beta_s):
  return np.sin(beta_s)

## Amplitude 
"""
Concernant la fonction cosinus et sinus = le maximum est calculé par le calcul 
d'Amplitude. le minimum est l'inverse du maximum (périodique)
"""
def calcul_de_minimum(alpha_s,beta_s,alpha_p=0):
  A_1=fonction_A(alpha_s,beta_s,alpha_p)
  B_1=fonction_B(beta_s)
  return -np.sqrt(A_1**2 + B_1**2)

def fonction_minimum_beta(x,alpha_s,beta_s,alpha_p):
  A= fonction_A(alpha_s,beta_s,alpha_p)
  B= fonction_B(beta_s)
  return (A*np.cos(x)) + (B*np.sin(x))

def calcul_beta_p (alpha_s,beta_s,alpha_p):
  A_1=fonction_A(alpha_s,beta_s,alpha_p)
  B_1=fonction_B(beta_s)
  beta_p=np.arctan2(-B_1,-A_1)
  return beta_p

print(data_meteo.columns)
### calcul avec les donnéees 
data_meteo["minimum_fonction"] = data_meteo.apply(
  lambda row: calcul_de_minimum(
    alpha_s=row["hauteur_soleil"],
    beta_s=row["angle_azimutal_rad"],
    alpha_p=0
  ),axis=1
)
data_meteo["beta_p_rad"] = data_meteo.apply(
  lambda row: calcul_beta_p(
    alpha_s=row["hauteur_soleil"],
    beta_s=row["angle_azimutal_rad"],
    alpha_p=0
  ),axis =1
)

data_meteo["beta_p_degre"]=data_meteo["beta_p_rad"].apply(
  lambda j: j*180/(math.pi)
)

from mpl_toolkits.mplot3d import Axes3D
#création de template figure
fig,axes = plt.subplots(2,1,figsize=(30,30))
fig1=sns.lineplot(data=data_meteo, x="fonction_panneaux",y="minimum_fonction", ax=axes[0],color="red")
fig3=sns.lineplot(data=data_meteo, x="heure",y="hauteur_soleil_degre", ax=axes[1],color="black")
fig2=sns.lineplot(data=data_meteo, x="heure",y="beta_p_degre",ax=axes[1], color="green")
plt.show()

fig1=sns.lineplot(data=data_meteo, x="fonction_panneaux",y="minimum_fonction")
fig3=sns.lineplot(data=data_meteo, x="heure",y="hauteur_soleil_degre")
plt.show()
#creation de l'axe 3D en rattachant à l'objet figure
ax=fig.add_subplot(111, projection="3d")
# projection sur la figure 3D
ax.plot(data_meteo["heure"],data_meteo["fonction_panneaux"],np.zeros(len(data_meteo["heure"])), color="red",label ="minimum de la fonction_panneau")
ax.plot(data_meteo["heure"],np.zeros(len(data_meteo["heure"])),data_meteo["beta_p_degre"], color="green",label="angle_beta du panneau")

# labelisation 
ax.set_xlabel("heure de la journée")
ax.set_ylabel("le minimum de la fonction [-1 production d'electricité maximale]")
ax.set_zlabel("l'inclinaison beta du panneau [se rapprocher de -1]")
ax.set_title("evolution de l'angle beta selon la hauteur du soleil pour atteindre le minimum de la fonction")

plt.show()



sns.lineplot(data=data_meteo, x="heure",y="minimum_fonction")
sns.lineplot(data=data_meteo,x="heure",y ="minimum_fonction")
plt.legend(True)
plt.show()
data_meteo["fonction_panneaux"] =data_meteo.apply(
  lambda row: fonction_minimum_beta(
    x=row["beta_p_rad"],
    alpha_s=row["hauteur_soleil"],
    beta_s=row["angle_azimutal_rad"],
    alpha_p=0
  ),axis=1
)

data_meteo=data_meteo.drop(["beta_p_rad","fonction_panneaux"],axis=1)
print(data_meteo.columns)
data_meteo= data_meteo.drop(["fonction_panneaux"],axis=1)
data_meteo["angle_beta_s_degre"]=data_meteo.apply

# fonction à calculer le minimum
def fonction_sin (x):
  return ((math.cos(x)* ((math.sin(alpha_s)*math.sin(beta_s)*math.sin(alpha_p))+(math.cos(alpha_s)*math.cos(beta_s)*math.cos(alpha_p))))+ math.sin(x)* math.sin(beta_s))-1


print(data_meteo.columns)



test_2 = bisect(fonction_sin, 1,2)
print(test_2)

x= fonction_sin(test_2)
print(x)

data_meteo_azimut= data_meteo[data_meteo["angle_azimutal_degre"].between(-90,90)]
import matplotlib.pyplot as plt
import seaborn as sns
print(data_meteo_azimut)

fig,axs=plt.subplots(2,1,figsize=(30,20))
sns.lineplot(data=data_meteo_azimut,x="Date",y="angle_azimutal_degre",ax=axs[0])
sns.lineplot(data=data_meteo,x="Date",y="angle_azimutal_degre",ax=axs[1])
plt.show()

data_meteo.groupby(data_meteo["Date"].dt.month)["angle_azimutal_degre"].describe()
data_meteo[
    (data_meteo["Date"].dt.month == 1) &
    (data_meteo["angle_azimutal_degre"].between(-90,90))
]

jan_fevr=data_meteo[data_meteo["Date"].between("2026-01-01","2026-01-02")]
jan_fevr=jan_fevr[jan_fevr["hauteur_soleil_degre"]>0]
print(jan_fevr.columns)
## calcul avec Pvlib
import pandas as pd
import pvlib
lattitude_site= 47.23
longitude_site= 3.30
longitude_ref =0
timezone="Europe/Paris"

times = pd.date_range("2026-01-01","2026-01-02",freq="1h",tz=timezone)
print(times)

# Calcul solar position 
solar_position =pvlib.solarposition.get_solarposition(
  times,
  lattitude_site,
  longitude_site
)

solara_pos_pos =solar_position[solar_position["elevation"]>0]
jan_fevr["angle_azimutal_degre"]=jan_fevr["angle_azimutal_rad"].apply(
  lambda j: j*180/np.pi
)
solara_pos_pos=solara_pos_pos.reset_index()
solara_pos_pos.rename(columns={"index":"date_heure"},inplace=True)
solara_pos_pos["azimuth_sud"]=solara_pos_pos["azimuth"]-180

print(jan_fevr)
solar_position=solar_position.reset_index()
solar_position.rename(columns={"index":"date_heure"},inplace=True)
print(jan_fevr.columns)

##################
sns.lineplot(data=solara_pos_pos,x="date_heure",y="azimuth_sud")
sns.lineplot(data=jan_fevr,x="Date",y="angle_azimutal_degre")
plt.show()
solara_pos_pos =solara_pos_pos[solara_pos_pos["azimuth_sud"].between(-85,85)]
jan_fevr=jan_fevr[jan_fevr["angle_azimutal_degre"].between(-85,85)]
print(solara_pos_pos)
print(jan_fevr)


###### calcul du minimum de la fonction avec les sorties de pvLib
import pandas as pd
import pvlib
lattitude_site= 47.23
longitude_site= 3.30
longitude_ref =0
timezone="Europe/paris"
data_brute = pd.date_range("2026-01-01","2026-12-31",freq="1h",tz=timezone)
print(data_brute)

## calcul hauteur solaire 
data_meteo_pv= pvlib.solarposition.get_solarposition(data_brute,latitude=lattitude_site,longitude=longitude_site)
data_meteo_pv=data_meteo_pv.reset_index()
data_meteo_pv.rename(columns={"index":"date_heure"})

data_meteo_pv=data_meteo_pv[data_meteo_pv["elevation"]>0]
data_meteo_pv["azimuth_sud"]=data_meteo_pv["azimuth"].apply(
  lambda j: j-180
)
data_meteo_pv=data_meteo_pv.reset_index()
data_meteo_pv.rename(columns={"index":"date_heure"},inplace=True)

data_meteo_pv=data_meteo_pv[data_meteo_pv["azimuth_sud"].between(-85,85)]

plt.plot(data_meteo_pv["date_heure"],data_meteo_pv["elevation"])


### calcul d'ombrage 

# calcul d'ombrage 1
data_meteo_pv["longeur_d_ombrage_30_3.95"]=data_meteo_pv.apply(
  lambda row: longueur_ombrage(
    angle_alpha = row["elevation"],
    angle_d_inclinaison=30,
    largeur_panneau=3.47,
    hauteur_bas_panneaux=3.95
  ),axis =1 
)

#calcul d'ombrage 2
data_meteo_pv["longeur_d_ombrage_30_3.80"]=data_meteo_pv.apply(
  lambda row: longueur_ombrage(
    angle_alpha = row["elevation"],
    angle_d_inclinaison=30,
    largeur_panneau=3.47,
    hauteur_bas_panneaux=3.80
  ),axis =1 
)

#graphique calcul d'ombrage 3 
data_meteo_pv["longeur_d_ombrage_10_3.95"]=data_meteo_pv.apply(
  lambda row: longueur_ombrage(
    angle_alpha = row["elevation"],
    angle_d_inclinaison=10,
    largeur_panneau=3.47,
    hauteur_bas_panneaux=3.95
  ),axis =1 
)
# calcul d'ombrage 4
data_meteo_pv["longeur_d_ombrage_10_3.80"]=data_meteo_pv.apply(
  lambda row: longueur_ombrage(
    angle_alpha = row["elevation"],
    angle_d_inclinaison=10,
    largeur_panneau=3.47,
    hauteur_bas_panneaux=3.80
  ),axis =1 
)

###### visulation des données avec seaborn

plt.figure(figsize=(10,6))

plt.plot(data_meteo_pv["elevation"],
         data_meteo_pv["longeur_d_ombrage_30_3.95"],
         label="longueur d'ombrage [alpha =30,hauteur de poteau =3.95]")

plt.plot(data_meteo_pv["elevation"],
         data_meteo_pv["longeur_d_ombrage_30_3.80"],
         label="longueur d'ombrage [alpha =30,hauteur de poteau =3.80]")

plt.plot(data_meteo_pv["elevation"],
         data_meteo_pv["longeur_d_ombrage_10_3.95"],
         label="longeur d'ombrage [alpha =10,hauteur de poteau =3.95]")

plt.plot(data_meteo_pv["elevation"],
         data_meteo["longeur_d_ombrage_10_3.80"],
         label="longeur d'ombrage [alpha =10,hauteur de poteau =3.80]")

plt.axhline(y=11,color="red",linestyle="--")
plt.axhline(y=18,color="black",linestyle="--")
plt.legend(loc="upper right",fontsize=12,frameon=True,shadow=True)
plt.xlabel("Hauteur du soleil degre (angle solaire)")
plt.ylabel("Portée de l'ombre (mètre)")
plt.grid(True)
plt.show()

#### fonction minimum

def fonction_A(alpha_s,beta_s,alpha_p=0):
  return np.sin(alpha_s)*np.sin(beta_s)*np.sin(alpha_p)+np.cos(alpha_s)*np.cos(beta_s)*np.cos(alpha_p)

def fonction_B(beta_s):
  return np.sin(beta_s)

def calcul_de_minimum(alpha_s,beta_s,alpha_p=0):
  A_1=fonction_A(alpha_s,beta_s,alpha_p)
  B_1=fonction_B(beta_s)
  return -np.sqrt(A_1**2 + B_1**2)

def fonction_minimum_beta(x,alpha_s,beta_s,alpha_p):
  A= fonction_A(alpha_s,beta_s,alpha_p)
  B= fonction_B(beta_s)
  return (A*np.cos(x)) + (B*np.sin(x))

def calcul_beta_p (alpha_s,beta_s,alpha_p):
  A_1=fonction_A(alpha_s,beta_s,alpha_p)
  B_1=fonction_B(beta_s)
  beta_p=np.arctan2(-B_1,-A_1)
  return beta_p

def calcul_beta_o(alpha_s,beta_s,alpha_p,tol=1e-12):
  A_1=fonction_A(alpha_s,beta_s,alpha_p)
  B_1=fonction_B(beta_s)
  if abs(A_1) < tol:
    beta_p_o=0
  elif B_1 == 0 and A_1!=0:
    if A_1 >0 :
      beta_p_o = np.pi/2
    else:
      beta_p_o=-np.pi/2
  else:
    beta_p_o = np.arctan(-A_1/B_1)
  return beta_p_o
  
from scipy.optimize import bisect
from scipy.optimize import newton

######################calcul 
data_meteo_pv["minimum_theo"]=data_meteo_pv.apply(
  lambda row: calcul_de_minimum(
    alpha_s=np.radians(row["elevation"]),
    beta_s=np.radians(row["azimuth_sud"]),
    alpha_p=0
  ),axis=1
)

data_meteo_pv["beta_p_rad"]=data_meteo_pv.apply(
  lambda row: calcul_beta_p(
    alpha_s=np.radians(row["elevation"]),
    beta_s=np.radians(row["azimuth_sud"]),
    alpha_p=0
  ),axis=1
)
data_meteo_pv["beta_p_degre"]=data_meteo_pv["beta_p_rad"]*180/np.pi

data_meteo_pv["fonction_minimum"]=data_meteo_pv.apply(
  lambda row: fonction_minimum_beta(
    x=row["beta_p_rad"],
    alpha_s=np.radians(row["elevation"]),
    beta_s=np.radians(row["azimuth_sud"]),
    alpha_p=0
  ),axis=1
)

data_meteo_pv["heure"]=data_meteo_pv["date_heure"].dt.hour
plt.plot(data_meteo_pv["minimum_theo"],data_meteo_pv["heure"])
plt.show()

alpha_s=np.radians(30)
beta_s=np.radians(-5)
alpha_p=0
### Equation =0 
def fonction_A(alpha_s,beta_s,alpha_p=0):
  return np.sin(alpha_s)*np.sin(beta_s)*np.sin(alpha_p)+np.cos(alpha_s)*np.cos(beta_s)*np.cos(alpha_p)

def fonction_B(beta_s):
  return np.sin(beta_s)

def fonction_x (x,alpha_s,beta_s,alpha_p=0):
  A = fonction_A(alpha_s,beta_s,alpha_p)
  B=fonction_B(alpha_p)
  return (A*np.cos(x))+(B*np.sin(x))

def prime_zero (alpha_s,beta_s,alpha_p):
  A=fonction_A(alpha_s,beta_s,alpha_p)
  B=fonction_B(alpha_p)
  return np.atan(-A/B)
