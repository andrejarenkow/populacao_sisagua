# Importação de bibliotecas
import streamlit as st
import pandas as pd
import plotly.express as px

# Hello SISAGUA

st.write("Heloo, Sisagua")

dados = pd.read_excel('https://drive.google.com/uc?export=download&id=1-3mDdJsT768n9gupjR3ZFDHdxlbY2td0')
dados.head()
