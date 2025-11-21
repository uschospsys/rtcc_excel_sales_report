# Excel Cell Formatting Options
# Table Header Format
dict_header_format = {
    'bold': True,
    'border': 1,
    'bottom': 6,
    'align': 'center',
    'valign': 'vcenter',
    'bg_color': '#D9E1F2',  # Light blue background
    'font_color': '#000000'
}

# Cell Format for numbers with 1000s separator
dict_number_format = {
    'num_format': '#,##0',
    'border': 1,
    'align': 'center',
    'valign': 'vcenter'
}

# Cell Format for currency with 1000s separator and 2 decimal places
dict_currency_format = {
    'num_format': '$ #,##0.00',
    'border': 1,
    'align': 'center',
    'valign': 'vcenter'
}

# Cell Format for percentages with 2 decimal places
dict_percent_format = {
    'num_format': '0.00 %',
    'border': 1,
    'align': 'center',
    'valign': 'vcenter'
}

# Cell Format for Table Index cells
dict_index_format = {
    'bold': True,
    'border': 1,
    'align': 'center',
    'valign': 'vcenter',
    'bg_color': '#FFE699',  # Light yellow or any color you like
    'font_color': '#000000'
}

# Cell Format for Grand Total row's Index Column
dict_totals_index_format = {
    'bold': True,
    'left': 1,
    'right': 1,
    'top': 6,
    'bottom': 6,
    'align': 'center',
    'valign': 'vcenter',
    'bg_color': '#92d050',
    'font_color': '#000000'
}

# Cell Format for Grand Total row's Currency Columns
dict_total_currency_format = {
    'bold': True,
    'num_format': '$ #,##0.00',
    'border': 1,
    'top': 6,
    'bottom': 6,
    'align': 'center',
    'valign': 'vcenter',
    'bg_color': '#92d050'
}

# Cell Format for Grand Total row's Numbers with 1000s separator
dict_total_number_format = {
    'bold': True,
    'num_format': '#,##0',
    'border': 1,
    'top': 6,
    'bottom': 6,
    'align': 'center',
    'valign': 'vcenter',
    'bg_color': '#92d050'
}

# Cell Format for Grand Total row's Percentage Column
dict_total_percent_format = {
    'bold': True,
    'num_format': '0.00 %',
    'border': 1,
    'right': 1,
    'top': 6,
    'bottom': 6,
    'align': 'center',
    'valign': 'vcenter',
    'bg_color': '#92d050'
}

# Cell Format for Merging Cells 
dict_merge_format = {
    'bold': True,
    'font_size': 16,
    'align': 'center',
    'valign': 'vcenter',
    'font_color': '#000000'
}

