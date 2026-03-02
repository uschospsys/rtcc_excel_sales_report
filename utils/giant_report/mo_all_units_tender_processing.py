import pandas as pd
import numpy as np
from models.Tender_Data import Tender_Data

def generate_tender_report(df, unique_locations):
    header_cols = np.unique(df['ttenders_name'])

    final_tender_sales = pd.DataFrame(columns=header_cols)
    final_tender_txns = pd.DataFrame(columns=header_cols)

    # unique_locations = np.unique(df['location_name'])

    # Generate aggregate sales/txns numbers for each location across different tenders
    for loc in unique_locations:
        temp_loc_df = df[df['location_name'] == loc]

        temp_tender_prices = []
        temp_tender_txns = []
        for tender in header_cols:
            temp_tender_df = temp_loc_df[temp_loc_df['ttenders_name'] == tender]
            temp_tender_prices.append(np.sum(temp_tender_df['item_price']))
            temp_tender_txns.append(np.sum(temp_tender_df['Checks']))
            
        final_tender_sales.loc[loc] = temp_tender_prices
        final_tender_txns.loc[loc] = temp_tender_txns


    # Generate totals for each location
    final_tender_sales['Total'] = final_tender_sales[header_cols].sum(axis=1)
    final_tender_txns['Total'] = final_tender_txns[header_cols].sum(axis=1)

    # Generate grand total row
    total_sales = final_tender_sales[final_tender_sales.columns].sum()
    total_txns = final_tender_txns[final_tender_txns.columns].sum()

    final_tender_sales = pd.concat([final_tender_sales, pd.DataFrame([total_sales], index=['Grand Total'])])
    final_tender_txns = pd.concat([final_tender_txns, pd.DataFrame([total_txns], index=['Grand Total'])])

    return Tender_Data(final_tender_sales, final_tender_txns)