import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np
import colorsys

st.set_page_config(page_title='apartment market trends', layout='wide')

st.cache_data.clear()

conn = st.connection('airflow_db')

hide_decoration_bar_style = '''
    <style>
        header {visibility: hidden;}
    </style>
'''
st.markdown(hide_decoration_bar_style, unsafe_allow_html=True)

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
        '''
if city!='All':
    query += f" where city='{city}'"

df = conn.query(query, index_col='id')
df.date = df.date.dt.strftime('%Y-%m-%d')

# home button
st.link_button('Home', 'https://piotrpietka.pl')

# tittles
st.title('Apartment market trends')
st.subheader(f':gray[City:] {city}')

# median prices
df_med= df[['date','price_of_sqm']].groupby('date').median().reset_index()
fig = px.line(df_med, x='date', y='price_of_sqm',
              title='Median price of sq m')
fig.update_traces(line_color=px.colors.qualitative.D3[0])
st.plotly_chart(fig, theme='streamlit', use_container_width=True)

# new apartments market share
df_share = df[['date','market','area']].pivot_table(index='date',
                                                    columns='market',
                                                    values='area',
                                                    aggfunc='count')
df_share.reset_index(inplace=True)
df_share['new_apt_share'] = df_share.primary_market / \
    (df_share.aftermarket + df_share.primary_market)

fig = px.line(df_share, x='date', y='new_apt_share',
              title='New apartments market share')
fig.update_traces(line_color=px.colors.qualitative.D3[1])
st.plotly_chart(fig, theme='streamlit', use_container_width=True)

# price in relation to area
df_list = []
for date in reversed(df.date.unique()):
    temp = df[df.date==date][['area','price_of_sqm']].copy()
    temp['bins'] = pd.cut(temp.area,
                            bins=np.linspace(temp.area.min(),
                                            temp.area.max(), 15))
    temp = temp[['area','price_of_sqm','bins']]\
        .groupby(['bins']).median().reset_index()
    temp['date'] = date
    df_list.append(temp)
df_bins = pd.concat(df_list)

def get_n_hexcol(n=5):
    hsv_tuples = [(0.35, 1, x * 1 / n) for x in range(n-1, -1, -1)]
    hex_out = []
    for rgb in hsv_tuples:
        rgb = map(lambda x: int(x * 255), colorsys.hsv_to_rgb(*rgb))
        hex_out.append('#%02x%02x%02x' % tuple(rgb))
    return hex_out

fig = px.line(df_bins, x='area', y='price_of_sqm', color='date',
              title='Median of price of sq m in relation to area',
              color_discrete_sequence=get_n_hexcol(df_bins.date.nunique()))
st.plotly_chart(fig, theme='streamlit', use_container_width=True)

# price box plot
fig = px.box(df, x='date', y='price_of_sqm',
             color='market',title='Prices of sq m',
             color_discrete_map={
                       'aftermarket': px.colors.qualitative.D3_r[0],
                       'primary_market': px.colors.qualitative.D3_r[1]},
             points=False, height=600)
st.plotly_chart(fig, theme='streamlit', use_container_width=True)

# home button
st.link_button('Home', 'https://piotrpietka.pl')
