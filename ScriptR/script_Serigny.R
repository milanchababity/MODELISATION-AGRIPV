####### importation des packages

library(dplyr)
library(ggplot2)
library(tidyr)
library(tidyverse)
library(readr)
library(readxl)
library(stringr)
library(here)
library(ggplot2)
library(gridExtra)

install.packages("here")
install.packages("gridExtra")
## importation de dossier de travail 
loca_fichier ="C:/Users/mbabity/Desktop/TSE_SERIGNY/PESEEFINAL"
file<-read_xlsx("C:/Users/mbabity/Desktop/TSE_SERIGNY/PESEEFINAL/echantillons.xlsx")
chemin1 <-"C:/Users/mbabity/Desktop/TSE_SERIGNY/PESEEFINAL/densite_apparente_krigeage.csv"
chemin2<-"C:/Users/mbabity/Desktop/TSE_SERIGNY/PESEEFINAL/densite_apparente_reservoir.csv"

## selection des colonnes contenant les variables d'interêt
sol_serigny<-file|>select("Id","Nom échantillon","Provenance","Poids_analyse","Poids_frais","Poids_sec")
sol_extract <-sol_serigny|>mutate(
  masse_humide = as.numeric(str_replace(str_extract(`Poids_frais`, "\\d+[,.]?\\d*"), ",", ".")),
  masse_seche  = as.numeric(str_replace(str_extract(`Poids_sec`, "\\d+[,.]?\\d*"), ",", ".")),
  masse_contenant = as.numeric(str_replace(str_extract(`Poids_analyse`, "\\d+[,.]?\\d*"), ",", "."))
)
names(sol_extract)
densite_apparente<-sol_extract|>mutate(
  masse_mumide_T=masse_humide-masse_contenant,
  masse_seche_T=masse_seche-masse_contenant
)|>select(Id,`Nom échantillon`,Provenance,masse_mumide_T,masse_seche_T)
View(densite_apparente)

## carto pour le krigeage avec suppresion des données na
carto_da<-densite_apparente[1:58,]|>na.omit()
write.csv(carto_da,chemin1,row.names = FALSE)
View(carto_da)

## densite apparente pour le calcul du réservoir  avec suppression des données manquantes
da_reservoir<-densite_apparente[58:nrow(densite_apparente),]|>na.omit()
write.csv(carto_da,chemin2,row.names = FALSE)
names(da_reservoir)
## calcul de la densite apparente
da_reservoir<-da_reservoir|>mutate(
  humidite_massique=(masse_mumide_T-masse_seche_T)/100,
  densite_apparente_seche=masse_seche_T/100,
  porosite_sol=((2.5-densite_apparente_seche)/2.5)*100)


## regroupement 
## temoins, AV point1,AV point2
da_reservoir_groupe <-da_reservoir|> mutate(
  type=case_when(
    grepl("tem/P1/H1",Provenance,ignore.case = TRUE)~"Tem_P1_H1",
    grepl("tem/P1/H2",Provenance,ignore.case = TRUE)~"Tem_P1_H2",
    grepl("tem/P1/H3",Provenance,ignore.case=TRUE)~"Tem_P1_H3",
    grepl("tem/P2/H1",Provenance,ignore.case=TRUE)~"Tem_P2_H1",
    grepl("tem/P2/H2",Provenance,ignore.case=TRUE)~"Tem_P2_H2",
    grepl("tem/P3/H1",Provenance,ignore.case=TRUE)~"Tem_P3_H1",
    grepl("tem/P3/H2",Provenance,ignore.case=TRUE)~"Tem_P3_H2",
    grepl("tem/P3/H2",Provenance,ignore.case=TRUE)~"Tem_P3_H2",
    grepl("Avgauche/P1/H1",Provenance,ignore.case=TRUE)~"AV_gauche",
    grepl("Avgauche/P2/H1",Provenance,ignore.case=TRUE)~"AV_droite_H1",
    grepl("Avgauche/P2/H2",Provenance,ignore.case=TRUE)~"AV_droite_H2",
    grepl("Avgauche/P2/H3",Provenance,ignore.case=TRUE)~"AV_droite_H3"))
View(da_reservoir_groupe)


graph_tem<-da_reservoir_groupe|>filter(grepl("Tem",type))|>ggplot(aes(x=type, y = densite_apparente_seche, color =type)) +geom_boxplot() +geom_hline(yintercept = 1.45, color= "red", linetype ="dashed")+labs(x = "Points de prélèvements",y = "Densité apparente sèche",title = "Densité apparente sèche (Témoin)")
graph_AV<-da_reservoir_groupe |>filter(grepl("AV",type))|>ggplot(aes(x=type,y=densite_apparente_seche,color=type))+geom_boxplot()+geom_hline(yintercept = 1.45,color="red",linetype="dashed")+labs(x="Points de prélèvements",y="Densité apparente sèche",title="Densité apparente sèche (AgriPV)")
graph_AV

Graph_final=grid.arrange(graph_tem,graph_AV,ncol=1,nrow=2)
ggsave("C:/Users/mbabity/Desktop/TSE_SERIGNY/PESEEFINAL/densite_reservoir.png",Graph_final)












### statistique descriptive 


