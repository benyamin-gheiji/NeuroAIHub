import streamlit as st
import pandas as pd

displaying_columns = [
    "category", "dataset_name", "doi", "url", "year", "access_type",
    "institution", "country", "modality", "resolution", "subject_no",
    "slice_scan_no", "age_range", "acquisition_protocol", "format",
    "segmentation_mask", "preprocessing", "disease", "healthy_control",
    "staging_information", "clinical_data_score", "histopathology", "lab_data"
]

def get_unique_options_from_column(df_column):
    options = df_column.dropna().astype(str).str.split(',').explode().str.strip()
    unique_options = options[~options.str.lower().isin(['not specified', 'nan', ''])]
    return sorted(list(unique_options.unique()))

def display_paginated_dataframe(df: pd.DataFrame, state_key: str, page_size: int = 5):
    """
    Renders a paginated dataframe with clickable links and number formatting.
    """
    if state_key not in st.session_state:
        st.session_state[state_key] = 1

    current_page = st.session_state[state_key]
    total_pages = max(1, (len(df) - 1) // page_size + 1)
    start_index = (current_page - 1) * page_size
    end_index = start_index + page_size

    df_slice = df.iloc[start_index:end_index].copy()

    if "url" in df_slice.columns:
        df_slice["url"] = df_slice["url"].apply(
            lambda x: "Not specified"
            if pd.isna(x)
            or str(x).strip() == ""
            or str(x).strip().lower() == "not specified"
            else str(x).strip()
        )

    df_display = df_slice[[col for col in displaying_columns if col in df_slice.columns]]

    for col in ["year", "subject_no", "slice_scan_no"]:
        if col in df_display.columns:
            df_display[col] = df_display[col].apply(
                lambda x: str(int(x)) if str(x).replace('.', '', 1).isdigit() else str(x)
            )

    column_config = {
        "url": st.column_config.LinkColumn( "URL", display_text="🔗 Link", width="small"),
    }

    st.dataframe(df_display, hide_index=True, use_container_width=True, column_config=column_config)


    c1, c2, c3, c4, c5 = st.columns([2, 2, 3, 2, 2])
    if c1.button("⏮️ First", key=f"first_{state_key}", disabled=(current_page == 1)):
        st.session_state[state_key] = 1; st.rerun()
    if c2.button("◀ Previous", key=f"prev_{state_key}", disabled=(current_page <= 1)):
        st.session_state[state_key] -= 1; st.rerun()
    c3.markdown(f"<p style='text-align: center; margin-top: 8px;'>Page <b>{current_page}</b> of <b>{total_pages}</b></p>", unsafe_allow_html=True)
    if c4.button("Next ▶", key=f"next_{state_key}", disabled=(current_page >= total_pages)):
        st.session_state[state_key] += 1; st.rerun()
    if c5.button("Last ⏭️", key=f"last_{state_key}", disabled=(current_page == total_pages)):
        st.session_state[state_key] = total_pages; st.rerun()
