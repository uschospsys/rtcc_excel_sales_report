# pages/4_RTCC_Patron_Counts

import streamlit as st
import numpy as np
import pandas as pd
import datetime

from utils.giant_report.mo_all_units_preprocessing import preprocess_all_units_raw

@st.cache_data
def load_excel(file, sheet_name=[0]):
    return pd.read_excel(file, sheet_name=sheet_name, engine="calamine")


@st.cache_data
def preprocess_excel(df):
    # Retain only RTCC Food Court Units
    df = df[df["location_name"] == "RTCC Food Court"]
    df = df[df["item_number"] != "DISCOUNT"]
    return preprocess_all_units_raw(df)

# Set Session State Variables here
session_state_vars = ["df"]
for var in session_state_vars:
    if var not in st.session_state:
        st.session_state[var] = None
        

st.set_page_config(page_title="[WIP] RTCC Food Court - Patron Counts", layout = "wide")
st.title("[WIP] RTCC Food Court - Patron Counts")

col12, col13, col14 = st.columns([2,1,1])

this_year = datetime.date.today().year
this_month = datetime.date.today().month
    
months = ('January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December')

month_input = col13.selectbox("Report Month", months, index=None, placeholder='Select the Report Month')
year_input = col14.number_input("Report Year", min_value=1900, max_value=this_year, value=this_year)
output_file_name = col12.text_input("What's the output file name?", f"RTCC Food Court Patron Counts {month_input} {year_input} Report.xlsx")


st.divider()

df = pd.DataFrame()

st.markdown(f"#### RTCC Food Court Raw Data")

# Upload Raw Excel Data File
uploaded_file = st.file_uploader(f"Upload Raw RTCC Sales Excel File - {month_input} {year_input}", type=["xls", "xlsx"])

if uploaded_file:
    with st.spinner(f"Reading Retail Raw Excel File...", show_time=True):
        df = load_excel(uploaded_file)
    with st.spinner(f"Pre-Processing Retail Raw Excel File...", show_time=True):
        st.session_state.df = preprocess_excel(df[0])
        
    st.success(f"Retail Excel File ready for processing!")

st.divider()

final_ready = all([st.session_state[var] is not None for var in session_state_vars])
if st.button('Generate Report', type = 'primary', icon=":material/analytics:", key="Final Giant Report Generator", disabled=not final_ready):
    st.dataframe(st.session_state.df.head(10))


    trxn_report_df = st.session_state.df.pivot_table(
        index='Unit', 
        columns='Meal Period', 
        values='item_qty', 
        aggfunc='sum', 
        fill_value=0,
        margins=True,       # Adds a "Total" row and column
        margins_name='Total'
    )
    
    # Optional: Reorder columns to follow chronological order
    # (Only do this if your columns aren't already in order)
    order = ['Breakfast', 'Lunch', 'Dinner', 'Total']
    trxn_report_df = trxn_report_df.reindex(columns=order)
    
    st.dataframe(trxn_report_df)


    sales_report_df = st.session_state.df.pivot_table(
        index='Unit', 
        columns='Meal Period', 
        values='item_price', 
        aggfunc='sum', 
        fill_value=0,
        margins=True,       # Adds a "Total" row and column
        margins_name='Total'
    )
    
    # Optional: Reorder columns to follow chronological order
    # (Only do this if your columns aren't already in order)
    order = ['Breakfast', 'Lunch', 'Dinner', 'Total']
    sales_report_df = sales_report_df.reindex(columns=order)
    
    st.dataframe(sales_report_df)

    # You may need to install openpyxl if you haven't: !pip install openpyxl

    with pd.ExcelWriter('Patron_Count_Report.xlsx', engine='openpyxl') as writer:
        # Sheet 1: The Summary Report
        trxn_report_df.to_excel(writer, sheet_name='Patron Count Summary')
        sales_report_df.to_excel(writer, sheet_name='Sales Summary')
        
        # Sheet 2: The Raw Data (Optional, but helpful for audits)
        # We use index=False here to keep the raw data clean
        st.session_state.df.to_excel(writer, sheet_name='Source Data', index=False)
    
    print("Report saved successfully!")

