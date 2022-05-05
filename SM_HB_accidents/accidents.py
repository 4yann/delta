import pandas as pd
import os
import dash
from dash import html, Dash, dependencies, dcc
import glob
import plotly.express as px

class Accidents():
    def __init__(self, application = None):
        df_final_test = pd.read_csv("SM_HB_accidents/data/final_df.csv")
        self.df = df_final_test
        # Traitement affichage


        #Dash integration

        self.main_layout = html.Div([
            html.H3(children=['Contextualisation des accidents de la route']),
            html.Div([dcc.Graph(id='main-graph')], style={'width':'100%'}),
            html.Div([dcc.RadioItems(id='line-to-histo',
                options=[{'label' : "Histogramme", 'value':1},
                    {'label' : "Ligne", 'value':0}],
                value=1,
                labelStyle={'display':'block'})]),
            html.Br(),
            dcc.Markdown("""
               # Analyse

            #### A propos

            *Sources : https://www.data.gouv.fr/fr/datasets/bases-de-donnees-annuelles-des-accidents-corporels-de-la-circulation-routiere-annees-de-2005-a-2020/

            *(c) 2022 Hugo Boux & Stephane Mabille
            """
            )], style = {
                'backgroundColor' : 'white',
                'padding': '10px 50px 10px 50px'
                })

        if application:
            self.app = application
        else:
            self.app = Dash(__name__)
            self.app.layout = self.main_layout

        self.app.callback(
                dependencies.Output('main-graph', 'figure'),
                dependencies.Input('line-to-histo', 'value'))(self.switch_graph_bar_line)

#    def update_graph(self, value):
#        return 

    def switch_graph_bar_line(self, value):
        strg = 'catr' 
        data = self.df
        if (value == True):
            return get_count_value_param_bar(strg, data)
        else:
            return get_count_value_param_line(strg, data)


def switch_categorie(strg):
    switcher = {
            "catr": ["Autoroute","Route nationale","Route Départementale","Voie Communales","Hors réseau public","Parc de stationnement ouvert à la circulation publique","Routes de métropole urbaine","","autre"],
            "plan": ["Partie rectiligne","En courbe à gauche","En courbe à droite","En « S »"],
            "surf": ["Normale","Mouillée","Flaques","Inondée","Enneigée","Boue","Verglacée","Corps gras – huile","Autre"],
            "prof": ["Plat","Pente","Sommet de côte","Bas de côte"],
            "lum": ["Jour", "Semi-nuit", "Nuit noire", "Nuit éclairage éteint", "Nuit avec éclairage"],
            "atm": ["Normale","Pluie légère","Pluie forte","Neige - grêle","Brouillard - fumée","Vent fort - tempête","Temps éblouissant","Temps couvert","Autre"],
            "col": ["Deux véhicules - Frontale", "Deux véhicules - Par l'arrière", "Deux véhicules - Par le coté", "Trois véhicules et + en chaîne", "Trois véhicules et + collisions multiples", "Autre", "Sans collision"],
            "int": ["Hors intersection","Intersection en X","Intersection en T","Intersection en Y","Intersection à plus de 4 branches","Giratoire","Place","Passage à niveau", "Autre intersection"]
            }
    return switcher.get(strg)

def switch_titre(strg):
    switcher = {
            "catr": "Nombre d'accident en fonction de la catégorie de la route de 2015 à 2020",
            "plan": "Nombre d'accident en fonction du tracé en plan de la route de 2015 à 2020",
            "surf": "Nombre d'accident en fonction de l'état de la surface de la route de 2015 à 2020",
            "prof": "Nombre d'accident en fonction de la déclivité de la route de 2015 à 2020",
            "lum": "Nombre d'accident en fonction des conditions d'éclairage de la route de 2015 à 2020",
            "atm": "Nombre d'accident en fonction des conditions atmosphériques de 2015 à 2020",
            "col": "Nombre d'accident en fonction du type de collision de 2015 à 2020",
            "int": "Nombre d'accident en fonction du type d'intersection de la voie de 2015 à 2020" 
            }
    return switcher.get(strg)

def switcher_categorie(strg, df_test):
    if (strg == "catr"):
        return df_test.catr
    elif (strg == "plan"):
        return df_test.plan
    elif (strg == "surf"):
        return df_test.surf
    elif (strg == "lum"):
        return df_test.lum
    elif (strg == "atm"):
        return df_test.atm
    elif (strg == "col"):
        return df_test.col
    elif (strg == "int"):
        return df_test.int
    else:
        return df_test.prof

def get_count_value_param_bar(strg, data):
    add = []
    #an = str(data.iloc[0]['an'])
    tmp_param_name = switch_categorie(strg)
    for annee in range(2015, 2021):
        tmp_annee = data[data["an"] == annee]
        for mois in range(1, 13):
            tmp = tmp_annee[tmp_annee["mois"] == mois]
            month_convert = pd.to_datetime(str(mois) + str(annee), format='%m%Y').strftime("%Y-%m")
            tmp_count = tmp[strg].value_counts()
            for i in range(0, len(tmp_count)):
                add.append([month_convert, tmp_param_name[tmp_count.index[i]-1], tmp_count.values[i]]) #faire qqlchose pour la liste
        df_test = pd.DataFrame(add, columns=["Date", strg, "Count_" + str(strg)])
    fig_line = px.bar(labels= {'x': 'Date', 'y': "Nombre d'accident"}, title=switch_titre(strg)) #faire un switch pour les noms des charts
    fig_test = df_test.groupby(strg)['Count_' + strg].sum().sort_values(ascending=False)###
    for param in range(0, len(fig_test.index)):
        tmp_df = df_test[(switcher_categorie(strg,df_test) == fig_test.index[param])]
        fig_line.add_bar(x=tmp_df["Date"], y=tmp_df["Count_" + str(strg)], name=fig_test.index[param] + " = " + str(fig_test.values[param]))
    return fig_line


def get_count_value_param_line(strg, data):
    add = []
    #an = str(data.iloc[0]['an'])
    tmp_param_name = switch_categorie(strg)
    for annee in range(2015, 2021):
        tmp_annee = data[data["an"] == annee]
        for mois in range(1, 13):
            tmp = tmp_annee[tmp_annee["mois"] == mois]
            month_convert = pd.to_datetime(str(mois) + str(annee), format='%m%Y').strftime("%Y-%m")
            tmp_count = tmp[strg].value_counts()
            for i in range(0, len(tmp_count)):
                add.append([month_convert, tmp_param_name[tmp_count.index[i]-1], tmp_count.values[i]]) #faire qqlchose pour la liste
        df_test = pd.DataFrame(add, columns=["Date", strg, "Count_" + str(strg)])
    fig_line = px.line(labels= {'x': 'Date', 'y': "Nombre d'accident"}, title=switch_titre(strg)) #faire un switch pour les noms des charts
    fig_test = df_test.groupby(strg)['Count_' + strg].sum().sort_values(ascending=False)###
    for param in range(0, len(fig_test.index)):
        tmp_df = df_test[(switcher_categorie(strg,df_test) == fig_test.index[param])]
        fig_line.add_scatter(x=tmp_df["Date"], y=tmp_df["Count_" + str(strg)], name=fig_test.index[param] + " = " + str(fig_test.values[param]))
    return fig_line

if __name__ == '__main__':
    SMBH = Accidents()
    #SMBH.app.run_server(debug=True, port=8051)
