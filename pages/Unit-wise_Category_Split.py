# pages/1_CategoryMapper.py

import streamlit as st
import pandas as pd
from utils.constants import default_sheet_categories
from utils.processing import (
    extract_categories_from_excel,
    format_monetary_columns,
    generate_excel
)

st.set_page_config(page_title="RTCC-Seeds Unit-wise Category Split", layout="wide")
st.title("RTCC Food Court and Seeds Marketplace Unit-wise Category Split")

# Upload Excel
uploaded_file = st.file_uploader("Upload Excel File", type=["xls", "xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    df = format_monetary_columns(df)

    # Extract categories dynamically from the uploaded Excel
    sheet_data = extract_categories_from_excel(df)
    extracted_categories = list(sheet_data.keys())

    st.divider()
    st.success(f"Found {len(extracted_categories)} categories in file")

    with st.expander("📋 View Extracted Categories"):
        st.write(extracted_categories)

    # Initialize sheet mapping with defaults — but only use available categories
    if "sheet_mapping" not in st.session_state:
        st.session_state.sheet_mapping = {}
        for sheet, default_cats in default_sheet_categories.items():
            filtered_cats = [cat for cat in default_cats if cat in extracted_categories]
            if filtered_cats:
                st.session_state.sheet_mapping[sheet] = filtered_cats

    st.divider()
    st.subheader("Manage Sheets & Category Assignments")

    # Add new sheet
    new_sheet = st.text_input("➕ Add new sheet name")
    if st.button("Add Sheet") and new_sheet.strip():
        new_sheet = new_sheet.strip()
        if new_sheet in st.session_state.sheet_mapping:
            st.warning("Sheet already exists.")
        else:
            st.session_state.sheet_mapping[new_sheet] = []

    st.divider()
    # Build current category-to-sheet mapping
    cat_to_sheet = {}
    for sheet, cats in st.session_state.sheet_mapping.items():
        for cat in cats:
            cat_to_sheet[cat] = sheet

    used_categories = set(cat_to_sheet.keys())
    updated_mapping = {}
    sheets_to_remove = []

    # Two-column layout for sheets
    sheet_names = list(st.session_state.sheet_mapping.keys())

    for i in range(0, len(sheet_names), 2):
        cols = st.columns(2)
        for j in range(2):
            if i + j >= len(sheet_names):
                continue

            sheet = sheet_names[i + j]
            current_cats = st.session_state.sheet_mapping[sheet]

            with cols[j]:
                # Sheet header with inline remove button
                header_col1, header_col2 = st.columns([4, 1])
                with header_col1:
                    st.markdown(f"#### 🗂️ {sheet}")
                with header_col2:
                    if st.button("❌", key=f"remove_{sheet}", help="Remove this sheet"):
                        sheets_to_remove.append(sheet)

                # Available categories: only those not already assigned, or currently selected
                available = [cat for cat in extracted_categories if cat not in used_categories or cat in current_cats]
                selected = st.multiselect(
                    "Categories",
                    options=available,
                    default=current_cats,
                    key=f"multiselect_{sheet}"
                )
                updated_mapping[sheet] = selected

    # Remove deleted sheets
    for sheet in sheets_to_remove:
        st.session_state.sheet_mapping.pop(sheet, None)

    # Update state with new selections
    st.session_state.sheet_mapping.update(updated_mapping)

    st.divider()
    # Generate Excel
    if st.button("📥 Generate and Download Excel"):
        output = generate_excel(
            sheet_categories=st.session_state.sheet_mapping,
            sheet_data=sheet_data,
            df_columns=df.columns
        )

        st.download_button(
            label="⬇️ Download Categorized Excel",
            data=output,
            file_name="categorized_output.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
