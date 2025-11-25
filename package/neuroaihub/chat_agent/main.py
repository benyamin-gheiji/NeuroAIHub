import base64, json, pandas as pd, io
from pathlib import Path
import matplotlib.pyplot as plt
from IPython.display import display, Image
from langchain_openai import ChatOpenAI
from neuroaihub.chat_agent.agent_setup import setup_agent
from neuroaihub.chat_agent.data_utils import load_data
from neuroaihub.chat_agent.memory_utils import DatasetAwareMemory

class NeuroAIChatAgent:
    def __init__(self, api_key, base_url, model, verbose=False):
        self.api_key = api_key.strip()
        self.base_url = base_url.strip()
        self.model = model.strip()
        self.verbose = verbose
        self.llm = ChatOpenAI(
            openai_api_key=self.api_key,
            base_url=self.base_url,
            model_name=self.model,
            temperature=0
        )
        self.dataframes, self.combined_df, self.sheet_names = load_data()
        self.agent_executor = setup_agent(
            self.llm, self.combined_df, self.dataframes, self.sheet_names,
            self.api_key, self.base_url, self.model, verbose=self.verbose
        )
        self.memory = DatasetAwareMemory(k=5, memory_key="chat_history", return_messages=True)
        self.last_found_datasets = None

    def chat(self, query: str):
        inputs = {"input": query, "chat_history": self.memory.load_memory_variables({})['chat_history']}
        response = self.agent_executor.invoke(inputs)
        final_answer = response.get('output', "I encountered an issue.")
        result = {"text": final_answer, "data": None, "image_b64": None}
        if 'intermediate_steps' in response and response['intermediate_steps']:
            last_action, last_observation = response['intermediate_steps'][-1]
            try:
                tool_output = json.loads(last_observation)
                if 'data' in tool_output and tool_output['data']:
                    df = pd.DataFrame(tool_output['data'])
                    self.last_found_datasets = df
                    self.memory.save_datasets(df)
                    result["data"] = df
                if 'image' in tool_output and tool_output['image']:
                    result["image_b64"] = tool_output['image']
                    txt = tool_output.get('text', '')
                    if txt and txt not in final_answer:
                        result["text"] += "\n\n" + txt
                elif 'text' in tool_output:
                    result["text"] = tool_output['text']
            except Exception:
                pass
        self.memory.save_context(inputs, {"output": final_answer})
        return result
    
    def display(self, result):
        print("\n🧠 NeuroAI says:\n")
        print(result["text"].strip())

        if result["data"] is not None and not result["data"].empty:
            print("\n📊 Showing dataset results:\n")
            try:
                display(result["data"])
            except Exception:
                print(result["data"].to_string(index=False))

        if result["image_b64"]:
            print("\n📈 Showing generated visualization...\n")
            try:
                img_bytes = base64.b64decode(result["image_b64"])
                try:
                    display(Image(data=img_bytes))
                except Exception:
                    img = plt.imread(io.BytesIO(img_bytes), format='png')
                    plt.imshow(img)
                    plt.axis('off')
                    plt.show()
            except Exception as e:
                print(f"[Image display error: {e}]")
