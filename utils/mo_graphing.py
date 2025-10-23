# Matplotlib Graphing Methods for MO Sales Report
import streamlit as st


import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np

# Pie Chart
def generate_pie_chart(df, label="Grand Total Sales", split_kiosks=False):
    pos = [x for x in list(df.columns) if "%" in x]
    
    df = df.iloc[-1]
    sizes = [df[x] for x in pos]
    
    # if split_kiosks:
        
    #     sizes = [df['MO%'], df['Register%'], df['Kiosk%']]
    #     pie_lab = ["Mobile", "Register", "Kiosk"]

    #     mask = [0 if x == 0.00 else 1 for x in sizes]
    #     sizes = [sizes[i] for i, _ in enumerate(mask) if mask[i]]
    #     pie_lab = [pie_lab[i] for i, _ in enumerate(mask) if mask[i]]
    # else:
    #     mo_percent = df['MO% of Total'] 
    #     sizes = [mo_percent, 100-mo_percent]
    #     pie_lab = ["Mobile", "Kiosk + Register"]

    fig, ax = plt.subplots(figsize=(10, 7))
    ax.pie(
        sizes, labels=pos, autopct="%1.2f%%",
        shadow=False, explode=[0]*len(sizes)
    )
    ax.set_title(label)

    ax.legend(loc='upper right')
    # plt.show()
    return fig

# Bar Chart
def plot_unit_channel_sales1(df, is_sales=True, unit_name="x", split_kiosks=False):
    df = df.copy()

    units = df.index.tolist()
    mobile = df['Mobile'].values

    if split_kiosks:
        kiosk = df['Kiosk'].values
        register = df['Register'].values
    else:
        kiosk = df['Kiosk + Register'].values
    total = df['Total'].values

    x = np.arange(len(units))
    width = 0.48 if split_kiosks else 0.20

    fig, ax = plt.subplots(figsize=(15, 6))

    # Bars for Mobile and (Kiosk + Register)
    if split_kiosks:
        bars_mobile = ax.bar(x - width/3, mobile, width/3, label='Mobile', color='#1f77b4')
        bars_kiosk = ax.bar(x, kiosk, width/3, label='Kiosk', color='green')
        bars_register = ax.bar(x + width/3, register, width/3, label='Register', color='#ff7f0e')
    else:
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

def plot_unit_channel_sales(df, is_sales=True, unit_name="x", split_kiosks=False):
    df = df.copy()

    # Detect numeric sales channels (exclude Total + percentages)
    channel_cols = [
        col for col in df.columns
        if col != "Total"
        and not col.endswith("%")
    ]

    # X axis values
    units = df.index.tolist()
    totals = df["Total"].values
    x = np.arange(len(units))

    # ----- FIXED GROUP-CENTERING BAR MATH -----
    num_channels = len(channel_cols)
    group_width = 0.3
    bar_width = group_width / num_channels

    offsets = np.linspace(
        -group_width/2 + bar_width/2,
        group_width/2 - bar_width/2,
        num_channels
    )
    # -------------------------------------------

    fig, ax = plt.subplots(figsize=(15, 6))

    # Draw bars
    for offset, col in zip(offsets, channel_cols):
        ax.bar(
            x + offset,
            df[col].values,
            bar_width,
            label=col
        )

    # X labels with totals
    ax.set_xticks(x)
    ax.set_xticklabels(
        [f"{unit}\n(${total:,.2f})" if is_sales else f"{unit}\n({total:,.0f})"
         for unit, total in zip(units, totals)]
    )

    ax.set_xlabel(f"{unit_name} Units")
    ax.set_ylabel("Sales ($)" if is_sales else "#Transactions")
    ax.set_title(f"{unit_name} {'Sales' if is_sales else 'Transactions'} Splits")

    ax.legend()
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    ax.yaxis.set_major_formatter(ticker.StrMethodFormatter('{x:,.0f}'))
    
    fig.tight_layout()
    return fig
