import streamlit as st
import numpy as np
import pandas as pd

st.set_page_config(layout="wide")

chart_data = pd.DataFrame(
     np.random.randn(20, 3),
     columns=['a', 'b', 'c'])

st.line_chart(chart_data)

# Add a selectbox to the sidebar:
add_selectbox = st.sidebar.selectbox(
    'How would you like to be contacted?',
    ('Email', 'Home phone', 'Mobile phone')
)

col1,col2 = st.columns([1,3])

col1.line_chart(chart_data)
col2.line_chart(chart_data)
