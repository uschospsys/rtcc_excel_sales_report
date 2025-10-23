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

unit_options = {
    0: "RTCC Food Court",
    1: "Seeds Mktplace",
    2: "USC Cafes"
}

cafe_options = {
    0: "UPC Trojan Grounds Illy",
    1: "Coffee Bean & Tea Leaf",
    2: "W. Annenberg Cafe",
    3: "HSC Illy",
    4: "Tutor Hall Cafe"
}

col1, col2, col3, col4 = st.columns([2, 1, 2, 2])
with col1:
    unit_selection = st.pills(
        "Select the Unit for this report?",
        options = unit_options,
        format_func = lambda opt: unit_options[opt],
        selection_mode = 'single',
        default = 0
    )
    if unit_selection == 2:
        cafes_unit_selection = st.pills(
            "Select the Cafes for this report?",
            options = cafe_options,
            format_func = lambda opt: cafe_options[opt],
            selection_mode = 'multi',
            default = None
        )

with col2:
    show_patrons_choice = st.segmented_control(
        "Show Patron Counts?",
        options = ["No", "Yes"],
        selection_mode = "single",
        default = "No"
    )

with col3:
    split_kiosks_choice = st.radio(
        "Display Non-MO sales as?",
        ["Merged", "Split"],
        captions = [
            "[Kiosks + Registers]",
            "[Kiosks] and [Registers]"
        ],
        horizontal = True
    )

with col4:
    hide_units = st.select_slider(
        "Units Display?",
        options = ["Hide Units with no Sales", "Show all Units"]
    )

# show_patrons = col2.toggle("Show Patrons Count in report?")
unit_name = None if unit_selection is None else unit_options[unit_selection]
output_file_name = st.text_input("What's the output file name?", f"{unit_name} Mobile Ordering Report.xlsx")

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

        # Filter for USC Cafes
        if unit_name == 'USC Cafes':
            cafes_filter = df['location_name'].isin([cafe_options[x] for x in cafes_unit_selection])
            df = df[cafes_filter]
            
        unique_units = np.unique(df["Unit"])
        st.divider()
        st.write(f"Found {len(unique_units)} Units in {unit_name}")
        with st.expander(f"View Unique {unit_name} Units"):
            st.write(unique_units.tolist())

        split_kiosks = True if split_kiosks_choice == "Split" else False
        show_patrons = True if show_patrons_choice == "Yes" else False
        
        final_sales_data, final_trxns_data = aggregate_sales(df, unique_units, show_patrons=show_patrons, split_kiosks=split_kiosks)

        final_sales_data = post_process_totals(final_sales_data, hide_units, split_kiosks)
        if show_patrons:
            final_trxns_data = post_process_totals(final_trxns_data, hide_units, split_kiosks)
        
        output = export_to_excel_report(
            final_sales_data,
            final_trxns_data,
            filename = output_file_name,
            unit_name = unit_name,
            show_patrons = show_patrons,
            split_kiosks = split_kiosks
        )
    
        st.download_button(
            label = "Download Report",
            data = output,
            file_name = output_file_name,
            mime = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )