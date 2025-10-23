# Utilities for writing to an Excel Sheet

import pandas as pd
import matplotlib.pyplot as plt
from pandas import ExcelWriter
from io import BytesIO

from utils.mo_graphing import (
    generate_pie_chart,
    plot_unit_channel_sales
)

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

def figure_to_img_bytes(figure):
    img_bytes = BytesIO()
    figure.savefig(img_bytes, format="png", bbox_inches="tight")
    img_bytes.seek(0)
    return img_bytes

def export_to_excel_report(sales_df, trxns_df, filename, unit_name, show_patrons=False, split_kiosks=False):
    
    # Save chart images
    fig_pie = generate_pie_chart(sales_df.iloc[-1], "Grand Total Sales", split_kiosks=split_kiosks)
    sales_pie_img = figure_to_img_bytes(fig_pie)
    # plt.savefig("sales_pie.png", bbox_inches='tight')
    plt.close(fig_pie)

    fig_bar = plot_unit_channel_sales(sales_df.iloc[:-1], True, unit_name, split_kiosks=split_kiosks)
    sales_bar_img = figure_to_img_bytes(fig_bar)
    # plt.savefig("sales_bar.png", bbox_inches='tight')
    plt.close(fig_bar)

    if show_patrons:
        fig_pie_t = generate_pie_chart(trxns_df.iloc[-1], "Grand Total Transactions", split_kiosks=split_kiosks)
        trxn_pie_img = figure_to_img_bytes(fig_pie_t)
        # plt.savefig("trxns_pie.png", bbox_inches='tight')
        plt.close(fig_pie_t)
    
        fig_bar_t = plot_unit_channel_sales(trxns_df.iloc[:-1], False, unit_name, split_kiosks=split_kiosks)
        trxn_bar_img = figure_to_img_bytes(fig_bar_t)
        # plt.savefig("trxns_bar.png", bbox_inches='tight')
        plt.close(fig_bar_t)

    # Start Excel writing
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        workbook = writer.book

        # Write sales data
        sheet_sales = workbook.add_worksheet('Sales')
        writer.sheets['Sales'] = sheet_sales

        table_start = 3
        pie_start = table_start + sales_df.shape[0] + 3
        bar_start = pie_start


        _add_formats(workbook)
        
        # Write To Excel
        _write_formatted_sheet(
            sheet_sales, 
            workbook,
            df = sales_df,
            table_start_row = table_start,
            table_start_col = 2,
            pie_image = sales_pie_img,
            pie_start_row = pie_start, 
            pie_start_col=1,
            bar_image = sales_bar_img,
            bar_start_row = pie_start, 
            bar_start_col=6,
            is_sales = True,
            split_kiosks = split_kiosks
        )
        
        sheet_sales.merge_range('C2:H2', f'{unit_name} Mobile-Ordering Sales Report', formats['merge_format'])


        if show_patrons:
            # Write transactions data
            sheet_trxns = workbook.add_worksheet('Transactions')
            writer.sheets['Transactions'] = sheet_trxns
    
            table_start = 3
            pie_start = table_start + trxns_df.shape[0] + 3
            bar_start = pie_start
            
            _write_formatted_sheet(
                sheet_trxns, 
                workbook,
                df = trxns_df,
                table_start_row = table_start,
                table_start_col = 2,
                pie_image = trxn_pie_img,
                pie_start_row = pie_start, 
                pie_start_col=1,
                bar_image = trxn_bar_img,
                bar_start_row = pie_start, 
                bar_start_col=6,
                is_sales = False,
                split_kiosks = split_kiosks
            )

            sheet_trxns.merge_range('C2:H2', f'{unit_name} Mobile-Ordering Patrons Report', formats['merge_format'])

    output.seek(0)
    return output


def _write_formatted_sheet(
    sheet, workbook,
    df, table_start_row, table_start_col,
    pie_image, pie_start_row, pie_start_col,
    bar_image, bar_start_row, bar_start_col,
    is_sales, split_kiosks
):
    # === Write Headers ===
    for j, col in enumerate(df.columns):
        sheet.write(table_start_row, table_start_col + j + 1, col, formats['header_format'])

    len_df = len(df)
    
    # === Write Index and Data with Proper Formatting ===
    for i, (index_label, row) in enumerate(df.iterrows()):
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
        sheet.set_column(table_start_col + j, table_start_col + j, 15)  # Adjust width as needed

    # === Insert Pie Chart ===
    sheet.insert_image(pie_start_row, pie_start_col, "pie_image.png", {'image_data': pie_image, 'x_scale': 0.7, 'y_scale': 0.7})

    # === Insert Bar Chart ===
    sheet.insert_image(bar_start_row, bar_start_col, "bar_image.png", {'image_data': bar_image, 'x_scale': 0.8, 'y_scale': 0.8})
