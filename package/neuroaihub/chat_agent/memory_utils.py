from langchain.memory import ConversationBufferWindowMemory
from pydantic import Field
from typing import List, Any
import json

class DatasetAwareMemory(ConversationBufferWindowMemory):
    dataset_history: List[Any] = Field(default_factory=list)

    def save_datasets(self, df):
        if df is not None and not df.empty:
            self.dataset_history = [df]

    def load_memory_variables(self, inputs):
        vars = super().load_memory_variables(inputs)
        if self.dataset_history:
            last_df = self.dataset_history[-1]
            dataset_json = last_df.to_dict(orient="records")
            vars["last_found_datasets"] = json.dumps(dataset_json, ensure_ascii=False, default=str)
        else:
            vars["last_found_datasets"] = "None"
        return vars