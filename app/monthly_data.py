import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np

st.set_page_config(layout='wide')

conn = st.connection('airflow_db')

hide_decoration_bar_style = '''
    <style>
        header {visibility: hidden;}
    </style>
'''
st.markdown(hide_decoration_bar_style, unsafe_allow_html=True)

# date selectbox
dates = conn.query('''
                      select distinct date
                      from apt_details_raw
                      ''').values.reshape(-1)
dates = list(map(lambda x: str(x).replace('T',' '), dates))
dates = reversed(dates)
date = st.sidebar.selectbox(
    label='Date:', options=dates, format_func=lambda x: x[:10])

# gettin cities
with open('cities.txt','r') as file:
    cities = file.readlines()
cities = [x.strip() for x in cities]

# cities selectbox
city = st.sidebar.selectbox(
    label='City:', options=cities)

# getting data
query = f'''
        select
            id,
            date,
            city,
            localization_x,
            localization_y,
            market,
            area,
            price_of_sqm
        from apt_details
        where date='{date}'
        '''
if city!='All':
    query += f" and city='{city}'"

df = conn.query(query, index_col='id')

# home button
st.link_button('Home', 'https://piotrpietka.pl')

# tittles
st.title('Apartment market monthly data')
st.subheader(f'Date: {date[:10]}, City: {city}')

# price distribution
fig = px.histogram(df, x='price_of_sqm', color='market', log_x=False,
                   barmode='group', nbins=50,
                   title='Price of sq m distribution',
                   color_discrete_map={
                       'aftermarket': px.colors.qualitative.D3_r[0],
                       'primary_market': px.colors.qualitative.D3_r[1]})
st.plotly_chart(fig, theme='streamlit', use_container_width=True)

# area distribution
fig = px.histogram(df, x='area', color='market', log_x=False,
                   barmode='group', nbins=50, title='Area distribution',
                   color_discrete_map={
                       'aftermarket': px.colors.qualitative.D3_r[0],
                       'primary_market': px.colors.qualitative.D3_r[1]})
st.plotly_chart(fig, theme='streamlit', use_container_width=True)

# price of sqm in relation to area
df_bins = df[['area','price_of_sqm','market']].copy()
df_bins['bins'] = pd.cut(df_bins.area,
                         bins=np.linspace(df_bins.area.min(),
                                          df_bins.area.max(), 15))
df_bins = df_bins[['area','price_of_sqm','market','bins']]\
    .groupby(['bins','market']).median().reset_index()

fig = px.line(df_bins, x='area', y='price_of_sqm', color='market',
              title='Median of price of sq m in relation to area',
              color_discrete_map={
                       'aftermarket': px.colors.qualitative.D3_r[0],
                       'primary_market': px.colors.qualitative.D3_r[1]})
st.plotly_chart(fig, theme='streamlit', use_container_width=True)

# price boxplots
medians = df[df.city.isin(cities)][['city','price_of_sqm']]\
    .groupby('city').median()
medians = medians.sort_values('price_of_sqm', ascending=False)
fig = px.box(df[df.city.isin(cities)], x='city', y='price_of_sqm',
             color='market', title='Prices of sq m in main cities',
             color_discrete_map={
                       'aftermarket': px.colors.qualitative.D3_r[0],
                       'primary_market': px.colors.qualitative.D3_r[1]},
             points=False, category_orders={'city': medians.index}, height=600)
st.plotly_chart(fig, theme='streamlit', use_container_width=True)

# price of sqm map
zoom = 5
if city!='All':
    zoom = 10

px.set_mapbox_access_token(st.secrets.mapbox.token)
fig = px.scatter_mapbox(df,
                        lat='localization_y',
                        lon='localization_x',
                        hover_name="city",
                        zoom=zoom,
                        color='price_of_sqm',
                        size_max=20,
                        opacity=1,
                        color_continuous_scale=px.colors.sequential.Jet,
                        height=600,
                        title='Prices of sq m')
fig.update_layout(mapbox_style='light')
st.plotly_chart(fig, theme='streamlit', use_container_width=True)

# home button
st.link_button('Home', 'https://piotrpietka.pl')
