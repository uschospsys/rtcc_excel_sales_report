
from models.Sales_Data import Sales_Data
from utils.mo_processing import post_process_totals

from io import BytesIO
import pandas as pd
import numpy as np
import streamlit as st
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

formats = {}

class Giant_Report():

    def __init__(self, df, df2):
        self.df = df
        self.df2 = df2

    def compute_totals(self, result):
        result['Total'] = sum(result.values())
        result['MO%'] = (result['Mobile'] / result['Total'] * 100 if result['Total'] != 0 else 0.0).round(2)
        result['Kiosk%'] = (result['Kiosk'] / result['Total'] * 100 if result['Total'] != 0 else 0.0).round(2) 
        result['Register%'] = (result['Register'] / result['Total'] * 100 if result['Total'] != 0 else 0.0).round(2)
        return result

    
    def aggregate_giant_sales_data(self, is_current=True):
        header_cols = ["Mobile", "Kiosk", "Register", "Total", "MO%", "Kiosk%", "Register%"]
        final_sales_data = pd.DataFrame(columns=header_cols)
        final_trxns_data = pd.DataFrame(columns=header_cols)
        
        if is_current:
            df = self.df
            unique_units = np.unique(df['Unit'])
            
            mo_df = df[df["POS"] == "Mobile"]
            k_df = df[df["POS"] == "Kiosk"]
            reg_df = df[df["POS"] == "Register"]
        
            for unit in unique_units:
                tmp_mo_df = mo_df[mo_df["Unit"] == unit]
                tmp_k_df = k_df[k_df["Unit"] == unit]
                tmp_reg_df = reg_df[reg_df["Unit"] == unit]
                
                final_sales_data.loc[unit] = [
                    np.sum(tmp_mo_df["item_price"]),
                    np.sum(tmp_k_df["item_price"]),
                    np.sum(tmp_reg_df["item_price"]),
                    0, 0, 0, 0
                ]

                final_trxns_data.loc[unit] = [
                    np.sum(tmp_mo_df["item_qty"]),
                    np.sum(tmp_k_df["item_qty"]),
                    np.sum(tmp_reg_df["item_qty"]),
                    0, 0, 0, 0
                ]

            return Sales_Data(
                post_process_totals(final_sales_data, '', True),
                post_process_totals(final_trxns_data, '', True)
            )
            
        else:
            df = self.df2
            unique_pos = ['Mobile', 'Kiosk', 'Register']

            result_sales = {}
            result_trxns = {}
            for pos in unique_pos:
                temp_pos_df = df[df['POS'] == pos]
                result_sales[pos] = np.sum(temp_pos_df['item_price'])
                result_trxns[pos] = np.sum(temp_pos_df['item_qty'])

            result_sales = self.compute_totals(result_sales)
            result_trxns = self.compute_totals(result_trxns)

            
            
            final_sales_data_row = pd.DataFrame(result_sales, index=['Grand Total'])
            final_trxns_data_row = pd.DataFrame(result_trxns, index=['Grand Total'])

            # st.write("HERE:")
            # st.dataframe(final_sales_data_row)
            
            return Sales_Data(final_sales_data_row, final_trxns_data_row)


    def _add_formats(self, workbook):
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

    
    def export_to_excel(
        self, sales_data1, sales_data2,
        final_tender_data1, final_tender_data2, final_tender_data3, final_tender_data4,
        res_curr_df, res_comp_df,
        filename, month, year
    ):
        output = BytesIO()
        datee = f"{month} {year}"

        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            workbook = writer.book
            sheet_retail = workbook.add_worksheet('Retail')
            sheet_residential = workbook.add_worksheet('Residential')
            
            writer.sheets['Retail'] = sheet_retail
            writer.sheets['Residential'] = sheet_residential
            
            self._add_formats(workbook)

        # Retail Sheet
            # Write the current MO Report to Excel
            table_start = 3
            self._write_formatted_sheet(
                sheet_retail,
                workbook,
                df = sales_data1.final_sales,
                table_start_row = table_start,
                table_start_col = 1,
                is_sales=True,
                split_kiosks = True
            ) 
            sheet_retail.merge_range('B2:I2', f'USC Retail Mobile-Ordering Sales {datee} Report', formats['merge_format'])
    
            # Write the current Tender Report to Excel
            table_start = 50
            self._write_formatted_sheet_tenders(
                sheet_retail,
                workbook,
                df = final_tender_data1.final_tender_sales,
                table_start_row = table_start,
                table_start_col = 1,
                is_sales=True,
                split_kiosks = True
            )
            sheet_retail.merge_range('B49:S49', f'USC Retail Tender Summary {datee} Report', formats['merge_format'])

            comp_table = self.build_sales_comp_table(sales_data1.final_sales, sales_data2.final_sales, month, year)
            st.dataframe(comp_table)
            # Write MO Report Comparison to Excel
            table_start = 42
            self._write_formatted_sheet(
                sheet_retail,
                workbook,
                df = comp_table,
                table_start_row = table_start,
                table_start_col = 1,
                is_sales=True,
                split_kiosks = True
            )
            sheet_retail.merge_range('B41:I41', f'USC Retail MO Sales {datee} Comparison Report', formats['merge_format'])

            tender_comp_table = self.build_tender_comp_table(final_tender_data1.final_tender_sales, final_tender_data2.final_tender_sales, month, year)
            st.dataframe(tender_comp_table)
            # Write Tender Report Comparison to Excel
            table_start = 68
            self._write_formatted_sheet_tenders(
                sheet_retail,
                workbook,
                df = tender_comp_table,
                table_start_row = table_start,
                table_start_col = 1,
                is_sales = True,
                split_kiosks = True
            )
            sheet_retail.merge_range('B67:S67', f'USC Retail Tender Summary {datee} Comparison Report', formats['merge_format'])

        # Residential Sheet
            # Write Current Customer Count Report
            table_start = 3
            self._write_formatted_sheet(
                sheet_residential,
                workbook,
                df = res_curr_df,
                table_start_row = table_start,
                table_start_col = 1,
                is_sales=False,
                split_kiosks = True
            ) 
            sheet_residential.merge_range('B2:G2', f'USC Residential Customer Count {datee} Comparison Report', formats['merge_format'])

            # Write Customer Count Comparison Report
            table_start = 12
            self._write_formatted_sheet(
                sheet_residential,
                workbook,
                df = res_comp_df,
                table_start_row = table_start,
                table_start_col = 1,
                is_sales=False,
                split_kiosks = True
            ) 
            sheet_residential.merge_range('B11:G11', f'USC Residential Customer Count {month} Comparison Report', formats['merge_format'])

            # Write the Residential Current Tender Report to Excel
            table_start = 21
            self._write_formatted_sheet_tenders(
                sheet_residential,
                workbook,
                df = final_tender_data3.final_tender_sales,
                table_start_row = table_start,
                table_start_col = 1,
                is_sales=True,
                split_kiosks = True
            )
            sheet_residential.merge_range('B20:S20', f'USC Residential Tender Summary {datee} Report', formats['merge_format'])

            res_tender_comp_table = self.build_tender_comp_table(final_tender_data3.final_tender_sales, final_tender_data4.final_tender_sales, month, year)
            st.dataframe(res_tender_comp_table)
            # Write Tender Report Comparison to Excel
            table_start = 30
            self._write_formatted_sheet_tenders(
                sheet_residential,
                workbook,
                df = res_tender_comp_table,
                table_start_row = table_start,
                table_start_col = 1,
                is_sales = True,
                split_kiosks = True
            )
            sheet_residential.merge_range('B29:S29', f'USC Residential Tender Summary {datee} Comparison Report', formats['merge_format'])
        
        output.seek(0)
        return output


    def build_sales_comp_table(self, sales_data1, sales_data2, month, year):
        last_row1 = sales_data1.iloc[[-1]].copy()
        last_row2 = sales_data2.iloc[[-1]].copy()

        comp_table = pd.concat([last_row2, last_row1], ignore_index=True)
        # comp_table.columns = sales_data2.columns.tolist().insert(0, 'Time')

        comp_table.rename(
            index={
                0: f"{month} {year-1}",
                1: f"{month} {year}"
            }
        , inplace=True)
        comp_table.loc['Variance'] = comp_table.iloc[1] - comp_table.iloc[0]

        return comp_table


    def build_tender_comp_table(self, tender_data1, tender_data2, month, year):
        last_row1 = tender_data1.iloc[[-1]].copy()
        last_row2 = tender_data2.iloc[[-1]].copy()

        comp_table = pd.concat([last_row2, last_row1], ignore_index=True)
        comp_table = comp_table.fillna(0)

        new_cols = list(comp_table.columns)
        new_cols.remove('Total')
        new_cols.append('Total')

        comp_table = comp_table[new_cols]

        comp_table.rename(
            index={
                0: f"{month} {year-1}",
                1: f"{month} {year}"
            }, inplace=True
        )
        comp_table.loc['Variance'] = comp_table.iloc[1] - comp_table.iloc[0]

        return comp_table
        

    def _write_formatted_sheet(self,
        sheet, workbook, df,
        table_start_row, table_start_col,
        is_sales, split_kiosks
    ):
        # === Write Headers ===
        for j, col in enumerate(df.columns):
            sheet.write(table_start_row, table_start_col + j + 1, col, formats['totals_index_format'])
    
        len_df = len(df)

        # st.write("===")
        # === Write Index and Data with Proper Formatting ===
        for i, (index_label, row) in enumerate(df.iterrows()):
            # st.write(f"index_label>{index_label}<")
            index_label = index_label.split("_")[1] if '_' in index_label else index_label
            sheet.write(table_start_row + i + 1, table_start_col, index_label, formats['index_format'] if (i+1) < len_df else formats['totals_index_format'])
            
            for j, value in enumerate(row):
                col_name = df.columns[j]
                curr_cols = ['Total', 'Mobile', 'Kiosk', 'Register', 'Dine-In', 'To-Go'] if split_kiosks else ['Total', 'Mobile', 'Kiosk + Register', 'Dine-In', 'To-Go']
                
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
    
    
    
    def _write_formatted_sheet_tenders(self, 
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
                sheet.set_column(table_start_col + j, table_start_col + j, 30)  # Adjust width as needed for Unit Index Column
            else:
                sheet.set_column(table_start_col + j, table_start_col + j, 15)  # Adjust width as needed for Unit Index Column


