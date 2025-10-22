# pages/2_RTCC_MO_Sales

import streamlit as st
import numpy as np
import pandas as pd

from utils.mo_processing import (
    aggregate_sales,
    post_process_totals
)

from utils.mo_excel_writer import export_to_excel_report

@st.cache_data
def load_excel(file):
    return pd.read_excel(file)

st.set_page_config(page_title="Mobile-Ordering Sales", layout = "wide")
st.title("Mobile Ordering Sales Comparison")

col1, col2, col3 = st.columns([1, 1, 2])
unit_name = col1.selectbox(
    "Select the Unit for this report?",
    ("RTCC Food Court", "Seeds Mktplace")
)
show_patrons = col2.selectbox(
    "Show Patron Counts in report?",
    (True, False), index = 1
)
# show_patrons = col2.toggle("Show Patrons Count in report?")

output_file_name = col3.text_input("What's the output file name?", f"{unit_name} September 2025 - Mobile Ordering Split Report.xlsx")
st.success(f"The current output file name is: {output_file_name}")

st.divider()

# Upload Raw Excel Data File
uploaded_file = st.file_uploader("Upload Raw Excel File", type=["xls", "xlsx"])
    
df = pd.DataFrame()

if uploaded_file:
    with st.spinner(f"Reading {unit_name} Raw Excel File...", show_time=True):
        df = load_excel(uploaded_file)
    st.success(f"Done reading {unit_name} Raw Excel File!")

col1, col2, _ = st.columns([1,1,5])
if col1.button("Clear File"):
    load_excel.clear()
    
if col2.button("Generate Report"):
    if df.empty:
        st.warning("Please upload a valid raw excel file first!")
    else:
        # Data Clean-up
        df = df[df["item_number"] != "DISCOUNT"]
    
        unique_units = np.unique(df["Unit"])
        st.divider()
        st.write(f"Found {len(unique_units)} Units in {unit_name}")
        with st.expander(f"View Unique {unit_name} Units"):
            st.write(unique_units.tolist())
    
    
        # Split into Mobile and non-Mobile (Kiosk + Registers)
        mo_df = df[df["POS"] == "Mobile"]
        oth_df = df[df["POS"] != "Mobile"]
    
        final_sales_data, final_trxns_data = aggregate_sales(mo_df, oth_df, unique_units, show_patrons=True)

        final_sales_data = post_process_totals(final_sales_data)
        if show_patrons:
            final_trxns_data = post_process_totals(final_trxns_data)
        
        output = export_to_excel_report(
            final_sales_data,
            final_trxns_data,
            filename = output_file_name,
            unit_name = unit_name,
            show_patrons = show_patrons
        )
    
        st.download_button(
            label = "Download Report",
            data = output,
            file_name = output_file_name,
            mime = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )