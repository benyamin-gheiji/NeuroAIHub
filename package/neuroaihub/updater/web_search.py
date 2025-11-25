import requests
import pandas as pd
from tavily import TavilyClient
import time

def serper_search(query: str, api_key: str, num_results: int = 5) -> pd.DataFrame:
    url = "https://google.serper.dev/search"
    headers = {'X-API-KEY': api_key, 'Content-Type': 'application/json'}
    payload = {"q": query, "num": num_results}

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        response.raise_for_status()
        results = response.json().get("organic", [])
        data = [
            {"Title": r.get("title"), "URL": r.get("link"), "Source": "Serper"}
            for r in results if r.get("link")
        ]
        return pd.DataFrame(data)
    except Exception as e:
        print(f"⚠️ Serper search failed: {e}")
        return pd.DataFrame(columns=["Title", "URL", "Source"])


def tavily_search(query: str, api_key: str, max_results: int = 5) -> pd.DataFrame:
    try:
        client = TavilyClient(api_key=api_key)
        response = client.search(query, max_results=max_results)
        results = response.get("results", [])
        data = [
            {"Title": r.get("title"), "URL": r.get("url"), "Source": "Tavily"}
            for r in results if r.get("url")
        ]
        return pd.DataFrame(data)
    except Exception as e:
        print(f"⚠️ Tavily search failed: {e}")
        return pd.DataFrame(columns=["Title", "URL", "Source"])


def combined_search(query: str, serper_api_key: str, tavily_api_key: str) -> pd.DataFrame:
    
    all_results = []

    try:
        serper_results = serper_search(query, serper_api_key, num_results=5)
        if not serper_results.empty:
            serper_results["source"] = "serper"
            all_results.append(serper_results)
            print(f"✅ Serper returned {len(serper_results)} results.")
    except Exception as e:
        print(f"⚠️ Serper search failed: {e}")

    try:
        tavily_results = tavily_search(query, tavily_api_key, max_results=5)
        if not tavily_results.empty:
            tavily_results["source"] = "tavily"
            all_results.append(tavily_results)
            print(f"✅ Tavily returned {len(tavily_results)} results.")
    except Exception as e:
        print(f"⚠️ Tavily search failed: {e}")

    if not all_results:
        print("⚠️ No results found.")
        return pd.DataFrame()

    combined = pd.concat(all_results, ignore_index=True)
    combined.columns = [c.lower() for c in combined.columns]

    if "url" in combined.columns:
        combined.drop_duplicates(subset=["url"], inplace=True)
    print(f"🔗 Combined {len(combined)} unique URLs.")
    return combined