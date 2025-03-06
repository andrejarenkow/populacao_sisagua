# Importação das bibliotecas necessárias
import streamlit as st
import pandas as pd
import plotly.express as px
from urllib.request import urlopen
import json

# Exibe uma mensagem na interface do Streamlit
st.write("Hello, Sisagua")

# Importação do json para mapas
with urlopen('https://raw.githubusercontent.com/andrejarenkow/geodata/refs/heads/main/municipios_rs_CRS/rs_municipios_crs.json') as response:
    url_municipios_geojson = json.load(response)

# Carrega os dados a partir de um arquivo Excel hospedado no Google Drive
dados = pd.read_excel('https://drive.google.com/uc?export=download&id=1-3mDdJsT768n9gupjR3ZFDHdxlbY2td0')

# Filtra os dados para incluir apenas o ano de referência 2025 (possível erro, deveria ser 2023?)
dados_rs_2023 = dados[(dados['Ano de referência'] == 2025)].reset_index(drop=True)

# Cria uma nova coluna 'pop_abastecida' baseada na 'População estimada'
dados_rs_2023['pop_abastecida'] = dados_rs_2023['População estimada']

# Criação de uma tabela dinâmica (pivot table) para agregar os dados de população abastecida
dados_rs_2023_pop_abastecida = pd.pivot_table(
    dados_rs_2023, 
    index=['Código IBGE', 'Município', 'Regional de Saúde'], 
    values='pop_abastecida', 
    columns='Tipo da Forma de Abastecimento', 
    aggfunc='sum'
).reset_index()

# Calcula o total da população abastecida somando as colunas 'SAA', 'SAC' e 'SAI'
dados_rs_2023_pop_abastecida['total'] = dados_rs_2023_pop_abastecida[['SAA','SAC','SAI']].sum(axis=1)

# Carrega os dados de municípios a partir de um arquivo CSV no GitHub
municipios = pd.read_csv(
    'https://raw.githubusercontent.com/andrejarenkow/csv/master/Munic%C3%ADpios%20RS%20IBGE6%20Popula%C3%A7%C3%A3o%20CRS%20Regional%20-%20P%C3%A1gina1.csv',
    sep=','
)

# Seleciona apenas as colunas relevantes
municipios = municipios[['IBGE6', 'População_estimada']]

# Renomeia as colunas para manter a consistência com os dados anteriores
municipios.columns = ['Código IBGE', 'População_estimada']

# Mescla (merge) os dados de abastecimento com a população estimada por município
dados_pop_sem_info = dados_rs_2023_pop_abastecida.merge(municipios, on='Código IBGE')

# Calcula a população sem informação de abastecimento de água
dados_pop_sem_info['pop_sem_informacao'] = dados_pop_sem_info['População_estimada'] - dados_pop_sem_info['total']

# Calcula a porcentagem da população sem informação e arredonda para duas casas decimais
dados_pop_sem_info['porcentagem_pop_sem_informacao'] = (
    dados_pop_sem_info['pop_sem_informacao'] / dados_pop_sem_info['População_estimada'] * 100
).round(2)

# Mapa
fig = px.choropleth(dados_pop_sem_info, geojson=url_municipios_geojson, locations='IBGE6', featureidkey="properties.IBGE6",
                    color='porcentagem_pop_sem_informacao',
                    color_continuous_scale="Viridis",
                    range_color=(0, 100),
                    labels={'porcentagem_pop_sem_informacao':'População sem informação'},
                    projection="mercator",
                    hover_data=['Regional de Saúde'],
                    hover_name='Município',
                    title='População sem informação por município',
                    width=1000,
                    height=800
                          )

fig.update_geos(fitbounds="locations", visible=False)
#fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
st.plotly_chart(fig)
