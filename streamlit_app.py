# Importação das bibliotecas necessárias
import streamlit as st
import pandas as pd
import plotly.express as px
from urllib.request import urlopen
import json

# Configurações da página
st.set_page_config(
    page_title="Pop Sisagua",
    page_icon="	:water:",
    layout="wide",
    initial_sidebar_state='collapsed'
) 
col1, col2, col3 = st.columns([1,4,1])

col1.image('https://github.com/andrejarenkow/csv/blob/master/logo_cevs%20(2).png?raw=true', width=100)
col2.header('Painel População Abastecida no Sisagua')
col3.image('https://github.com/andrejarenkow/csv/blob/master/logo_estado%20(3)%20(1).png?raw=true', width=150)

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
municipios = municipios[['IBGE6', 'População_estimada', "Município"]]

# Renomeia as colunas para manter a consistência com os dados anteriores
municipios.columns = ['Código IBGE', 'População_estimada', 'Município']

dados_pop_sem_info = dados_rs_2023_pop_abastecida.drop(['Município'], axis = 1).merge(municipios, on='Código IBGE', how = 'right')
dados_pop_sem_info['IBGE6'] = dados_pop_sem_info['Código IBGE']#.astype(str)
dados_pop_sem_info['porcentagem_pop_com_informacao'] = (dados_pop_sem_info['total']/dados_pop_sem_info['População_estimada']*100).round(1).fillna(0)

dados_pop_sem_info.sort_values('porcentagem_pop_com_informacao', ascending=False)

# Criar faixas para deixar cores discretas

faixas = [-1, 1, 25, 50, 75, 99, 10000]

nomes_faixas = ['0%', '1 a 25%','25 a 50%', '50 a 75%', '75 a 99%', '100%']

dados_pop_sem_info['faixa'] = pd.cut(dados_pop_sem_info['porcentagem_pop_com_informacao'], bins=faixas, labels=nomes_faixas)
dados_pop_sem_info = dados_pop_sem_info.sort_values('porcentagem_pop_com_informacao')

# Gerar mapa com o plotly.express

import plotly.express as px

fig_mapa = px.choropleth(dados_pop_sem_info, geojson=url_municipios_geojson, locations='Código IBGE', featureidkey="properties.IBGE6",
                    color='faixa',
                    color_continuous_scale="Viridis",
                    range_color=(0, 100),
                    labels={'porcentagem_pop_com_informacao':'População com informação',
                           'faixa':'Faixa de atingimento'},
                    projection="mercator",
                    hover_data=['porcentagem_pop_com_informacao', 'Regional de Saúde'],
                    hover_name='Município',
                    title='População com informação por município',
                    width=1000,
                    height=800,
                    color_discrete_map = {
                        '1 a 25%': '#FE556A',
                        '25 a 50%': '#FEA052',
                       '50 a 75%': '#FEDD59',
                        '75 a 99%': '#19B377',
                        '0%': '#161C23',
                        '100%': '#5372FE'
                    }

                          )


fig_mapa.update_geos(fitbounds="locations", visible=False)

# Criar DataFrame com a contagem das faixas
df_faixas = dados_pop_sem_info['faixa'].value_counts().reset_index()
df_faixas.columns = ['faixa', 'contagem']

# Definir a ordem desejada
ordem_faixas = nomes_faixas
df_faixas['faixa'] = pd.Categorical(df_faixas['faixa'], categories=ordem_faixas, ordered=True)
df_faixas['faixa'] = df_faixas['faixa'].astype('str')

# Criar gráfico de barras
fig_bar = px.bar(df_faixas.sort_values('faixa'), x='faixa', y='contagem', title='Distribuição das Faixas',
             labels={'faixa': 'Faixa', 'contagem': 'Contagem'}, text_auto=True)

df_faixas
coluna_1, coluna_2 = st.columns(2)
st.plotly_chart(fig_bar)
coluna_2.plotly_chart(fig_mapa)
