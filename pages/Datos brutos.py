from bs4 import BeautifulSoup
import pandas as pd
import plotly.express as px
import requests
import time
import streamlit as st
import warnings

warnings.filterwarnings('ignore')

@st.cache_data
def convierte_csv(df):
    return df.to_csv(index=False, sep='#').encode('utf-8')

def mensaje_exito():
    exito = st.success('Archivo descargado con exito')#icon
    time.sleep(8)
    exito.empty()

st.title("DATOS BRUTOS")

url = 'https://ahcamachod.github.io/productos'

response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')
datos = pd.read_json(soup.pre.contents[0])
datos['Fecha de Compra'] = pd.to_datetime(datos['Fecha de Compra'], format='%d/%m/%Y')

st.sidebar.title('Filtros')

with st.expander('Columnas'):
    columnas = st.multiselect('Selecciona las columnas', list(datos.columns),list(datos.columns))

with st.sidebar.expander('Nombre del Producto'):
    productos = st.multiselect('Selecciona los productos', datos['Producto'].unique(),datos['Producto'].unique())

with st.sidebar.expander('Precio del Producto'):
    precio = st.slider('Selecciona el precio',0,5000000,(0,5000000))

with st.sidebar.expander('Fecha de Compra'):
    fecha_compra = st.date_input('Selecciona la fecha', (datos['Fecha de Compra'].min(),datos['Fecha de Compra'].max()))


query = """
Producto in @productos and \
@precio[0] <= Precio <=@precio[1] and \
@ fecha_compra[0] <= `Fecha de Compra` <= @fecha_compra[1]    

"""
datos_filtrados = datos.query(query)
datos_filtrados = datos_filtrados[columnas]

st.dataframe(datos_filtrados)

st.markdown(f'La tabla posee :blue[{datos_filtrados.shape[0]}] filas y :blue[{datos_filtrados.shape[1]}] columnas')

st.markdown('Escribe un nombre para el archivo')

col1, col2 = st.columns(2)

with col1:
    nombre_archivo = st.text_input('',
                                   label_visibility='collapsed',
                                   value='datos')
    nombre_archivo +='.csv'

with col2:
    st.download_button('Realiza la descarga de la tabla en formato csv',
                       data= convierte_csv(datos_filtrados),
                       file_name=nombre_archivo,
                       mime='text/csv', on_click= mensaje_exito)