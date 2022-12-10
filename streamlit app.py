#!/usr/bin/env python
# coding: utf-8

# In[2]:


import altair as alt
import pandas as pd
import streamlit as st
from typing import List


st.title('Demo')

def comma_to_dot(df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
    for col in columns:
        df = df.assign(**{col: lambda df: df[col].str.replace(',', '.').astype(float)})
    return df

data = (pd.read_csv('../data/datos-metereologicos-2021.csv')
    .assign(**{'fecha': lambda df: pd.to_datetime(df['fecha'])})
    .assign(**{'prec': lambda df: df['prec'].replace({'Ip': 0, 'Acum': None})})
    .pipe(comma_to_dot, columns=['tmed', 'prec', 'tmin', 'tmax', 'velmedia', 'racha', 'sol', 'presMax', 'presMin'])
    .loc[lambda df: df.isin(['Acum']).any(axis=1)]
)

if st.checkbox('Mostrar datos'):
    data

provincias = st.sidebar.multiselect('Provincias', data['provincia'].sort_values().unique())
time_granularity = st.selectbox('Nivel de granularidad', ['Día', 'Semana', 'Mes'])
show_points = st.checkbox('Mostrar puntos')

tmed_data = (data
    .assign(**{'Día': lambda df: df['fecha']})
    .assign(**{'Semana': lambda df: df['fecha'].dt.to_period('W').dt.start_time})
    .assign(**{'Mes': lambda df: df['fecha'].dt.to_period('m').dt.start_time})
    .loc[lambda df: df['provincia'].isin(provincias)]
    .groupby(['provincia', time_granularity], as_index=False)
    .agg({'tmed': 'mean'})
    .assign(**{'tmed_str': lambda df: df['tmed'].apply(lambda x: f'{x:,.2f} ºC')})
)

tmed_chart = alt.Chart(tmed_data, title='Temperatura media (ºC)').mark_line(point=show_points).encode(
    x=alt.X(time_granularity, axis=alt.Axis(title='')),
    y=alt.Y('tmed', axis=alt.Axis(title='')),
    color=alt.Color('provincia', title=''),
    tooltip=[time_granularity, 'provincia', 'tmed', 'tmed_str'],
)

st.altair_chart(tmed_chart, use_container_width=True)


# In[ ]:




