import pandas as pd
import numpy as np
from xlsxwriter.utility import xl_col_to_name
from io import BytesIO


def extract_categories(df, categories):
    full_categories = ["Category - " + cat for cat in categories]
    cat_idx = []

    for idx, val in enumerate(df.iloc[:, 0].astype(str).tolist()):
        if val in full_categories:
            cat_name = val.split("- ")[1]
            cat_idx.append((idx, cat_name))

    sheet_data = {}
    for i in range(len(cat_idx)):
        start = cat_idx[i][0]
        end = cat_idx[i + 1][0] if i + 1 < len(cat_idx) else len(df)
        cat_name = cat_idx[i][1]
        sheet_data[cat_name] = df.iloc[start:end]

    return sheet_data


def extract_categories_from_excel(df):
    cat_idx = []

    for idx, val in enumerate(df.iloc[:, 0].astype(str)):
        if val.startswith("Category - "):
            cat_name = val.split("Category - ")[1].strip()
            cat_idx.append((idx, cat_name))

    sheet_data = {}
    for i in range(len(cat_idx)):
        start = cat_idx[i][0]
        end = cat_idx[i + 1][0] if i + 1 < len(cat_idx) else len(df)
        cat_name = cat_idx[i][1]
        sheet_data[cat_name] = df.iloc[start:end]

    return sheet_data


def format_monetary_columns(df):
    amt_update_cols = ['Unnamed: 2', 'Unnamed: 10', 'Unnamed: 11', 'Unnamed: 12']
    
    for col in amt_update_cols:
        if col in df.columns:
            df[col] = df[col].apply(lambda x: f"${x:,.2f}" if isinstance(x, (float, np.float64)) and not pd.isna(x) else x)
    
    return df

def generate_excel(sheet_categories, sheet_data, df_columns, highlight=True, remove_summary=True):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')

    if remove_summary and sheet_data:
        last_key = list(sheet_data.keys())[-1]
        sheet_data[last_key] = sheet_data[last_key].head(-9)

    empty_row_df = pd.DataFrame([[''] * len(df_columns)], columns=df_columns)
    highlight_format = writer.book.add_format({'bg_color': 'yellow', 'bold': True})

    for sheet_name, cats in sheet_categories.items():
        cat_dfs = []
        for cat in cats:
            if cat not in sheet_data:
                continue
            cat_dfs += [empty_row_df, sheet_data[cat], empty_row_df]
        
        if not cat_dfs:
            continue

        combined_df = pd.concat(cat_dfs, ignore_index=True)
        combined_df.to_excel(writer, sheet_name=sheet_name, index=False, header=False)

        if highlight:
            ws = writer.sheets[sheet_name]
            nrows, ncols = combined_df.shape
            last_col = xl_col_to_name(ncols - 1)
            data_range = f"A1:{last_col}{nrows}"
            for cat in cats:
                ws.conditional_format(data_range, {
                    'type': 'formula',
                    'criteria': f'=$A1="Total Sales for {cat}"',
                    'format': highlight_format
                })

    writer.close()
    output.seek(0)
    return output
