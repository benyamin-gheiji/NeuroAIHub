import pandas as pd
from datetime import datetime
from importlib import resources
import os

def load_existing_datasets():
    try:
        with resources.path("neuroaihub", "NeuroAIHub_Database.xlsx") as db_path:
            database_path = str(db_path)
    except FileNotFoundError:
        print("⚠️ NeuroAIHub_Database.xlsx not found in package.")
        return set(), set(), set()

    try:
        excel_data = pd.read_excel(database_path, sheet_name=None)
        doi_set, url_set, name_set = set(), set(), set()

        for sheet_name, df in excel_data.items():
            for col_name in df.columns:
                if col_name.lower() == "doi":
                    doi_set.update(df[col_name].dropna().astype(str).str.strip())
                elif col_name.lower() == "url":
                    url_set.update(df[col_name].dropna().astype(str).str.strip())
                elif col_name.lower() == "dataset_name":
                    name_set.update(df[col_name].dropna().astype(str).str.strip())

        print(f"📚 Loaded database with {len(name_set)} names, {len(doi_set)} DOIs, {len(url_set)} URLs.")
        return name_set, doi_set, url_set

    except Exception as e:
        print(f"⚠️ Error reading database file: {e}")
        return set(), set(), set()


def filter_new_datasets(new_results, existing_names, existing_dois, existing_urls):
    filtered = []
    for record in new_results:
        name = record.get("dataset_name", "").strip()
        doi = record.get("doi", "").strip()
        url = record.get("url", "").strip()
        if (
            (name and name in existing_names)
            or (doi and doi in existing_dois)
            or (url and url in existing_urls)
        ):
            continue
        filtered.append(record)
    removed = len(new_results) - len(filtered)
    print(f"Removed {removed} duplicate datasets found in database.")
    return filtered


def save_new_datasets(all_results):
    if not all_results:
        print("❌ No new datasets extracted.")
        return None

    df = pd.DataFrame(all_results)
    df.drop_duplicates(subset=["dataset_name", "doi", "url"], inplace=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    filename = f"new_datasets_{timestamp}.xlsx"
    df.to_excel(filename, index=False)
    print(f"✅ New datasets saved to: {filename}")
    return filename
