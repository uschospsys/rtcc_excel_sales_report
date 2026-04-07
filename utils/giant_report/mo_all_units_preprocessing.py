import pandas as pd
import numpy as np

def pos_selection(kiosk_name):
    if 'MO' in kiosk_name:
        return 'Mobile'
    elif 'Reg' in kiosk_name:
        return 'Register'
    elif 'Kiosk' in kiosk_name:
        return 'Kiosk'
    elif 'Tablet' in kiosk_name:
        return 'Tablet'
    else:
        return None


def unit_selection(row):
    # DISCOUNT items
    if 'DISCOUNT' in str(row['item_number']):
        return 'DISCOUNT'
    
    # Dining Halls
    elif 'EVK Residential' in row['location_name']:
        return 'RES_EVK Residential'
    elif 'PIRC Residential' in row['location_name']:
        return 'RES_PIRC Residential'
    elif 'University VillageResidential' in row['location_name']:
        return 'RES_UV Residential'

    # HSC Units
    elif 'HSC Illy' in row['location_name']:
        return 'HSC_HSC Illy'
    elif 'HSC Marketplace' in row['item_cat_name']:
        return 'HSC_HSC Marketplace'
    elif 'HSC Marketplace Breakfast' in row['item_cat_name']:
        return 'HSC_HSC Marketplace'
    elif 'HSC Marketplace Fruit' in row['item_cat_name']:
        return 'HSC_HSC Marketplace'
    elif 'HSC Panda Express' in row['item_cat_name']:
        return 'HSC_HSC Panda Express'
    elif 'HSC Panda Express Catering' in row['item_cat_name']:
        return 'HSC_HSC Panda Express'
    elif 'HSC Taco Taco' in row['item_cat_name']:
        return 'HSC_HSC Taco Taco'
    elif 'HSC Takeover' in row['item_cat_name']:
        return 'HSC_HSC Takeover'
    elif 'HSC Food Court' in row['location_name']:
        return 'HSC_HSC Retail'
    
    # UPC Units
    elif 'UPC Trojan Grounds Illy' in row['location_name']:
        return 'UPC_UPC Trojan Grounds Illy'
    elif 'Tutor Hall Cafe' in row['location_name']:
        return 'UPC_Tutor Hall'
    elif 'W. Annenberg Cafe' in row['location_name']:
        return 'UPC_W. Annenberg Cafe'
    elif 'HSC Illy' in row['location_name']:
        return 'UPC_HSC Illy'
    elif 'Coffee Bean & Tea Leaf' in row['location_name']:
        return 'UPC_CBTL Cinema'
    elif 'Popovich' in row['location_name']:
        return 'UPC_Popovich'
    elif 'Law School' in row['location_name']:
        return 'UPC_Law School'
    elif 'Chad Tons Family Cafe' in row['location_name']:
        return 'UPC_Chad Tons Family Cafe'
    elif 'Literatea' in row['location_name']:
        return 'UPC_Literatea'

    # RTCC Food Court
    elif 'C&G' in row['item_cat_name']:
        return 'RTCC_C&G'
    elif 'Taco Taco' in row['item_cat_name']:
        return 'RTCC_Taco Taco'
    elif 'Burger Crush' in row['item_cat_name']:
        return 'RTCC_Burger Crush'
    elif 'Chicken Tenders' in row['item_cat_name']:
        return 'RTCC_Chicken Tenders'
    elif 'Panda Express' in row['item_cat_name']:
        return 'RTCC_Panda Express'
    elif 'Filones' in row['item_cat_name']:
        return 'RTCC_Filones'
    elif 'Slice Shop' in row['item_cat_name']:
        return 'RTCC_Slice Shop'
    elif 'RTCC Bowls Express'  in row['item_cat_name']:
        return 'RTCC_Bowls Express'
    elif 'RTCC Bowls' in row['item_cat_name']:
        return 'RTCC_Bowls'
    elif 'RTCC Upstairs' in row['item_cat_name']:
        return 'RTCC_Upstairs'
    elif 'RTCC Pop Up' in row['item_cat_name']:
        return 'RTCC_Pop Up'


    # Seeds Marketplace
    elif 'Seeds Breakfast Meal Plan' in row['item_cat_name']:
        return 'Seeds_Seeds Breakfast'
    elif 'Seeds EatWell Breakfast' in row['item_cat_name']:
        return 'Seeds_Seeds Breakfast'
    elif 'Seeds Breakfast' in row['item_cat_name']:
        return 'Seeds_Seeds Breakfast'
    elif 'Seeds Sandwiches Meal Plan' in row['item_cat_name']:
        return 'Seeds_Seeds Sandwich'
    elif 'Seeds Sandwich' in row['item_cat_name']:
        return 'Seeds_Seeds Sandwich'
    elif 'Seeds Salads Meal Plan' in row['item_cat_name']:
        return 'Seeds_Seeds Salad'
    elif 'Seeds Salads' in row['item_cat_name']:
        return 'Seeds_Seeds Salad'
    elif 'Seeds EatWell Salads' in row['item_cat_name']:
        return 'Seeds_Seeds Salad'
    elif 'Seeds Poke Bowls' in row['item_cat_name']:
        return 'Seeds_Seeds Poke Bowls'
    elif 'Retail' in row['item_cat_name']:
        return 'Seeds_Seeds Retail'
    elif 'Seeds Original Bowls' in row['item_cat_name']:
        return 'Seeds_Bowls at Seeds'
    elif 'Seeds Original Bowls Meal Plan' in row['item_cat_name']:
        return 'Seeds_Bowls at Seeds'
    elif 'Seeds Pop Up' in row['item_cat_name']:
        return 'Seeds_Seeds Pop Up'
    elif 'Seeds Cafe' in row['item_cat_name']:
        return 'Seeds_Seeds Cafe'
    elif 'Seeds Marketplace' in row['location_name']:
        return 'Seeds_Seeds Grab N Go'

    else:
        return None
        
def preprocess_all_units_raw(df):

    # Date, Time, Weekday Columns
    # If one exists, all three shall exist (from the query)
    if 'Date' not in df.columns:
        df['Date'] = df['tdatetime'].apply(lambda x: x.date())
        df['Time'] = df['tdatetime'].apply(lambda x: x.time())
        df['Weekday'] = df['tdatetime'].apply(lambda x: x.day_name())


    # POS Selection
    if 'POS' not in df.columns:
        df['POS'] = df['kiosk_name'].apply(pos_selection)

    # Unit Selection
    if 'Unit' not in df.columns:
        df['Unit'] = df.apply(unit_selection, axis=1)

    # Final Sorting
    df.sort_values(by='tdatetime', ascending=False, inplace=True)

    return df
        