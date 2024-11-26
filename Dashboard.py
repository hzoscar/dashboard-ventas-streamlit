from bs4 import BeautifulSoup
import pandas as pd
import plotly.express as px
import requests
import streamlit as st
import warnings

warnings.filterwarnings('ignore')

## Funciones

def formato_numero(valor,prefijo=''):
    for unidad in ['','mil']:
        if valor < 1000:
            return f'{prefijo} {valor:.2f} {unidad}'
        
        valor /= 1000
    
    return f'{prefijo} {valor:.2f} millones'     

st.set_page_config(layout='wide')

st.title("DASHBOARD DE VENTAS :shopping_trolley:")

url = 'https://ahcamachod.github.io/productos'

response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')
datos = pd.read_json(soup.pre.contents[0])
datos['Fecha de Compra'] = pd.to_datetime(datos['Fecha de Compra'], format='%d/%m/%Y')

## Filtrando por region y por año

regiones_dict = {'Bogotá':'Andina','Medellín':'Andina','Cali':'Pacífica',
                 'Pereira':'Andina','Barranquilla':'Caribe','Cartagena':'Caribe',
                 'Cúcuta':'Andina','Bucaramanga':'Andina','Riohacha':'Caribe',
                 'Santa Marta':'Caribe','Leticia':'Amazónica','Pasto':'Andina',
                 'Manizales':'Andina','Neiva':'Andina','Villavicencio':'Orinoquía',
                 'Armenia':'Andina','Soacha':'Andina','Valledupar':'Caribe',
                 'Inírida':'Amazónica'}

datos['Region'] = datos['Lugar de Compra'].map(regiones_dict)
datos['Año'] = datos['Fecha de Compra'].dt.year

## Sidebar para la interaccion con la API

regiones = ['Colombia','Caribe','Andina','Pacífica','Orinoquía','Amazónica']

st.sidebar.title('Filtro')
region = st.sidebar.selectbox('Region',regiones)
if region == 'Colombia':
    datos = datos.loc[datos['Region'] != 'Colombia']
else:
    datos = datos.loc[datos['Region'] == region]

todos_anos = st.sidebar.checkbox('Datos de todo el periodo', value=True)
if todos_anos:
    datos = datos
else:
    ano = st.sidebar.slider('Año',2020,2023)
    datos = datos.loc[datos['Año']== ano]

filtro_vendedores = st.sidebar.multiselect('Vendedores',datos['Vendedor'].unique())
if filtro_vendedores:
    datos = datos[datos['Vendedor'].isin(filtro_vendedores)]
    



## Creacion de features

# Facturacion por ciudad
fact_ciudades = datos.groupby('Lugar de Compra')[['Precio']].sum()
fact_ciudades = datos.drop_duplicates(subset='Lugar de Compra')[['Lugar de Compra','lat','lon']].merge(fact_ciudades, left_on='Lugar de Compra', right_index=True).sort_values('Precio',ascending=False)

# Facturacion por mes
facturacion_mensual = datos.set_index('Fecha de Compra').groupby(pd.Grouper (freq = 'ME'))['Precio'].sum().reset_index()
facturacion_mensual['Año'] = facturacion_mensual['Fecha de Compra'].dt.year
facturacion_mensual['Mes'] = facturacion_mensual['Fecha de Compra'].dt.month_name()

# Facturacion por categoria
facturacion_cat = datos.groupby('Categoría del Producto')[['Precio']].sum().sort_values('Precio',ascending=False) 

# Cantidad de ventas

cantidad_ventas_estado = datos['Lugar de Compra'].value_counts().to_frame().reset_index().rename(columns={'count':'Cantidad de Ventas'})
cantidad_ventas_estado = datos.drop_duplicates(subset='Lugar de Compra')[['Lugar de Compra','lat','lon']].merge(cantidad_ventas_estado, on='Lugar de Compra').sort_values('Cantidad de Ventas',ascending=False)
cantidad_ventas_mensuale = datos.set_index('Fecha de Compra').groupby(pd.Grouper(freq = 'ME')).count().reset_index()[['Fecha de Compra','Producto']].rename(columns={'Producto':'Cantidad de Ventas'})
cantidad_ventas_mensuale['Año'] = cantidad_ventas_mensuale['Fecha de Compra'].dt.year
cantidad_ventas_mensuale['Mes'] = cantidad_ventas_mensuale['Fecha de Compra'].dt.month_name()
cantidad_ventas_categoria = datos['Categoría del Producto'].value_counts().to_frame().reset_index().rename(columns={'count':'Cantidad de Ventas'})


# Vendedores
vendedores = pd.DataFrame(datos.groupby('Vendedor')['Precio'].agg(['sum','count']))

## Creacion de graficos

fig_fact = px.scatter_geo(fact_ciudades, lat='lat', lon='lon',
                          scope='south america',
                          size='Precio',
                          template='seaborn',
                          hover_name='Lugar de Compra',
                          hover_data ={'lat':False, 'lon':False},
                          title= 'Facturación por ciudad',key=f"plot_{1}")

fig_fact.update_geos(fitbounds="locations")

fig_facturacion_mensual = px.line(facturacion_mensual, x='Mes', y='Precio',
                                  markers = True, range_y=(0,facturacion_mensual.max()),
                                  color='Año', 
                                  line_dash= 'Año',
                                  title = 'Facturación mensual',
                                  key=f"plot_{2}")

fig_facturacion_mensual.update_layout(yaxis_title='Facturación')



fig_facturacion_ciudades = px.bar(fact_ciudades.head(),x='Lugar de Compra',
                                  y='Precio',
                                  text_auto=True,
                                  title='Top ciudades (Facturacion)',
                                  key=f"plot_{3}")

fig_facturacion_ciudades.update_layout(yaxis_title='Facturacion')

fig_cantidad_ventas_estado = px.scatter_geo(cantidad_ventas_estado, lat='lat', lon='lon',
                          scope='south america',
                          size='Cantidad de Ventas',
                          template='seaborn',
                          hover_name='Lugar de Compra',
                          hover_data ={'lat':False, 'lon':False},
                          title= 'Cantidad de ventas por ciudad',key=f"plot_{4}")

fig_cantidad_ventas_estado.update_geos(fitbounds="locations")

fig_cantidad_ventas_mensual = px.line(cantidad_ventas_mensuale, x='Mes', y='Cantidad de Ventas',
                                  markers = True, range_y=(0,cantidad_ventas_mensuale.max()),
                                  color='Año', 
                                  line_dash= 'Año',
                                  title = 'Cantidad de ventas mensual',key=f"plot_{5}")

#fig_facturacion_mensual.update_layout(yaxis_title='Facturación')

fig_top_5_estados_cantidad_ventas = px.bar(cantidad_ventas_estado.head().sort_values('Cantidad de Ventas',ascending=False),
                                            y='Lugar de Compra',
                                            x='Cantidad de Ventas',
                                            text_auto=True,
                                            title=f'Top-5 estados por cantidad de ventas',
                                            color='Lugar de Compra',
                                            color_discrete_sequence=px.colors.qualitative.Bold,,key=f"plot_{6}")


fig_cantidad_ventas_categoria = px.bar(cantidad_ventas_categoria.head().sort_values('Cantidad de Ventas',ascending=False),
                                            y='Categoría del Producto',
                                            x='Cantidad de Ventas',
                                            text_auto=True,
                                            title=f'Top-5 Categorias por cantidad de Ventas',
                                            color='Categoría del Producto',
                                            color_discrete_sequence=px.colors.qualitative.G10,key=f"plot_{7}")



fig_facturacion_cat = px.bar(facturacion_cat,
                             text_auto=True,
                             title='Facturacion por categoria')

fig_facturacion_cat.update_layout(yaxis_title='Facturacion')


####

tab1, tab2, tab3 =st.tabs(['Facturación','Cantidad de ventas','Vendedores'])

with tab1:

    col1, col2 = st.columns(2)

    with col1:
        st.metric('Facturación', formato_numero(datos['Precio'].sum()),'COP')
        st.plotly_chart(fig_fact, use_container_width=True)
        st.plotly_chart(fig_facturacion_ciudades, use_container_width=True)
    with col2:
        st.metric('Cantidad de Ventas', formato_numero(datos.shape[0]))
        st.plotly_chart(fig_cantidad_ventas_mensual, use_container_width=True)
        st.plotly_chart(fig_facturacion_cat, use_container_width=True)
    #st.dataframe(datos)
    
with tab2:
    
    col1, col2 = st.columns(2)

    with col1:
        st.metric('Facturación', formato_numero(datos['Precio'].sum()),'COP')
        st.plotly_chart(fig_cantidad_ventas_estado, use_container_width=True)
        st.plotly_chart(fig_top_5_estados_cantidad_ventas, use_container_width=True)
    with col2:
        st.metric('Cantidad de Ventas', formato_numero(datos.shape[0]))
        st.plotly_chart(fig_cantidad_ventas_mensual, use_container_width=True)    
        st.plotly_chart(fig_cantidad_ventas_categoria,use_container_width=True)
        
        
with tab3:
    ct_vendedores = st.number_input('Cantidad de vendedores',2,10,5)
    sum_up_variable = vendedores[['sum']].sort_values('sum').head(ct_vendedores)
    sum_up_variable_count = vendedores[['count']].sort_values('count').head(ct_vendedores)
    col1, col2 = st.columns(2)

    with col1:
        st.metric('Facturación', formato_numero(datos['Precio'].sum()),'COP')
        fig_facturacion_vendedores = px.bar(sum_up_variable,
                                            x='sum',
                                            y=sum_up_variable.index,
                                            text_auto=True,
                                            title=f'Top {ct_vendedores} vendedores (Facturacion)',key=f"plot_{8}")
        st.plotly_chart(fig_facturacion_vendedores)
    
    with col2:
        st.metric('Cantidad de Ventas', formato_numero(datos.shape[0]))
        
        fig_cantidad_ventas = px.bar(sum_up_variable_count,
                                            x='count',
                                            y=sum_up_variable_count.index,
                                            text_auto=True,
                                            title=f'Top {ct_vendedores} vendedores (Cantidad de ventas)',key=f"plot_{9}")
        st.plotly_chart(fig_cantidad_ventas)