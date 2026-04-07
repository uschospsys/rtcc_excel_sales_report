# pages/2_RTCC_MO_Sales

import streamlit as st
import numpy as np
import pandas as pd
import datetime

from utils.mo_processing import (
    aggregate_sales,
    post_process_totals
)
from utils.giant_report.mo_all_units_residential_processing import (
    process_residential_data_bb, 
    process_residential_data_sql,
    process_residential_data
)

from utils.giant_report.mo_all_units_retail_processing import process_retail_data
from utils.giant_report.mo_all_units_preprocessing import preprocess_all_units_raw
from utils.giant_report.mo_all_units_tender_processing import generate_tender_report
from utils.mo_excel_writer import export_to_excel_report

from models.Tender_Data import Tender_Data
from models.Sales_Data import Sales_Data
from models.Giant_Report import Giant_Report
from models.Retail_All_Data import Retail_All_Data

@st.cache_data
def load_excel(file, sheet_name=[0]):
    return pd.read_excel(file, sheet_name=sheet_name,engine="calamine")

@st.cache_data
def preprocess_excel(df):
    return preprocess_all_units_raw(df)

# Set Session State Variables here
session_state_vars = ["gr", "retail_all_data", "curr_res_df", "summ_res_df"]
for var in session_state_vars:
    if var not in st.session_state:
        st.session_state[var] = None

st.set_page_config(page_title="Mobile-Ordering Giant Report", layout = "wide")
st.title("Mobile Ordering Sales Comparison - Giant Report")

col11, col12, col13, col14 = st.columns([1,2,1,1])

this_year = datetime.date.today().year
this_month = datetime.date.today().month
    
months = ('January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December')

month_input = col13.selectbox("Report Month", months)
year_input = col14.number_input("Report Year", min_value=1900, max_value=this_year, value=this_year)
output_file_name = col12.text_input("What's the output file name?", f"Hospitality Mobile-Ordering {month_input} {year_input} Report.xlsx")
show_patrons_choice = col11.segmented_control(
    "Show Patron Counts?",
    options = ["No", "Yes"],
    selection_mode = "single",
    default = "No",
    disabled = True
)

st.divider()

df = pd.DataFrame()
df2 = pd.DataFrame()

st.markdown(f"#### Retail Raw Data")
up_col1, up_col2 = st.columns([2, 2])
with up_col1:
    
    # Upload Raw Excel Data File
    uploaded_file = st.file_uploader(f"Upload Raw Sales Excel File - {month_input} {year_input}", type=["xls", "xlsx"])
    
    if uploaded_file:
        with st.spinner(f"Reading Retail Raw Excel File...", show_time=True):
            df = load_excel(uploaded_file)
        with st.spinner(f"Pre-Processing Retail Raw Excel File...", show_time=True):
            df = preprocess_excel(df[0])
            
        st.success(f"Retail Excel File ready for processing!")

with up_col2:
    uploaded_comparison_file = st.file_uploader(f"Upload Comparison Sales Excel File - {month_input} {year_input-1}", type=["xls", "xlsx"])
    if uploaded_comparison_file:
        with st.spinner(f"Reading Retail Comparison Raw Excel File...", show_time=True):
            df2 = load_excel(uploaded_comparison_file)
        with st.spinner(f"Pre-Processing Retail Comparison Raw Excel File...", show_time=True):
            df2 = preprocess_excel(df2[0])
        st.success(f"Retail Comparison Excel File ready for processing!")

_, button_col0, button_col1, _ = st.columns([3,3,3,3])
if button_col0.button("Clear Uploaded Files", type="secondary", icon=":material/close:", key="Retail Clear"):
    load_excel.clear()
    preprocess_excel.clear()

if button_col1.button("Process Retail Data", type="primary", icon=":material/autorenew:", key="Retail Processing"):
    if df.empty or df2.empty:
        st.warning("Please upload a valid excel file first! Here")
        # gr, retail_all_data = None, None
    else:
        st.session_state.gr, st.session_state.retail_all_data = process_retail_data(df, df2)
        st.success("Completed Processing all Retail Sales")

st.divider()

st.markdown(f"#### Residential Raw Data")
res_up_col1, res_up_col2 = st.columns([2, 2])

with res_up_col1:
    residential_bb_file = st.file_uploader(f"Upload Res. Blackboard Excel File", type=["xls", "xlsx"])
    if residential_bb_file:
        with st.spinner(f"Reading Residential Blackboard Excel File...", show_time=True):
            resi_bb_df = load_excel(residential_bb_file, sheet_name=[0,1])
        st.success(f"Residential Blackboard Excel File ready for processing!")
with res_up_col2:
    residential_sql_file = st.file_uploader(f"Upload Res. SQL Excel File", type=["xls", "xlsx"])
    if residential_sql_file:
        with st.spinner(f"Reading Residential SQL (Transact) Excel File...", show_time=True):
            resi_sql_file = load_excel(residential_sql_file, sheet_name=[0,1])
        st.success(f"Residential SQL (Transact) Excel File ready for processing!")

_, col1, col2, _ = st.columns([3,3,3,3])
if col1.button("Clear Uploaded Files", type="secondary", icon=":material/close:", key="Residential Clear"):
    load_excel.clear()
    preprocess_excel.clear()

if col2.button("Process Residential Data", type="primary", icon=":material/autorenew:", key="Residential Processing"):
    if not resi_bb_df or not resi_sql_file:
        st.warning("Please upload a valid Blackboard Residential and/or SQL Residential Excel File")
    else:
        bb_df = process_residential_data_bb(resi_bb_df)
        sql_df = process_residential_data_sql(resi_sql_file)

        st.session_state.curr_res_df, st.session_state.summ_res_df = process_residential_data(bb_df, sql_df, month_input, year_input)
        st.success("Completed Processing all Residential Sales")

st.divider()

# final_gr_ready = (
#     st.session_state.gr is not None and
#     st.session_state.retail_all_data is not None and    
# )

final_gr_ready = all([st.session_state[var] is not None for var in session_state_vars])

if st.button("Generate Final Giant Report", type="primary", icon=":material/analytics:", key="Final Giant Report Generator", disabled=not final_gr_ready):
    if df.empty or df2.empty:
        st.warning("Please upload a valid excel file first!")
    else:
        show_patrons = True if show_patrons_choice == "Yes" else False
        
        # df_raw = df.copy()
        # df2_raw = df2.copy()
        # # res_df_raw = res_df.copy()

        # all_locations = df_raw['location_name']
        # residential_locations = ['EVK Residential', 'PIRC Residential', 'University VillageResidential']
        # retail_locations = list(set(all_locations) - set(residential_locations))

        # all_locations2 = df2_raw['location_name']
        # retail_locations2 = list(set(all_locations2) - set(residential_locations))

        # # Data Clean-up
        # df = df[df["item_number"] != "DISCOUNT"]
        # df2 = df2[df2["item_number"] != "DISCOUNT"]

        # # Remove Residential Rows from the sales dfs
        # df = df[~df['location_name'].isin(residential_locations)]
        # df2 = df2[~df2['location_name'].isin(residential_locations)]
        
        # unique_units1 = np.unique(df["Unit"])
        # st.divider()
        # st.write(f"Found {len(unique_units1)} Units in USC Hospitality")
        # with st.expander(f"View Unique USC Hospitality Units"):
        #     st.write(unique_units1.tolist())

        # unique_units2 = np.unique(df2["Unit"])

        # gr = Giant_Report(df, df2)

        # # Unit Sales
        # sales_data1 = gr.aggregate_giant_sales_data()
        # sales_data2 = gr.aggregate_giant_sales_data(is_current=False)

        # st.write("=============")
        # # st.dataframe(sales_data2.final_sales)
        
        # # Tender Sales
        # final_tender_data1 = generate_tender_report(df_raw, retail_locations)
        # final_tender_data2 = generate_tender_report(df2_raw, retail_locations2)
        # final_tender_data3 = generate_tender_report(df_raw, residential_locations)
        # final_tender_data4 = generate_tender_report(df2_raw, residential_locations)

        # # st.dataframe(final_tender_data3.final_tender_sales)

        st.dataframe(st.session_state.retail_all_data.sales_data1.final_sales)
        
        output = st.session_state.gr.export_to_excel(
            st.session_state.retail_all_data.sales_data1, 
            st.session_state.retail_all_data.sales_data2,
            st.session_state.retail_all_data.tender_data1, 
            st.session_state.retail_all_data.tender_data2, 
            st.session_state.retail_all_data.res_tender_data1, 
            st.session_state.retail_all_data.res_tender_data2,
            st.session_state.curr_res_df, 
            st.session_state.summ_res_df,
            output_file_name, month_input, year_input
        )
        
        # output = gr.export_to_excel(
        #     sales_data1, sales_data2,
        #     final_tender_data1, final_tender_data2, final_tender_data3, final_tender_data4,
        #     output_file_name, month_input, year_input
        # )
        
        # output = export_to_excel_report(
        #     final_sales_data,
        #     final_trxns_data,
        #     filename = output_file_name,
        #     unit_name = unit_name,
        #     month = f'{month_input} {year_input}',
        #     show_patrons = show_patrons,
        #     split_kiosks = split_kiosks,
        #     giant_report = giant_report,
        #     tender_data=final_tender_data
        # )
    
        st.download_button(
            label = "Download Report",
            data = output,
            file_name = output_file_name,
            mime = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

        # Delete session state to make sure memory overload doesn't happen.
        del st.session_state.gr
        del st.session_state.retail_all_data
        del st.session_state.curr_res_df
        del st.session_state.summ_res_df

        