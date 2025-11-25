import pandas as pd
from importlib import resources

def load_data():
    try:
        with resources.path("neuroaihub", "NeuroAIHub_Database.xlsx") as db_path:
            xls = pd.ExcelFile(db_path, engine="openpyxl")
    except FileNotFoundError:
        raise FileNotFoundError("NeuroAIHub_Database.xlsx not found in package.")

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
    for sheet, df in dataframes.items():
        for col in columns_to_clean:
            if col in df.columns:
                df[col] = df[col].astype(str).replace("nan", "", regex=False).fillna("")
                df[f"{col}_clean"] = df[col].str.replace(r"\s*\(.*\)", "", regex=True).str.strip()

        for col in ["year", "subject_no", "slice_scan_no"]:
            clean_col = f"{col}_clean"
            if clean_col in df.columns:
                df[clean_col] = pd.to_numeric(df[clean_col], errors="coerce")

    combined_df = pd.concat(dataframes.values(), ignore_index=True)

    return dataframes, combined_df, sheet_names
