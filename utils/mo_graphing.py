# Matplotlib Graphing Methods for MO Sales Report

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np

# Pie Chart
def generate_pie_chart(df, label="Grand Total Sales"):
    mo_percent = df['MO% of Total'] 
    sizes = [mo_percent, 100-mo_percent]
    pie_lab = ["Mobile", "Kiosk + Register"]

    fig, ax = plt.subplots(figsize=(10, 7))
    # plt.figure(figsize=(10,7))
    ax.pie(
        sizes, labels=pie_lab, autopct="%1.2f%%",
        shadow=True, explode=(0.05,0)
    )
    ax.set_title(label)

    ax.legend(loc='upper right')
    # plt.show()
    return fig

# Bar Chart
def plot_unit_channel_sales(df, is_sales=True, unit_name="x"):
    df = df.copy()

    units = df.index.tolist()
    mobile = df['Mobile'].values
    kiosk = df['Kiosk + Register'].values
    total = df['Total'].values

    x = np.arange(len(units))
    width = 0.20

    fig, ax = plt.subplots(figsize=(15, 6))

    # Bars for Mobile and (Kiosk + Register)
    bars_mobile = ax.bar(x - width/2, mobile, width, label='Mobile', color='#1f77b4')
    bars_kiosk = ax.bar(x + width/2, kiosk, width, label='Kiosk + Register', color='#ff7f0e')
    
    # Total sales text
    ax.set_xticks(x)
    ax.set_xticklabels(
        [f"{unit}\n(${total:,.2f})" if is_sales else f"{unit}\n({total:,.0f})" for unit, total in zip(units, total)]
    )

    ax.set_xlabel(f'{unit_name} Units')
    ax.set_ylabel('Sales ($)' if is_sales else '#Transactions')
    ax.set_title(f'{unit_name} {'Sales' if is_sales else 'Transactions'} Splits')
    
    ax.legend()
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # plt.ylim(top=50000)

    ax.yaxis.set_major_formatter(ticker.StrMethodFormatter('{x:,.0f}'))
    
    fig.tight_layout()
    # plt.show()

    return fig