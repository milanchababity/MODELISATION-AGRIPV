library(dplyr)
library(readxl)
# Read the Excel file
data <- read_excel("C:/Users/mbabity/Desktop/These CIFRE/Densite_apparente_avant_chantier/echantillons_2025-12-05_1757.xlsx")
head(data)
str(data)

##########################sélection des données permettant de calculer la densité apparente pour le réservoir hydrique 
res_da<-data|>rename(poids_prelevement="Poids prélèvement",
                     masse_seche="Poids sec",
                     masse_fraiche = "Poids frais",
                     Tare="Poids analyse") |> select(
                       Id,
                       Provenance,
                       masse_fraiche,
                       masse_seche,
                       Tare,
                     )
print(res_da, n=80)
str(res_da)

####séparation des numeriques et des unités 
library(tidyr)
library(dplyr)
cols<-c("masse_fraiche","masse_seche","Tare")

for(c in cols) {
  res_da<-res_da|>
    separate(
      !!sym(c),
      into = c(paste0(c,"_valeur"), paste0(c,"_unité")),
      sep = "(?<=\\d)(?=g)",
      remove = FALSE
    )
}
View(res_da)


###### Sélection des valeurs numériques
library(dplyr)

res_da_valeur<-res_da|> select(
  Id,Provenance,masse_fraiche_valeur,masse_seche_valeur,Tare_valeur
)

View(res_da_valeur)
res_da_cal<-res_da_valeur|>mutate(
  across(
    ends_with("_valeur"),## toutes les colonnnes finissent par valeur 
    as.numeric
  )
)

####Nettoyage de données 
library(dplyr)

res_da_clean <- res_da_cal|>
  filter(rowSums(!is.na(across(ends_with("_valeur")))) > 0)

res_da_clean <- res_da_clean %>%
  slice(-1)  # enlève la première ligne

View(res_da_clean)
write.csv(res_da_clean,"données nettoyées.csv")

### séparation des données en deux fichiers 
# le premier servira à calculer le réservoir hydrique et deuxième pour la densité apparente 
fichier_resda <- res_da_clean |>
  filter(grepl("Resda", Provenance, ignore.case = TRUE))
print(fichier_resda)
View(fichier_resda)

fichier_da<-res_da_clean |>
  filter(grepl("da", Provenance, ignore.case = TRUE) &!grepl("Resda", Provenance,ignore.case = TRUE))
fichier_da

write.csv(fichier_resda,"densite_apparente_reservoir.csv")
write.csv(fichier_da,"densite_apparente_da.csv")

#### traitement de données réservoir 
reservoir_da<-fichier_resda |> mutate(
  "Tare"=5.350
) |> select(Id,Provenance,masse_fraiche_valeur,masse_seche_valeur,Tare)
reservoir_da<-reservoir_da |>
  mutate("humidite_ponderale"= (masse_fraiche_valeur - masse_seche_valeur)/(masse_seche_valeur - Tare),
         "densite_apparente"= (masse_seche_valeur-Tare)/100,
         "humidite_volumique" = densite_apparente * humidite_ponderale,
         "porosite_du_sol" = (2.6 - densite_apparente)/2.6)

View(reservoir_da)
head(reservoir_da)

##### séparation par configuration 
conf1_h1<-reservoir_da|>filter(
  grepl("Conf1/H1",Provenance,ignore.case=TRUE)
) |> mutate("type"= "config1",
            "horizon"= "1")
conf1_h2<-reservoir_da|>filter(
  grepl("Conf1/H2",Provenance,ignore.case=TRUE)
)|> mutate(
  "type" ="config1",
  "horizon" ="2"
)
View(conf1_h2)

##conf2
conf2_h1<-reservoir_da|>filter(
  grepl("Conf2/H1",Provenance,ignore.case=TRUE)
)|> mutate(
  "type" ="config2",
  "horizon" ="1")

conf2_h2<-reservoir_da|>filter(
  grepl("Conf2/H2",Provenance,ignore.case=TRUE)
)|> mutate(
  "type" ="config2",
  "horizon" ="2")

#conf3
conf3_h1<-reservoir_da|>filter(
  grepl("Conf3/H1",Provenance,ignore.case=TRUE)
)|> mutate(
  "type" ="config3",
  "horizon" ="1")


conf3_h2<-reservoir_da|>filter(
  grepl("Conf3/H2",Provenance,ignore.case=TRUE)
)|> mutate(
  "type" ="config3",
  "horizon" ="2")

#conf4
conf4_h1<-reservoir_da|>filter(
  grepl("Conf4/H1",Provenance,ignore.case=TRUE)
)|> mutate(
  "type" ="config4",
  "horizon" ="1")


conf4_h2<-reservoir_da|>filter(
  grepl("Conf4/H2",Provenance,ignore.case=TRUE)
)|> mutate(
  "type" ="config4",
  "horizon" ="2")

# conf5
conf5_h1<-reservoir_da|>filter(
  grepl("Conf5/H1",Provenance,ignore.case=TRUE)
)|> mutate(
  "type" ="config5",
  "horizon" ="1")

conf5_h2<-reservoir_da|>filter(
  grepl("Conf5/H2",Provenance,ignore.case=TRUE)
  )|> mutate(
    "type" ="config5",
    "horizon" ="2")

#temoin

tem_h1<-reservoir_da|>filter(
  grepl("Tem/H1",Provenance,ignore.case=TRUE)
)|> mutate(
  "type" ="tem",
  "horizon" ="1")

tem_h2<-reservoir_da|>filter(
  grepl("Tem/H2",Provenance,ignore.case=TRUE)
)|> mutate(
  "type" ="tem",
  "horizon" ="2")
### assemblage des données 

# Fusionner tous les sous-ensembles
reservoir_da_traite <- bind_rows(
  conf1_h1, conf1_h2,
  conf2_h1, conf2_h2,
  conf3_h1, conf3_h2,
  conf4_h1, conf4_h2,
  conf5_h1, conf5_h2,
  tem_h1, tem_h2
)

dim(reservoir_da_traite)   # nombre de lignes et colonnes
head(reservoir_da_traite)  # voir les premières lignes
View(reservoir_da_traite)

### boxplot 
library(dplyr)
library(tidyr)
reservoir<-reservoir_da_traite|> group_by(type,horizon)|>
  summarise(
    y=mean(densite_apparente,na.rm=TRUE), #POINT CENTRAL
    ymin=min(densite_apparente, na.rm = TRUE),
    ymax=max(densite_apparente, na.rm =TRUE)
  )
View(reservoir)

############bulk density graphique 

bulk_density <- ggplot(reservoir_da_traite, aes(x=type, y=densite_apparente, fill=horizon))+
  geom_boxplot(
    width = 0.5,
    outlier.shape = NA
  )+
  geom_jitter(
    width = 0.15,
    size = 1,
    alpha = 0.7,
    color="black"
  ) +
    scale_fill_manual(
      values = c("1"="gray", "2"="#C77")
    )+
  facet_wrap (~ type, nrow= 3)+
  labs(
    x = "Configurations",
    y= "Densité apparente",
    fill = "Horizons pédologiques")+
  theme(
    axis.text.x = element_blank()
  ) +
  geom_hline(
    yintercept = 1.5,
    linetype ="dashed",
    color ="red"
  )

####### porosité graphique 

soil_porosity <- ggplot(reservoir_da_traite, aes(x=type, y=porosite_du_sol, fill=horizon))+
  geom_boxplot(
    width = 0.5,
    outlier.shape = NA
  )+
  geom_jitter(
    width = 0.15,
    size = 1,
    alpha = 0.7,
    color="black"
  ) +
  scale_fill_manual(
    values = c("1"="gray", "2"="#C77")
  )+
  facet_wrap (~ type, nrow= 3)+
  labs(
    x = "Configurations",
    y= "Porisité",
    fill = "Horizons pédologiques")+
  theme(
    axis.text.x = element_blank()
  ) 
 
soil_porosity

############## humidité volumique 

soil_humidity <- ggplot(reservoir_da_traite, aes(x=type, y=humidite_volumique, fill=horizon))+
  geom_boxplot(
    width = 0.5,
    outlier.shape = NA
  )+
  geom_jitter(
    width = 0.15,
    size = 1,
    alpha = 0.7,
    color="black"
  ) +
  scale_fill_manual(
    values = c("1"="gray", "2"="#C77")
  )+
  facet_wrap (~ type, nrow= 3)+
  labs(
    x = "Configurations",
    y= "Humidité volumique",
    fill = "Horizons pédologiques")+
  theme(
    axis.text.x = element_blank(),
    axis.title.x =element_blank()
  ) 

soil_humidity

######################################################### analyse statistique############################################ 
## test d'homegeneité de la variance 

install.packages("car")
library(car)

# test de levene pour l'homogeneité de variance 
leveneTest(densite_apparente ~ type * horizon, reservoir_da_traite)
# H0 absence de variation de variance 
# H1 variance non homogène 
# P_value = 0.8 > 0.05 donc on ne rejette pas l'hypothèse nulle ==> variance homogène 

#### test de normalité 
anova_model<-aov(densite_apparente ~ type * horizon, reservoir_da_traite)
residus <-residuals(anova_model)
shapiro.test(residus)
 # H0 variable suit une distribution normale 
#  H1 variable ne suit pas une distrubition normale 
 # P_vlaue 0.8501 > 0.05 on ne rejette pas l'hypothèse nulle 

############################# ANOVA ######################

summary(anova_model)
# effet config # significatif
#effet horizon très significatif
# effet config+horizon siggnificatif

################ test post-hoc ou comparaison multiple des moyennes






#### visualisation des données 
install.packages("multcompView")
library(multcompView)

anova_model <- aov(densite_apparente ~ type * horizon, data = reservoir_da_traite)

tukey_results<-TukeyHSD(anova_model)

#### les trois méthodes d'analyse possible (type, horizon et type:horizon)
tukey_cld <- multcompLetters4(anova_model,tukey_results)
tukey_cld$`type:horizon`
tukey_cld$type
tukey_cld$horizon


#### regroupement des résultats 
library(dplyr)
library(tidyr)


# préparation des moyennes et ecart_type
moyennes <- reservoir_da_traite |> 
  group_by (type, horizon) |>
  summarise (
    moyenne = mean (densite_apparente),
    sd=sd(densite_apparente),
    .groups = "drop"
  )
moyennes


#graphique d'intéraction entre type et horizon 

library(ggplot2)
ggplot(moyennes, aes(x= horizon, y = moyenne, color = type, group = type)) +
  geom_point( size = 3)+
  geom_line (size =1)+
  geom_errorbar(
    aes(
      ymin = moyenne - sd,
      ymax = moyenne + sd,
      width = 0.15
    )
  )+
facet_wrap (~ type, ncol= 3)+
  labs(
    x = "Configurations",
    y= "Densité apparente",
    fill = "Horizons pédologiques")+
theme_minimal()


# extraction de p_value et gerer les lettres 

### effet type 
type_df <- data.frame(
  type = names(tukey_cld$type$Letters),
  lettres = tukey_cld$type$Letters
)

moyenne_type <- reservoir_da_traite |> group_by(type) |>
  summarise(moyenne = mean (densite_apparente),
             sd = sd(densite_apparente),
             .groups ="drop")

type_df_g <- left_join(moyenne_type,type_df, by ="type")

###################################graph type 
library(ggplot2)
effet_type <- ggplot (type_df_g, aes(x=type, y = moyenne, color =type)) +
  geom_boxplot(aes (x=type, y = moyenne, size = 4, fill = type))+
  geom_errorbar(aes(
    ymin = moyenne-sd,
    ymax = moyenne +sd,
    width = 0.15
  )) +
  geom_text(aes(
    label = lettres),vjust = -2, size = 4
  ) +
  labs (
    x= "Ccnfigurations",
    y= "Densité apparente g/cm3",
    title = "Densité apparente mesurée selon les configurations"
  ) +
theme_minimal () +
  theme (legend.position = "none",
         panel.grid = element_blank(),
         panel.border = element_rect(color ="black"),
         axis.line = element_line(color = "black"))
  
effet_type





## effet horizon################################################################################## 
horizon_df <- data.frame (
  horizon = names(tukey_cld$horizon$Letters),
  lettres =tukey_cld$horizon$Letters
)

moyenne_horizon <- reservoir_da_traite |> group_by(horizon) |>
  summarise(moyenne = mean(densite_apparente),
            sd = sd(densite_apparente),
            .groups = "drop")
horizon_df_g <- left_join(moyenne_horizon, horizon_df, by = "horizon")


################################### graph horizon

effet_horizon <- ggplot (horizon_df_g, aes(x=horizon , y = moyenne, color = horizon)) +
  geom_boxplot(aes (x= horizon, y = moyenne, size = 4, fill = horizon))+
  geom_errorbar(aes(
    ymin = moyenne - sd,
    ymax = moyenne + sd,
    width = 0.15
  )) +
  geom_text(aes(
    label = lettres),vjust = -2, size = 4
  ) +
  labs (
    x= "Horizons",
    y= "Densité apparente g/cm3",
    title = "Densité apparente mesurée selon les horizons"
  ) +
  theme_minimal () +
  theme (legend.position = "none",
         panel.grid = element_blank(),
         panel.border = element_rect(color ="black"),
         axis.line = element_line(color = "black"))

effet_horizon



## effet intéraction 
inter_df <- data.frame (
  type_horizon = names(tukey_cld$`type:horizon`$Letters),
  lettres = tukey_cld$`type:horizon`$Letters
)


inter_df <- inter_df |>
  separate (
    type_horizon, into = c("type","horizon"), sep = ":"
  )

moyenne_inter <- reservoir_da_traite |> group_by (type,horizon) |>
  summarise( moyenne = mean(densite_apparente),
             sd = sd (densite_apparente),
             .groups = "drop") 


inter_df_g <- left_join (moyenne_inter, inter_df, by= c("type", "horizon"))




#### graphiquessss####" intéraction 

ncol_facets <- 3
effet_interact <- ggplot(inter_df_g, aes(x=type , y = moyenne, color = horizon, group = horizon))+
  geom_point()+
  geom_hline(yintercept = 1.5, color ="red", linetype = "dashed", size = 0.5)+
  geom_text(aes(
    label = lettres),hjust = -0.5, size = 4
  ) +
  labs (
    x= "Horizons",
    y= "Densité apparente g/cm3",
    title = "Densité apparente mesurée selon les horizons"
  ) +
  theme_minimal () +
  theme (legend.position = "bottom",
         panel.grid = element_blank(),
         panel.border = element_rect(color ="black"),
         axis.line = element_line(color = "black"),
         axis.text.x = element_blank(),
         axis.ticks.x = element_blank(),
         axis.title.x = element_blank(),
         strip.placement = "outside",
         strip.background = element_blank())+
  facet_wrap (~ type, nrow = 3, scales ="fixed", switch("x"))
  


effet_interact
g <- ggplotGrob(effet_interact)

# Identifier les axes X
# Les axes X ont le nom "axis-b" dans la gtable
axis_b_indices <- which(g$layout$name == "axis-b")

# Identifier les strips (facette titles) pour trouver la dernière rangée
strip_t_indices <- which(g$layout$name == "strip-t")


# Trouver combien de colonnes il y a dans la grille (pour deviner la dernière rangée)
layout <- g$layout
effet_interact

# Extraire les panneaux (panel) et leur position
panels <- layout[layout$name == "panel", ]

# Nombre de colonnes des panneaux
ncol_panels <- length(unique(panels$l))
library (tidyr)

# Trouver les panneaux de la dernière rangée
last_row_panels <- panels %>% filter(t == max_row)
# Trouver les rangées des panneaux (coordonnées 't')
max_row <- max(panels$t)

# Trouver les panneaux de la dernière rangée
last_row_panels <- panels %>% filter(t == max_row)

# Identifier quels axes X correspondent aux panneaux hors dernière rangée
# Chaque axe-b correspond à un panneau, dans le même ordre que panels
# On masque les axes qui ne sont pas sur la dernière rangée

for (i in seq_along(axis_b_indices)) {
  # Position du panneau correspondant à cet axe
  panel_pos <- panels[i, ]
  if (panel_pos$t != max_row) {
    # Masquer cet axe X (par ex. réduire sa hauteur à 0 et/ou rendre invisible)
    g$heights[g$layout[axis_b_indices[i], ]$t] <- unit(0, "cm")
    g$grobs[[axis_b_indices[i]]] <- nullGrob()
  }
}

# Dessiner le plot modifié
library(grid)
grid.newpage()
grid.draw(g)

tukey_cld<-multcompLetters4(anova_model, tukey_results)

tukey_letters <- multcompLetters(tukey_results$`type:horizon`[, "p adj"])$Letters
tukey_df <-data.frame(
  group = names(tukey_letters),
  letter = tukey_letters
)
View(tukey_df)


# moyenne par groupe 

means_df <- reservoir_da_traite |> group_by (type, horizon) |>
  summarise(
    means_dens = mean (densite_apparente, na.rm =TRUE),
    .groups ="drop"
  ) |> mutate(
    group = paste(type,horizon,sep =":")) |> left_join(
    tukey_df, by ="group"
  )

View(means_df)


# Niveau de facteur 
reservoir_da_traite<- reservoir_da_traite|> mutate(
  type = as.factor(type),
  horizon = as.factor(horizon)
)
View(reservoir_da_traite)

##" conversion de chaine de carractére en numerique
library(dplyr)





res_da_unit <- res_da_unit |>
  mutate(across(
    c(masse_fraiche_unité, masse_seche_unité, Tare_uni),  # colonnes à convertir
    as.numeric
  ))



res_da_unit <- res_da |>
  tidyr::separate(
    c(masse_fraiche, masse_seche, Tare),
    into = c("{.col}_valeur", "{.col}_unité"),
    sep = "(?<=\\d)(?=g)",
    remove = FALSE
  )



install.packages("tidyr")
res_da_unit<-res_da|>separate(
  c(masse_fraiche,masse_seche,Tare),
  into=c("{.col}_valeur","{.col}_unité"),
  sep = "(?<=\\d)(?=g)",
  remove = FALSE)
  

  
# The data is loaded.
# Install and load tidyr for pivoting
install.packages("tidyr")
library(tidyr)

densite<-data|>select("Id","Provenance","Poids frais","Poids sec","Poids analyse")

# Create a grouping column based on the new request
densite_grouped <- densite %>%
  mutate(groupe = case_when(
    grepl("gran", Provenance, ignore.case = TRUE) ~ "groupe1",
    grepl("Resda", Provenance, ignore.case = TRUE) ~ "groupe2",
    grepl("da", Provenance, ignore.case = TRUE) ~ "groupe3",
    TRUE ~ NA_character_
  ))

# Pivot the data to a wider format.
# This assumes each row has a unique 'Id'. If 'Id' is repeated, you might get list-columns.
densite_pivoted <- densite_grouped %>%
  filter(!is.na(groupe)) %>% # Remove rows that don't belong to a group
  pivot_wider(
    names_from = groupe,
    values_from = Provenance,
    id_cols = c("Id", "Poids frais", "Poids sec", "Poids analyse")
  )

# Select and arrange the final columns as requested
final_data <- densite_pivoted %>%
  select("Id", "Poids frais", "Poids analyse", any_of(c("groupe1", "groupe2", "groupe3")))


# Print the head of the pivoted data to the console
print("Head of the pivoted data:")
print(head(final_data))

# Also try to open the data in a viewer, which might be more convenient
View(final_data)

# Install and load the writexl package to save the data to an Excel file
install.packages("writexl")
library(writexl)

# Save the final data to an Excel file
write_xlsx(final_data, "da_pretraite.xlsx")

print("Successfully saved the pre-processed data to da_pretraite.xlsx")
