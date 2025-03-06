# Importação de bibliotecas
import streamlit as st
import pandas as pd
import plotly.express as px

# Hello SISAGUA

st.write("Heloo, Sisagua")

dados = pd.read_excel('https://drive.google.com/uc?export=download&id=1-3mDdJsT768n9gupjR3ZFDHdxlbY2td0')

dados_rs_2023 = cadastro_populacao_abastecida[(cadastro_populacao_abastecida['UF']=='RS')&(cadastro_populacao_abastecida['Ano de referência']==2025)].reset_index(drop=True)
dados_rs_2023['pop_abastecida'] = dados_rs_2023['População estimada']

dados_rs_2023_pop_abastecida = pd.pivot_table(dados_rs_2023, index=['Código IBGE', 'Município', 'Regional de Saúde'], values='pop_abastecida', columns='Tipo da Forma de Abastecimento', aggfunc='sum').reset_index()
dados_rs_2023_pop_abastecida['total'] = dados_rs_2023_pop_abastecida[['SAA','SAC','SAI']].sum(axis=1)
dados_rs_2023_pop_abastecida

municipios = pd.read_csv('https://raw.githubusercontent.com/andrejarenkow/csv/master/Munic%C3%ADpios%20RS%20IBGE6%20Popula%C3%A7%C3%A3o%20CRS%20Regional%20-%20P%C3%A1gina1.csv', sep=',')
municipios = municipios[['IBGE6', 'População_estimada']]
municipios.columns = ['Código IBGE', 'População_estimada']

dados_pop_sem_info = dados_rs_2023_pop_abastecida.merge(municipios, on='Código IBGE')
dados_pop_sem_info['pop_sem_informacao'] = dados_pop_sem_info['População_estimada'] - dados_pop_sem_info['total']
dados_pop_sem_info['porcentagem_pop_sem_informacao'] = (dados_pop_sem_info['pop_sem_informacao']/dados_pop_sem_info['População_estimada']*100).round(2)
dados_pop_sem_info.sort_values('porcentagem_pop_sem_informacao', ascending=False)
