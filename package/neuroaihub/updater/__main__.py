import time
import pandas as pd
from neuroaihub.updater.llm_client import LLMClient
from neuroaihub.updater.query_generator import generate_search_queries
from neuroaihub.updater.web_search import combined_search
from neuroaihub.updater.text_fetcher import fetch_text
from neuroaihub.updater.extractor import extract_dataset_info
from neuroaihub.updater.updater import (
    save_new_datasets,
    load_existing_datasets,
    filter_new_datasets
)
from neuroaihub.updater.utils import split_text, aggregate_chunk_results


class NeuroAIUpdater:
    def __init__(
        self,
        llm_api_key: str,
        llm_base_url: str,
        llm_model: str,
        serper_api: str,
        tavily_api: str,
        verbose: bool = False,
    ):
        self.llm_api_key = llm_api_key.strip()
        self.llm_base_url = llm_base_url.strip()
        self.llm_model = llm_model.strip()
        self.serper_api = serper_api.strip()
        self.tavily_api = tavily_api.strip()
        self.verbose = verbose
        self.llm = LLMClient(self.llm_api_key, self.llm_base_url, self.llm_model)

    def _log(self, msg):
        if self.verbose:
            print(msg)

    def run(self):
        self._log("\n✅ LLM configuration successful.")
        self._log("🔍 Starting dataset update process...")

        existing_names, existing_dois, existing_urls = load_existing_datasets()

        categories = [
            "Neurodegenerative",
            "Neoplasm",
            "Cerebrovascular",
            "Psychiatric",
            "Spinal",
            "Neurodevelopmental",
        ]

        all_new = []

        for category in categories:
            self._log(f"\n📂 Processing category: {category}")

            queries = generate_search_queries(category)

            combined_urls = pd.DataFrame()
            for q in queries:
                self._log(f"🔍 Searching for: '{q}'")
                results = combined_search(q, self.serper_api, self.tavily_api)
                if not results.empty:
                    combined_urls = pd.concat([combined_urls, results])
                time.sleep(2)

            if combined_urls.empty:
                self._log(f"⚠️ No results found for {category}")
                continue

            combined_urls.drop_duplicates(subset=["url"], inplace=True)

            self._log(f"🔗 {len(combined_urls)} unique URLs collected for {category}.")

            for url in combined_urls['url']:
                self._log(f"\n🌐 Fetching: {url}")

                text = fetch_text(url)
                if not text.strip():
                    self._log("⚠️ Empty or unreadable content, skipping.")
                    continue

                chunks = split_text(text)

                if len(chunks) == 1:
                    data = extract_dataset_info(chunks[0], self.llm)
                    if data:
                        data["Category"] = category
                        all_new.append(data)
                        self._log("✅ Extracted dataset successfully.")
                else:
                    chunk_results = []
                    for chunk in chunks:
                        chunk_data = extract_dataset_info(chunk, self.llm)
                        if chunk_data:
                            chunk_results.append(chunk_data)
                    if chunk_results:
                        final_data = aggregate_chunk_results(chunk_results)
                        final_data["Category"] = category
                        all_new.append(final_data)
                        self._log("✅ Extracted dataset successfully.")

                time.sleep(3)

        if all_new:
            self._log(f"\n💾 {len(all_new)} raw extracted datasets.")
            filtered = filter_new_datasets(
                all_new, existing_names, existing_dois, existing_urls
            )
            save_new_datasets(filtered)
            self._log("🎉 Update complete! New results saved.")
        else:
            self._log("\n⚠️ No new datasets were found during this run.")
