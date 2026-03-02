
import pandas as pd
import numpy as np
import streamlit as st

def add_location_name(value):
    if value == "EVK Residential Dining" or value == "EVK Residential":
        return "EVK"
    elif value == "PIRC Residential Dining" or value == "PIRC Residential":
        return "PIRC"
    elif value == "UV Residential Dining" or value == "University VillageResidential":
        return "UV"
    else:
        return None

def process_residential_data_bb(dfs):

    res = {}
    for key, df in dfs.items():

        # Step 1: Explicit Type Conversion
        df['Profit Center Name'] = df['Profit Center Name'].astype(str)
        df['Board Summary Date'] = pd.to_datetime(df['Board Summary Date'])
        df['Board Plan'] = df['Board Plan'].astype(str)
        df['Sum of Board Count'] = df['Sum of Board Count'].astype(int)

        # Step 2: Add Conditional Column for Venue
        df['Venue'] = df['Profit Center Name'].map(add_location_name)

        # Step 3: Reorder Columns
        df_re = df.loc[:, ['Profit Center Name', 'Venue', 'Board Summary Date', 'Board Plan', 'Sum of Board Count']]

        df_re.rename(columns = {
            'Board Plan': 'Board Plan.BB'
        }, inplace=True)

        # Step 4: Add Conditional Column1 "Board Plan" based on TOGO plans
        TOGO_BOARD_PLANS = [
            "AC Card Flex RA To Go",
            "x AC Card Flex To Go",
            "AC Cardinal To Go",
            "AC Gold To Go",
            "AC Flex RA To Go",
            "AC Flex Card To Go",
            "AC RA Cardinal To Go",
            "Z - AC Gold To Go"
        ]

        def add_togo_plans(value):
            if value in TOGO_BOARD_PLANS:
                return "To Go"
            else:
                return "Residential"
        
        df_re['Board Plan'] = df_re['Board Plan.BB'].map(add_togo_plans)
        
        # Step 5: Rename Columns 
        df_re.rename(columns={
            'Sum of Board Count': 'Transaction Count',
            'Board Summary Date': 'Date',
        }, inplace=True)

        df_re['Date'] = df_re['Date'].apply(lambda x: x.date())

        # Step 6: Final column reordering
        df_final = df_re.loc[:, ["Profit Center Name", "Venue", "Date", "Board Plan", "Transaction Count", "Board Plan.BB"]]

        res[key] = df_final

    return res


def process_residential_data_sql(dfs):
    
    res = {}
    for key, df in dfs.items():

        # Step 1: Add Conditional Column for Venue
        df['Venue'] = df['Profit_Center_Name'].map(add_location_name)

        # Step 2: Reorder Columns1
        df_re = df.loc[:, ["Profit_Center_Name", "Venue", "Date", "item_cat_name", "Sum_of_Transaction_Count"]]

        # Step 3: Rename Columns1
        df_re.rename(columns={
            'item_cat_name': 'Board Plan.O',
            'Sum_of_Transaction_Count': 'Transaction Count',
            'Date': 'Date.Time'
        }, inplace=True)

        # Step 4: Extract the date from date.time column
        df_re['Date'] = df_re['Date.Time'].apply(lambda x: x.date())

        # Step 5: Add Conditional Column for Board Plan
        def add_togo_plan2(value):
            if value == "Residential":
                return "Residential"
            elif value == "Residential ToGo":
                return "To Go"
            else:
                return None
        
        df_re['Board Plan'] = df_re['Board Plan.O'].map(add_togo_plan2)
        
        # Step 6: Reorder Columns2
        df_final = df_re.loc[:, ["Profit_Center_Name", "Venue", "Date", "Board Plan.O", "Transaction Count", "Date.Time", "Board Plan"]]

        res[key] = df_final

    return res


def get_aggregated_data(df):
    df = (
        df.groupby(["Venue", "Board Plan"], as_index=False)
          .agg({"Transaction Count": "sum"})
    )

    curr_year = df.pivot_table(
        index="Venue",
        columns="Board Plan",
        values="Transaction Count",
        aggfunc="sum",
        fill_value=0
    )

    curr_year.rename(columns={
        'Residential': 'Dine-In',
        'To Go': 'To-Go'
    }, inplace=True)
    
    curr_year['Total'] = curr_year['Dine-In'] + curr_year['To-Go']
    curr_year.loc['Grand Total'] = curr_year.sum(axis=0)
    curr_year['Dine-In %'] = (curr_year['Dine-In'] / curr_year['Total']) * 100.0
    curr_year['To-Go %'] = (curr_year['To-Go'] / curr_year['Total']) * 100.0

    return curr_year


def process_residential_data(bb_dfs, sql_dfs, month, year):

    # Current Year Statistics
    curr_df = pd.concat([bb_dfs[0], sql_dfs[0]], ignore_index=True)
    curr_df = curr_df[["Venue", "Transaction Count", "Board Plan"]]

    curr_year = get_aggregated_data(curr_df)

    # Comparison with Current and Previous Years
    prev_df = pd.concat([bb_dfs[1], sql_dfs[1]], ignore_index=True)
    prev_df = prev_df[["Venue", "Transaction Count", "Board Plan"]]
    
    prev_year = get_aggregated_data(prev_df)

    # Build Comparison Table
    summary_df = pd.concat([
        prev_year.loc[['Grand Total']],
        curr_year.loc[['Grand Total']]
    ])
    summary_df.index = [f'{month} {year-1}', f'{month} {year}']
    summary_df.loc['Variance'] = summary_df.loc[f'{month} {year}'] - summary_df.loc[f'{month} {year-1}']

    return curr_year, summary_df

