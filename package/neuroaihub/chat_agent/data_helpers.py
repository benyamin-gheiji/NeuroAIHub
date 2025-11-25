import pandas as pd
def get_unique_options_from_column(df_column):
    options = df_column.dropna().astype(str).str.split(',').explode().str.strip()
    unique_options = options[~options.str.lower().isin(['not specified', 'nan', ''])]
    return sorted(list(unique_options.unique()))