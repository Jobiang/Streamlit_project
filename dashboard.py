import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import math
import seaborn as sns; sns.set()
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px

st.title('DASHBOARD\nSmart People Platform')
st.sidebar.title('DASHBOARD\nSmart People Platform')

DATA_URL = ('Dashboard.xlsx')

@st.cache(persist=True)
def load_data():
    data = pd.read_excel(DATA_URL)
    data['Fecha de Compra'] = pd.to_datetime(data['Fecha de Compra'], format='%d-%m-%Y')
    return data

data = load_data()

st.subheader('Conversions: Approved loans Vs. Applications')
st.sidebar.subheader('Conversions: \nApproved loans Vs. Applications')

# Aprobados y denegados: clientes
n_rows = data.shape[0]
labels = ['Approved','Denied']
labels_perc = [100*data.is_approved.sum()/n_rows, 100 - 100*data.is_approved.sum()/n_rows]

# Aprobados y denegados: clientes
n_rows = data.shape[0]
labels_cap = ['Approved (S/.)','Denied (S/.)']
labels_cap_perc = [data[data.is_approved==True]['Precio Contado'].sum(), 
                   data[data.is_approved==False]['Precio Contado'].sum()]

if not st.sidebar.checkbox('Hide Conversions', False):
    # Create subplots: use 'domain' type for Pie subplot
    fig = make_subplots(rows=1, cols=2, specs=[[{'type':'domain'}, {'type':'domain'}]])
    fig.add_trace(go.Pie(labels=labels, values=labels_perc, name="Approved Loans"),
                1, 1)
    fig.add_trace(go.Pie(labels=labels_cap, values=labels_cap_perc, name="Approved Sells"),
                1, 2)

    # Use `hole` to create a donut-like pie chart
    fig.update_traces(hole=.45, hoverinfo="label+percent+name")

    fig.update_layout(
        # Add annotations in the center of the donut pies.
        annotations=[dict(text='Approved Clients', x=0.03, y=1.05, font_size=20, showarrow=False),
                    dict(text='Approved Capital', x=0.95, y=1.05, font_size=20, showarrow=False)])
    st.plotly_chart(fig)

# Variables globales
auxdf = data.copy()
inversion = auxdf[auxdf.is_approved==True]['Precio Contado'].sum()
auxdf['Total_a_pagar'] = auxdf['Pago inicial'] + auxdf['# Cuotas']*auxdf['Valor Cuotas']
ingreso_esperado = auxdf[auxdf.is_approved==True]['Total_a_pagar'].sum()
auxdf['Morosidad'] = auxdf['Total_a_pagar'] - auxdf['Pago Acumulado']
morosidad = auxdf[auxdf.is_approved==True]['Morosidad'].sum()

st.subheader('Liquidity Indicators')
st.sidebar.subheader('Liquidity Indicators')

if not st.sidebar.checkbox('Hide Indicators', False):
    fig = go.Figure(go.Bar(
            x=[inversion, ingreso_esperado, morosidad],
            y=['Inversion', 'Expected Income', 'Default'],
            orientation='h',
            marker_color='darkgreen'))
    st.plotly_chart(fig)

# Default de acuerdo al sku vendido
st.subheader('Paid/Default by SKU')
st.sidebar.subheader('Paid/Default by SKU')
select = st.sidebar.selectbox('Visualization Type', ['Stacked Bars','Unstacked Bars'], key=1)

condicion = auxdf.is_approved==True
auxdf_00 = auxdf[condicion].groupby(['SKU'])[['is_default','is_paid']].sum().unstack(level=1).reset_index()
auxdf_00.columns = ['State','SKU','Units']

if not st.sidebar.checkbox('Hide Paid/Default', False):
    if select == 'Stacked Bars':
        fig = px.bar(auxdf_00, x="SKU", y="Units", color="State")
        st.plotly_chart(fig)
    else:
        labels = ['CELL A','CELL B','CELL C']
        fig = go.Figure()
        fig.add_trace(go.Bar(x=labels, y=[18, 12, 6],
                        base=[-18,-12,-6],
                        marker_color='darkred',
                        name='Default'))
        fig.add_trace(go.Bar(x=labels, y=[24, 30, 30],
                        base=0,
                        marker_color='darkgreen',
                        name='Paid'
                        ))
        fig.update_layout(showlegend=True)
        st.plotly_chart(fig)

# Ejemplo de Data en tabla
st.subheader('Clients Information')
st.sidebar.subheader('Clients Information')
select = st.selectbox('Client State', ['Paid','Default'])

features = ['Cliente ID','Fecha de Compra','SKU','# Cuotas','Tipo de Cuota','# Cuotas Pagadas','Pago Acumulado']

if not st.sidebar.checkbox('Hide Clients', False):
    if select == 'Paid':
        st.write(data.query('is_paid >= 1')[features].sort_values(by=['Fecha de Compra'], ascending=False).dropna(how='any'))
    else:
        st.write(data.query('is_default >= 1')[features].sort_values(by=['Fecha de Compra'], ascending=False).dropna(how='any'))

