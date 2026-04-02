###############chargement et téléchargement des packages 
library(readr)
library(readxl)
library(dplyr)
library(tidyr)
library(car)
library(ggplot2)

## chargement des fichiers
file <-"C:/Users/mbabity/OneDrive - INRAE SharePoint SE/Projet de Thèse/These CIFRE/Traitement de données/Réservoir_hydrique densité apparente"
da_carto <- read.csv("densite_apparente_da.csv")
View(da_carto)


### traitement de données 
##############################importation des données GPS##################
coordonnees <- "C:/Users/mbabity/OneDrive - INRAE SharePoint SE/Projet de Thèse/These CIFRE/Traitement de données/densité_apparente_struc/Coordonnees geographiques"
conf1 <-read.csv(file.path(coordonnees, "config1.csv"))
conf2 <-read.csv(file.path(coordonnees, "config2.csv"))
conf3 <-read.csv(file.path(coordonnees, "config3.csv"))
conf4 <-read.csv(file.path(coordonnees, "config4.csv"))
conf5 <-read.csv(file.path(coordonnees, "config5.csv"))
Temoin <-read.csv(file.path(coordonnees, "Temoin.csv"))
names(Temoin)[names(Temoin) == "X_lamb"] <- "Est_lamb" 


############harmoniser les noms des colonnes##############################################################################
names(conf1) <- c("id", "conf", "Est_lamb", "Nord_lamb")
names(conf4) <- c("id", "conf", "Est_lamb", "Nord_lamb")

####################### combinaison des données###########################################################################
str(Temoin)
Cooord_geo_da <- rbind(conf1,conf2,conf3,conf4,conf5,Temoin)
View(Cooord_geo_da)

write.csv(Cooord_geo_da,"gps_point_da_avant_chantier.csv")

library(dplyr)
Cooord_geo_da <- Cooord_geo_da|> mutate(
  Id = NA,
  Provenance = NA,
  Ligne = row_number()
)
View(Cooord_geo_da)

############################################filtration de données##########################################################


# filtrer 
library(stringr)
da_carto_ligne <-da_carto |> mutate (Ligne = row_number())
con1.1 <-Cooord_geo_da|> filter(str_detect(conf,"conf1"))
con1.1

con2 <-da_carto_ligne|> filter(str_detect(Provenance,"da/conf2"))
con2

con2.1 <-Cooord_geo_da|> filter(str_detect(conf,"conf2"))
con2.1

con3 <-da_carto_ligne|> filter(str_detect(Provenance,"da/conf3"))
con3

con3.1 <-Cooord_geo_da|> filter(str_detect(conf,"conf3")
)
con3.1

con4 <-da_carto_ligne|> filter(str_detect(Provenance,"da/conf4"))
con4

con4.1 <-Cooord_geo_da|> filter(str_detect(conf,"conf4"))
con4.1


con5 <-da_carto_ligne|> filter(str_detect(Provenance,"da/conf5"))
con5

tem <-Cooord_geo_da|> filter(str_detect(conf,"conf5"))
con5.1


tem <-da_carto_ligne|> filter(str_detect(Provenance,"da/Tem")
)
tem

tem.1 <-Cooord_geo_da|> filter(str_detect(conf,"tem")
)
tem.1
#########################################################################################################


### Id configuration 1 #############################
Cooord_geo_da$Id[1] <-59740

Cooord_geo_da$Id[2] <-59737  

Cooord_geo_da$Id[3] <-59734   

Cooord_geo_da$Id[4] <-59731  

Cooord_geo_da$Id[5] <-59728 

Cooord_geo_da$Id[6] <-59739 

Cooord_geo_da$Id[7] <-59736 

Cooord_geo_da$Id[8] <-59733 

Cooord_geo_da$Id[9] <-59730 

### Id configuration 2 #############################
Cooord_geo_da$Id[10] <-59725

Cooord_geo_da$Id[11] <-59716  

Cooord_geo_da$Id[12] <-59713  

Cooord_geo_da$Id[13] <-59724  

Cooord_geo_da$Id[14] <-59721

Cooord_geo_da$Id[15] <-59715

Cooord_geo_da$Id[16] <-59718

Cooord_geo_da$Id[17] <-59722  

Cooord_geo_da$Id[18] <-59719


### Id configuration 3 #############################
Cooord_geo_da$Id[19] <-59710

Cooord_geo_da$Id[20] <-59707  

Cooord_geo_da$Id[21] <-59704  

Cooord_geo_da$Id[22] <-59701  

Cooord_geo_da$Id[23] <-59698

Cooord_geo_da$Id[24] <-59709

Cooord_geo_da$Id[25] <-59706

Cooord_geo_da$Id[26] <-59703  

Cooord_geo_da$Id[27] <-59700


### Id configuration 4 #############################
Cooord_geo_da$Id[28] <-59695

Cooord_geo_da$Id[29] <-59692 

Cooord_geo_da$Id[30] <-59689

Cooord_geo_da$Id[31] <-59686

Cooord_geo_da$Id[32] <-59683

Cooord_geo_da$Id[33] <-59694

Cooord_geo_da$Id[34] <-59691

Cooord_geo_da$Id[35] <-59688

Cooord_geo_da$Id[36] <-59685

### Id configuration 5 #############################
Cooord_geo_da$Id[37] <-59680

Cooord_geo_da$Id[38] <-59677

Cooord_geo_da$Id[39] <-59674

Cooord_geo_da$Id[40] <-59671

Cooord_geo_da$Id[41] <-59668

Cooord_geo_da$Id[42] <-59679

Cooord_geo_da$Id[43] <-59676

Cooord_geo_da$Id[44] <-59673

Cooord_geo_da$Id[45] <-59670


### Id Temoin #############################
Cooord_geo_da$Id[46] <-59755

Cooord_geo_da$Id[47] <-59752

Cooord_geo_da$Id[48] <-59749

Cooord_geo_da$Id[49] <-59746

Cooord_geo_da$Id[50] <-59743

Cooord_geo_da$Id[51] <-59754

Cooord_geo_da$Id[52] <-59751

Cooord_geo_da$Id[53] <-59748

Cooord_geo_da$Id[54] <-59745

View(Cooord_geo_da)

#### joindre les deux tableau sur la base de l'ID
Cartographie_da <- left_join (Cooord_geo_da,da_carto, by = "Id")

## Suppression des colonnes provenances.x, X et Ligne)
Cartographie_da <-Cartographie_da|> select (-Provenance.x,-X,-Ligne)
Cartographie_da

### enregistrement de données Cartographie en fichier csv
library(readr)
write.csv (Cartographie_da, "Données_brute_da_spatialisée_avant_chantier.csv")

### importation de données
Cartographie_da <-read.csv("Données_brute_da_spatialisée_avant_chantier.csv") #### chargement de fichier 
library(dplyr)
library(tidyr)
Densite_apparente_A_C <- Cartographie_da |> mutate (
  Densite_apparente = (masse_seche_valeur-Tare_valeur)/100) |> mutate (
    humidite_ponderale = (masse_fraiche_valeur - masse_seche_valeur)/(masse_seche_valeur-Tare_valeur)
  ) |> mutate (Humidite_volumique = humidite_ponderale * Densite_apparente) |>mutate (
    Porosite = (2.6 - Densite_apparente)/2.6
  )
View(Densite_apparente_A_C)

Densite_app_B_c <- Densite_apparente_A_C |> mutate(type = case_when(
  grepl("tem", Provenance.y, ignore.case = TRUE) ~ "Temoin",
  grepl ("conf1", Provenance.y, ignore.case = TRUE) ~ "Conf1",
  grepl ("conf2", Provenance.y, ignore.case = TRUE) ~ "Conf2",
  grepl ("conf3", Provenance.y, ignore.case = TRUE) ~ "Conf3",
  grepl ("conf4", Provenance.y, ignore.case = TRUE) ~ "Conf4",
  grepl ("conf5", Provenance.y, ignore.case = TRUE) ~ "Conf5"
))

stat <-shapiro.test(Densite_apparente_A_C$Densite_apparente)
stat1 <-shapiro.test(Densite_apparente_A_C$Humidite_volumique)
stat1
View (Densite_app_B_c)

################################## Graphique densite apparente ##############################
Densite_moyenne <- ggplot(Densite_app_B_c, aes(x=type, y = Densite_apparente, color =type)) +
  geom_boxplot() +
  geom_hline(yintercept = 1.45, color= "red", linetype ="dashed")

Densite_moyenne
################################# Traitement geostatistique##############################
library(gstat)
library(sp)
install.packages("geoR")
library(geoR)
class(Densite_apparente_A_C) ## verification du tableau
coordinates(Densite_apparente_A_C) <- ~ Est_lamb + Nord_lamb # indication des coordonnées spatiales
View(Densite_apparente_A_C)

################# tableau de données devient data frame classe spatiale 
class(Densite_apparente_A_C)

### afficher les apercus de coordonnées spatiales 
head(coordinates(Densite_apparente_A_C))

##calculation de score #########
install.packages("FactorCopulaModel")
library(FactorCopulaModel)
norma_reduite_da <-nscore(Densite_apparente_A_C$Densite_apparente)
Densite_apparente_A_C$N_Densite <- norma_reduite_da

summary(Densite_apparente_A_C$N_Densite)

##### VISUALISATION DE LA DISTRIBUTION DE LA DENSITE APPARENTE

install.packages("gridExtra")  # une seule fois
library(gridExtra)

cuts = c(1.1,1.2,1.3,1.4,1.5,1.6,1.7)

par (mfrow = c(2,2))
hist(Densite_apparente_A_C$Densite_apparente, main = "Densité apparente", xlab = "Densité apparente", nclass = 15)
plot(ecdf(Densite_apparente_A_C$Densite_apparente), main = "Densite apparente", xlab = "Densité apparente",ylab ="Cumulative probabilité") 
hist(Densite_apparente_A_C$N_Densite, main = "N[Densité apparente]", xlab = "N[Densité apparente]", nclass = 15)
plot(ecdf(Densite_apparente_A_C$N_Densite), main = "N[Densite apparente]", xlab = "N[Densité apparente]",ylab ="Cumulative probabilité") 

##### visualisation spatiale des donnnées 
bublle <-bubble(Densite_apparente_A_C,"Densite_apparente", fill =TRUE, maxsize = 1.5, main = "Densité apparente", identify = FALSE, xlab = "X (m)", ylab = "Y(m)")



ssplot <-spplot(Densite_apparente_A_C, "Densite_apparente", do.log = TRUE,# location map of porosity data
       key.space=list(x=.85,y=0.97,corner=c(-1,1)),cuts = cuts,
       scales=list(draw=T),xlab = "X (m)", ylab = "Y (m)",main ="Porosity (%)")

cutoff <- 100
width  <- 10



###### calcul de variogram omnidirectionnel###################################"
vg_map_densite<- variogram(
  N_Densite ~ 1,
  Densite_apparente_A_C,
  cutoff = 100,
  width = 10,
  map =TRUE
)
plot(
  vg_map_densite,
  main = "Semivariogram Map",
  max = 1.0
)


################## calcul de variogramm directionnel #########################

vg_dir_densite <- variogram(
  N_Densite ~ 1,
  Densite_apparente_A_C,
  alpha = c(0,45,90,135),
  cutoff =100,
  width = 10
)
vg_dir_densite
plot(vg_dir_densite, main = "Directional Variograms")

############################ construction de variogramme anisotrope#############
vg_aniso_dens <- vgm(
  psill = 1.25,
  model = "Exp",
  range = 90,
  nugget = 0.3,
  anis = c(45, 0.7)
)

vg_aniso_dens_fit <- fit.variogram(vg_dir_densite, model = vg_aniso_dens)
  
plot(vg_dir_densite, vg_aniso_dens_fit, main="Variogramme anisotrope ajusté")

vg_model <- vgm(
  psill = 1.25,
  model = "Sph",
  range = 90,
  anis = c(45, 0.7)
)
################ validation croisée##########################################
cv <- krige.cv(
  N_Densite ~ 1,
  Densite_apparente_A_C,
  model = vg_model,
  nfold = nrow(Densite_apparente_A_C)
)

mean(cv$residual)

#####################################Krigeage anisotrope ######################

############création de la grille spatiale #################
grd <- spsample(
  Densite_apparente_A_C,
  type = "regular",
  n = 5000
)

gridded(grd) <- TRUE

############################################ réalisation de Krigeage anisotrope####

krig <- krige(
  N_Densite ~ 1,
  Densite_apparente_A_C,
  grd,
  model = vg_model
)

str(krig)

###################################cartographie finale#########################
spplot(krig["var1.pred"], main = "Carte de densité estimée", col.regions = terrain.colors(90), scales = list(draw= TRUE))

###### cartographie avec les valeurs de la densité apparente normales à bonne echelle #########

## remise à la bonne echelle en mumtipliant par l'ecart-type et en rajoutant la moyenne
krig$pred_dens_ori <- krig$var1.pred * sd(Densite_apparente_A_C$Densite_apparente) + mean(Densite_apparente_A_C$Densite_apparente)

mean_res <- mean(cv$residual)       # moyenne des résidus
mean_z   <- mean(cv$zscore)         # moyenne des z-scores

### cartographie à bonne echelle
library(ggplot2)
library(lattice)
install.packages("latticeExtra")
library(latticeExtra)

# Calcul des coordonnées pour le coin supérieur gauche
x_text <- bbox(krig)[1,1] + 0.02 * (bbox(krig)[1,2] - bbox(krig)[1,1])
y_text <- bbox(krig)[2,2] - 0.02 * (bbox(krig)[2,2] - bbox(krig)[2,1])

# Création de la carte avec annotation
cartographie_predi <- spplot(
  krig["pred_dens_ori"],
  main = "Carte de densité estimée",
  col.regions = terrain.colors(90),
  scales = list(draw = TRUE)
) +
  layer(
    ltext(
      x = x_text, y = y_text,
      labels = paste0("Mean residual = ", round(mean_res, 3),
                      "\nMean Z-score = ", round(mean_z, 3)),
      cex = 0.8, font = 1, adj = c(0,1)# alignement en haut à gauche
    )
  )
cartographie_predi

## remise à bonne echelle de la variance ##############
krig$pred_var_ori <-krig$var1.var * sd(Densite_apparente_A_C$Densite_apparente)^2

#### cartographie de la variance ###################
cartorgaphie_var<-spplot(krig["pred_var_ori"], main = "Variance du krigeage", col.regions = terrain.colors(90), scales = list(draw =TRUE))
cartorgaphie_var1<-spplot(krig["var1.var"], main = "Variance du krigeage", col.regions = terrain.colors(90), scales = list(draw =TRUE))
cartorgaphie_var1


##" assemblage des cartes 
library(gridExtra)
grid.arrange(cartographie_predi,cartorgaphie_var,nrow=2)



mu <- mean(Densite_apparente_A_C$Densite_apparente, na.rm = TRUE)
sigma <- sd(Densite_apparente_A_C$Densite_apparente, na.rm = TRUE)

krig$densite_pred <- krig$var1.pred * sigma + mu
krig$densite_var <- krig$var1.var * sigma^2


########################### cartographie de la répartiotion de la densité apparente #############
carte_variabilite_Da <-spplot(
  krig["densite_pred"],
  main = "Carte de densité apparente estimée",
  col.regions = terrain.colors(100),
  xlab = "X (m)",
  ylab = "Y (m)",
  scales = list(draw = TRUE)
)
carte_variance_da <-spplot(
  krig["densite_var"],
  main = "Variance du krigeage (densité apparente)",
  xlab = "X (m)",
  ylab = "Y (m)",
  scales = list(draw = TRUE)
)

grid.arrange(carte_variabilite_Da,carte_variance_da, nrow = 2)

###########









library(gridExtra)
####### VISULATION DE LA DISTRIBUTION D'humidité du sol 
humidite_pond_norm <- nscore(Densite_apparente_A_C$humidite_ponderale)
humidite_vol_norm <- nscore(Densite_apparente_A_C$Humidite_volumique)

Densite_apparente_A_C$N_humidite_pond <-humidite_pond_norm
Densite_apparente_A_C$N_humidite_volu <-humidite_vol_norm

cut2 = c(0.20,0.25, 0.30,0.35,0.40,0.45, 0.50, 0.55)
par (mfrow = c(2,2))
hist(Densite_apparente_A_C$humidite_ponderale, main = "Humidité pondérale", xlab = "Humidité pondérale", nclass = 15)
plot(ecdf(Densite_apparente_A_C$humidite_ponderale), main = "Humidité pondérale", xlab = "Humidité pondérale",ylab ="Cumulative probabilité") 
hist(Densite_apparente_A_C$N_humidite_pond, main = "N[humidité pondérale]", xlab = "N[humidité pondérale]", nclass = 15)
plot(ecdf(Densite_apparente_A_C$N_humidite_pond), main = "N[humidité pondérale]", xlab = "N[humidité pondérale]",ylab ="Cumulative probabilité") 

bubble(Densite_apparente_A_C,"humidite_ponderale", fill =TRUE, maxsize = 1.5, main = "Humidité pondérale", identify = FALSE, xlab = "X (m)", ylab = "Y(m)")

spplot(Densite_apparente_A_C, "Humidite_volumique", do.log = TRUE,# location map of porosity data
       key.space=list(x=.85,y=0.97,corner=c(-1.2,1)),cuts = cut2,
       scales=list(draw=T),xlab = "X (m)", ylab = "Y (m)",main ="Humidité volumique(%)")

###### calcul de variogram omnidirectionnel humidité ###################################"
vg_map_humidite_vol<- variogram(
  N_humidite_volu ~ 1,
  Densite_apparente_A_C,
  cutoff = 100,
  width = 10,
  map =TRUE
)
plot(
  vg_map_humidite_vol,
  main = "Semivariogram Map",
  max = 1.0
)

################## calcul de va################## calcul de variogramm directionnel #########################

vg_dir_hv <- variogram(
  N_humidite_volu ~ 1,
  Densite_apparente_A_C,
  alpha = c(0,45,90,135),
  cutoff = 100,
  width = 10
)
vg_dir_hv
plot(vg_dir_hv, main = "Directional Variograms")

### à 0 degre 
# nugget = 1.5
### sill = 1.46
# range = 45

### à 45 degre 
# nugget = 0.008
### sill = 1.2
# range = 64

### à 90 degre 
# nugget = 1.18
### sill = 1.1
# range = 34

### à 130 degre 
# nugget = 1.4
### sill = 1.17
# range = 55


# portée majeur à 45 degre et portée mineur à 90 degree
# ratio anisotrope = 34/64 = 0.5

############################ construction de variogramme anisotrope#############
vg_aniso_dens <- vgm(
  psill = 1.25,
  model = "Exp",
  range = 90,
  nugget = 0.3,
  anis = c(45, 0.5)
)

vg_aniso_dens_fit <- fit.variogram(vg_dir_densite, model = vg_aniso_dens)
### modelisation du variogramme 
# creation de modéle anisotrope 
vg_mode_hum <- vgm(
  psill = 1.4,
  model ="Sph",
  range = 64,
  nugget = 1.2,
  anis = c(45,0.5)
)
plot(vg_mode_hum, main ="modèle de variogramme anisotrope", cutoff = 100)


###" ajustement du modèle aux données ###############
vg_fit_hum <- fit.variogram(
  vg_dir_hv, model = vg_mode_hum
)

plot(vg_fit_hum,vg_dir_hv)


############################################# etape 


################## calcul de variogramm directionnel #########################

vg_dir_huv <- variogram(
  N_humidite_volu ~ 1,
  Densite_apparente_A_C,
  alpha = c(0,45,90,135),
  cutoff =100,
  width = 10
)

plot(vg_dir_huv, main = "Directional Variograms")

############################ construction de variogramme anisotrope#############
vg_aniso_huv <- vgm(
  psill = 1.2,
  model = "Sph",
  range = 50,
  nugget = 0.8,
  anis = c(45, 0.5)
)

vg_hum_fit <- fit.variogram(vg_dir_huv, model = vg_aniso_huv)

plot(vg_dir_densite, vg_aniso_dens_fit, main="Variogramme anisotrope ajusté")

vg_dir_huv_filtered <- vg_dir_huv[vg_dir_huv$np >= 5, ]
vg_hum_fit <- fit.variogram(vg_dir_huv_filtered, model = vg_aniso_huv)

