import pandas as pd
import streamlit as st
import os
from pathlib import Path

@st.cache_resource
def load_data():
    dataframes, combined_df, sheet_names = None, None, None
    base_dir = Path(__file__).resolve().parent
    file_path = base_dir / "assets" / "NeuroAIHub_Database.xlsx"
    if not os.path.exists(file_path):
        st.error(f"❌ The Excel file '{file_path}' was not found in the app directory.", icon="⚠️")
        st.stop()

    xls = pd.ExcelFile(file_path, engine="openpyxl")
    sheet_names = xls.sheet_names
    dataframes = {
        sheet: pd.read_excel(xls, sheet_name=sheet).assign(category=sheet)
        for sheet in sheet_names
    }


    columns_to_clean = [
    "year", "access_type", "institution", "country", "modality", "resolution",
    "subject_no", "slice_scan_no", "age_range", "disease", "segmentation_mask",
    "healthy_control", "staging_information", "clinical_data_score",
    "histopathology", "lab_data"
]

    # --- Clean each sheet individually ---
    for sheet, df in dataframes.items():
        for col in columns_to_clean:
            if col in df.columns:
                df[col] = df[col].astype(str).replace("nan", "", regex=False).fillna("")
                df[f"{col}_clean"] = df[col].str.replace(r"\s*\(.*\)", "", regex=True).str.strip()
        
        # Convert numeric cleans
        for col in ["year", "subject_no", "slice_scan_no"]:
            clean_col = f"{col}_clean"
            if clean_col in df.columns:
                df[clean_col] = pd.to_numeric(df[clean_col], errors="coerce")

    combined_df = pd.concat(dataframes.values(), ignore_index=True)

    return dataframes, combined_df, sheet_names
