import pandas as pd
import numpy as np
import streamlit as st

from io import BytesIO
from pandas import ExcelWriter
from utils.mo_excel_formats import (
    dict_header_format,
    dict_number_format,
    dict_currency_format,
    dict_percent_format,
    dict_index_format,
    dict_totals_index_format,
    dict_total_currency_format,
    dict_total_percent_format,
    dict_merge_format,
    dict_total_number_format
)
from models.Tender_Data import Tender_Data

formats = {}
def _add_formats(workbook):
    formats['header_format'] = workbook.add_format(dict_header_format)
    formats['number_format'] = workbook.add_format(dict_number_format)
    formats['currency_format'] = workbook.add_format(dict_currency_format)
    formats['percent_format'] = workbook.add_format(dict_percent_format)
    formats['index_format'] = workbook.add_format(dict_index_format)
    formats['totals_index_format'] = workbook.add_format(dict_totals_index_format)
    formats['total_currency_format'] = workbook.add_format(dict_total_currency_format)
    formats['total_percent_format'] = workbook.add_format(dict_total_percent_format)
    formats['merge_format'] = workbook.add_format(dict_merge_format)
    formats['total_number_format'] = workbook.add_format(dict_total_number_format)

    
def write_giant_report(sales_retail, tender_data, unit_name, month, split_kiosks):

    output = BytesIO()

    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        workbook = writer.book
        sheet_retail = workbook.add_worksheet('Retail')
        writer.sheets['Retail'] = sheet_retail

        
        _add_formats(workbook)

        # Write the MO Report to Excel
        table_start = 3
        _write_formatted_sheet(
            sheet_retail,
            workbook,
            df = sales_retail,
            table_start_row = table_start,
            table_start_col = 1,
            is_sales=True,
            split_kiosks = split_kiosks
        ) 
        sheet_retail.merge_range('B2:H2', f'USC Retail Mobile-Ordering Sales {month} Report', formats['merge_format'])

        # Write the Tender Report to Excel
        table_start = 29
        _write_formatted_sheet_tenders(
            sheet_retail,
            workbook,
            df = tender_data.final_tender_sales,
            table_start_row = table_start,
            table_start_col = 1,
            is_sales=True,
            split_kiosks = split_kiosks
        )
        sheet_retail.merge_range('B28:N28', f'USC Retail Tender Summary {month} Report', formats['merge_format'])
    
    output.seek(0)
    return output


def _write_formatted_sheet(
    sheet, workbook, df,
    table_start_row, table_start_col,
    is_sales, split_kiosks
):
    # === Write Headers ===
    for j, col in enumerate(df.columns):
        sheet.write(table_start_row, table_start_col + j + 1, col, formats['totals_index_format'])

    len_df = len(df)

    # === Write Index and Data with Proper Formatting ===
    for i, (index_label, row) in enumerate(df.iterrows()):
        index_label = index_label.split("_")[1] if '_' in index_label else index_label
        sheet.write(table_start_row + i + 1, table_start_col, index_label, formats['index_format'] if (i+1) < len_df else formats['totals_index_format'])
        
        for j, value in enumerate(row):
            col_name = df.columns[j]
            curr_cols = ['Total', 'Mobile', 'Kiosk', 'Register'] if split_kiosks else ['Total', 'Mobile', 'Kiosk + Register']
            
            if col_name in curr_cols:
                if is_sales:
                    fmt = formats['currency_format'] if (i+1) < len_df else formats['total_currency_format']
                else:
                    fmt = formats['number_format'] if (i+1) < len_df else formats['total_number_format']  
            else:
                fmt = formats['percent_format'] if (i+1) < len_df else formats['total_percent_format']
                value = value / 100
                
                # value = value / 100 if value > 1 else value

            sheet.write(table_start_row + i + 1, table_start_col + j + 1, value, fmt)

    # === Set Column Widths ===
    total_cols = len(df.columns) + 1  # +1 for index column
    for j in range(total_cols):
        if j == 0:
            sheet.set_column(table_start_col + j, table_start_col + j, 25)  # Adjust width as needed for Unit Index Column
        else:
            sheet.set_column(table_start_col + j, table_start_col + j, 15)  # Adjust width as needed for Unit Index Column



def _write_formatted_sheet_tenders(
    sheet, workbook, df,
    table_start_row, table_start_col,
    is_sales, split_kiosks
):
    # === Write Headers ===
    for j, col in enumerate(df.columns):
        sheet.write(table_start_row, table_start_col + j + 1, col, formats['totals_index_format'])

    len_df = len(df)

    # === Write Index and Data with Proper Formatting ===
    for i, (index_label, row) in enumerate(df.iterrows()):
        index_label = index_label.split("_")[1] if '_' in index_label else index_label
        sheet.write(table_start_row + i + 1, table_start_col, index_label, formats['index_format'] if (i+1) < len_df else formats['totals_index_format'])
        
        for j, value in enumerate(row):
            col_name = df.columns[j]
            if is_sales:
                fmt = formats['currency_format'] if (i+1) < len_df else formats['total_currency_format']
            else:
                fmt = formats['number_format'] if (i+1) < len_df else formats['total_number_format']  

            sheet.write(table_start_row + i + 1, table_start_col + j + 1, value, fmt)

    # === Set Column Widths ===
    total_cols = len(df.columns) + 1  # +1 for index column
    for j in range(total_cols):
        if j == 0:
            sheet.set_column(table_start_col + j, table_start_col + j, 25)  # Adjust width as needed for Unit Index Column
        else:
            sheet.set_column(table_start_col + j, table_start_col + j, 15)  # Adjust width as needed for Unit Index Column



    