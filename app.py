# app.py

import streamlit as st

st.set_page_config(page_title="hospsys-bdo", layout="wide")
st.title("Hospsys BDO Home")

st.markdown("""
Welcome to the USC Hospitality System - Business Data Operations - Home!  

The following report automation are currently supported.
You can also use the sidebar to navigate.
""")

col1, col2 = st.columns([1,1], border=True)

with col1:
    st.write("RTCC Food Court and Seeds Marketplace Unit-wise Category Split Report")

with col2:
    st.write("Mobile Ordering Sales Comparison Report")