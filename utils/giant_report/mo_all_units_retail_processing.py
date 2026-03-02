# utils/giant_report/mo_all_units_retail_processing.py

import numpy as np
import pandas as pd

from utils.giant_report.mo_all_units_tender_processing import generate_tender_report
from models.Giant_Report import Giant_Report
from models.Retail_All_Data import Retail_All_Data

def process_retail_data(df, df2):

    df_res = df.copy()
    df2_res = df2.copy()
    
    
    all_locations = df_res['location_name']
    residential_locations = ['EVK Residential', 'PIRC Residential', 'University VillageResidential']
    retail_locations = list(set(all_locations) - set(residential_locations))

    all_locations2 = df2_res['location_name']
    retail_locations2 = list(set(all_locations2) - set(residential_locations))


    # Data Clean Up
    df = df[df["item_number"] != "DISCOUNT"]
    df2 = df2[df2["item_number"] != "DISCOUNT"]

    # Remove Residential Rows from the sales dfs
    df = df[~df['location_name'].isin(residential_locations)]
    df2 = df2[~df2['location_name'].isin(residential_locations)]



    gr = Giant_Report(df, df2)

    # Unit Sales
    sales_data1 = gr.aggregate_giant_sales_data()
    sales_data2 = gr.aggregate_giant_sales_data(is_current=False)

    # Tender Sales
    final_tender_data1 = generate_tender_report(df_res, retail_locations)
    final_tender_data2 = generate_tender_report(df2_res, retail_locations2)
    final_tender_data3 = generate_tender_report(df_res, residential_locations)
    final_tender_data4 = generate_tender_report(df2_res, residential_locations)


    retail_all_data = Retail_All_Data(
        sales_data1,
        sales_data2,
        final_tender_data1,
        final_tender_data2,
        final_tender_data3,
        final_tender_data4
    )

    return gr, retail_all_data





    