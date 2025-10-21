# Processing Methods for Mobile-Ordering Reports
import pandas as pd
import numpy as np

# Aggregate MO and OTH sales (and trxns) across days per unit
def aggregate_sales(mo_df, oth_df, unique_units, show_patrons=False):
    header_cols = ["Mobile", "Kiosk + Register", "Total", "MO% of Total"]
    final_sales_data = pd.DataFrame(columns=header_cols)
    final_trxns_data = pd.DataFrame(columns=header_cols)
    
    for unit in unique_units:
        tmp_mo_df = mo_df[mo_df["Unit"] == unit]
        tmp_oth_df = oth_df[oth_df["Unit"] == unit]
        
        final_sales_data.loc[unit] = [
            np.sum(tmp_mo_df["item_price"]),
            np.sum(tmp_oth_df["item_price"]),
            0, 0
        ]

        if show_patrons:
            final_trxns_data.loc[unit] = [
                np.sum(tmp_mo_df["Checks"]),
                np.sum(tmp_oth_df["Checks"]),
                0, 0
            ]

    return final_sales_data, final_trxns_data


# Update the Total and MO% Columns
def post_process_dfs(agg_data):
    non_sales_cols = ['Total', 'MO% of Total']
    sales_cols = [col for col in agg_data.columns if col not in non_sales_cols]

    agg_data['Total'] = agg_data[sales_cols].sum(axis=1)
    agg_data['MO% of Total'] = agg_data.apply(
        lambda row: (row['Mobile'] / row['Total'] * 100) if row['Total'] != 0 else 0.0,
        axis=1
    ).round(2)

    return agg_data

# Add the Grand Total Row to the df
def add_grand_total_row(df):
    sales_cols = ['Mobile', 'Kiosk + Register', 'Total']
    totals = df[sales_cols].sum()

    mo_percent = (totals['Mobile'] / totals['Total']) * 100 if totals['Total'] != 0 else 0.0

    grand_total_row = pd.DataFrame({
        'Mobile': [totals['Mobile']],
        'Kiosk + Register': [totals['Kiosk + Register']],
        'Total': [totals['Total']],
        'MO% of Total': [round(mo_percent, 2)]
    }, index=['Grand Total'])

    df_with_total = pd.concat([df, grand_total_row])
    return df_with_total


# Trim Units with 0 sales across MO and non-MO
def trim_no_sales(df):
    df = df.drop(df[df["Total"] <= 0].index)
    return df


# Apply the post process, grand total, and trim no sales operations
def post_process_totals(df):
    df = post_process_dfs(df)
    df = add_grand_total_row(df)
    df = trim_no_sales(df)
    return df