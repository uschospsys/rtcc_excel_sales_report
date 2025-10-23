# Processing Methods for Mobile-Ordering Reports
import pandas as pd
import numpy as np

# Aggregate MO and OTH sales (and trxns) across days per unit
def aggregate_sales(df, unique_units, show_patrons=False, split_kiosks=False):
    if split_kiosks:
        header_cols = ["Mobile", "Kiosk", "Register", "Total", "MO%", "Kiosk%", "Register%"]
    else:
        header_cols = ["Mobile", "Kiosk + Register", "Total", "MO% of Total"]
    final_sales_data = pd.DataFrame(columns=header_cols)
    final_trxns_data = pd.DataFrame(columns=header_cols)

    if split_kiosks:
        # Split into Mobile and non-Mobile (Kiosk + Registers)
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
    
            if show_patrons:
                final_trxns_data.loc[unit] = [
                    np.sum(tmp_mo_df["Checks"]),
                    np.sum(tmp_k_df["Checks"]),
                    np.sum(tmp_reg_df["Checks"]),
                    0, 0, 0, 0
                ]
        return final_sales_data, final_trxns_data
    
    # Else:
    # Split into Mobile and non-Mobile (Kiosk + Registers)
    mo_df = df[df["POS"] == "Mobile"]
    oth_df = df[df["POS"] != "Mobile"]
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
def post_process_dfs(agg_data, split_kiosks):
    non_sales_cols = ["Total", "MO%", "Kiosk%", "Register%"] if split_kiosks else ['Total', 'MO% of Total']
    sales_cols = [col for col in agg_data.columns if col not in non_sales_cols]

    agg_data['Total'] = agg_data[sales_cols].sum(axis=1)
    if split_kiosks:
        agg_data['MO%'] = agg_data.apply(
            lambda row: (row['Mobile'] / row['Total'] * 100) if row['Total'] != 0 else 0.0,
            axis=1
        ).round(2)

        agg_data['Kiosk%'] = agg_data.apply(
            lambda row: (row['Kiosk'] / row['Total'] * 100) if row['Total'] != 0 else 0.0,
            axis=1
        ).round(2)

        agg_data['Register%'] = agg_data.apply(
            lambda row: (row['Register'] / row['Total'] * 100) if row['Total'] != 0 else 0.0,
            axis=1
        ).round(2)

    else:
        agg_data['MO% of Total'] = agg_data.apply(
            lambda row: (row['Mobile'] / row['Total'] * 100) if row['Total'] != 0 else 0.0,
            axis=1
        ).round(2)

    return agg_data

# Add the Grand Total Row to the df
def add_grand_total_row(df, split_kiosks):
    sales_cols = ['Mobile', 'Kiosk', 'Register', 'Total'] if split_kiosks else ['Mobile', 'Kiosk + Register', 'Total']
    totals = df[sales_cols].sum()

    if split_kiosks:
        mo_percent = (totals['Mobile'] / totals['Total']) * 100 if totals['Total'] != 0 else 0.0
        k_percent = (totals['Kiosk'] / totals['Total']) * 100 if totals['Total'] != 0 else 0.0
        reg_percent = (totals['Register'] / totals['Total']) * 100 if totals['Total'] != 0 else 0.0
    
        grand_total_row = pd.DataFrame({
            'Mobile': [totals['Mobile']],
            'Kiosk': [totals['Kiosk']],
            'Register': [totals['Register']],
            'Total': [totals['Total']],
            'MO%': [round(mo_percent, 2)],
            'Kiosk%': [round(k_percent, 2)],
            'Register%': [round(reg_percent, 2)]
        }, index=['Grand Total'])
        
    else:
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
def post_process_totals(df, hide_units, split_kiosks):
    df = post_process_dfs(df, split_kiosks)
    df = add_grand_total_row(df, split_kiosks)
    if hide_units == "Hide Units with no Sales":
        df = trim_no_sales(df)
    return df