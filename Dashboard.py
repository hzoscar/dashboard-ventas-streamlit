from bs4 import BeautifulSoup
import pandas as pd
import plotly.express as px
import requests
import streamlit as st
import warnings

warnings.filterwarnings('ignore')

st.title("DASHBOARD DE VENTAS :shopping_trolley:")

url = 'https://ahcamachod.github.io/productos'

response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')
datos = pd.read_json(soup.pre.contents[0])

st.dataframe(datos)