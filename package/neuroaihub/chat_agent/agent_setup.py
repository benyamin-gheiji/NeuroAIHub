import json, re, base64
from io import BytesIO
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from langchain.agents import Tool, create_react_agent, AgentExecutor
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_experimental.tools.python.tool import PythonAstREPLTool
from neuroaihub.chat_agent.data_helpers import get_unique_options_from_column

def setup_agent(_llm, _combined_df, _dataframes, _sheet_names, api_key, base_url, model, verbose=False):

    def _col(name): 
        return f"{name}_clean" if f"{name}_clean" in _combined_df.columns else name

    def get_category_summary(user_query: str) -> str:
        category_finder_prompt = PromptTemplate.from_template("""
            You are a classification assistant. Your task is to identify which single data category a user is asking about.
            Here is the list of available, official category names: {categories}
            Analyze the user's query below and determine which of the official category names is the best match.
            Respond with ONLY the single, official category name from the list. If no category matches, respond with 'None'.
            User Query: "{query}"
            """
        )
        finder_chain = category_finder_prompt | _llm
        target_category = finder_chain.invoke({"categories": list(_dataframes.keys()), "query": user_query}).content.strip()

        if target_category not in _dataframes:
            return json.dumps({"summary": f"I couldn't determine which category you're asking about. Available categories are: {list(_dataframes.keys())}", "data": None})

        df = _dataframes[target_category].copy()
        disease_col = 'disease_clean' if 'disease_clean' in df.columns else 'disease'
        modality_col = 'modality_clean' if 'modality_clean' in df.columns else 'modality'
        disease_list = df[disease_col].dropna().unique().tolist()
        modality_list = df[modality_col].dropna().unique().tolist()
        years = pd.to_numeric(df['year_clean'], errors='coerce')
        min_year = int(years.min()) if not years.empty else 'N/A'
        max_year = int(years.max()) if not years.empty else 'N/A'

        summary_prompt = PromptTemplate.from_template("""
            You are a data summarization expert. Based on the provided data, create a concise, one-paragraph summary.
            - From the list of diseases, identify and list the top 3 primary conditions, summarizing them cleanly.
            - From the list of modalities, identify and list the top 2 unique modalities.
            DATA:
            - Category Name: {category}
            - Total Datasets: {count}
            - Year Range: {min_year} - {max_year}
            - List of Diseases: {diseases}
            - List of Modalities: {modalities}
            Generate the summary in this exact format:
            "The {category} category contains {count} datasets. They primarily focus on conditions like [Top 4 summarized diseases], using modalities such as [Top 2 unique modalities], with data published between {min_year} and {max_year}."
            """
        )
        summary_chain = summary_prompt | _llm
        summary = summary_chain.invoke({"category": target_category, "count": len(df), "min_year": min_year, "max_year": max_year, "diseases": disease_list, "modalities": modality_list}).content

        output_data = {"summary": summary, "data": df.to_dict(orient='records')}
        return json.dumps(output_data)
    
    def dataset_finder(user_query: str) -> str:
 
        parser_prompt = PromptTemplate.from_template("""
            You are an expert query parser. Your job is to deconstruct the user's query and map it to a structured JSON filter based on the available options.
            User Query: "{query}"
            Available options for filtering:
            - category: {category_options}
            - disease: {disease_options}
            - access_type: {access_type_options}
            - modality: {modality_options}
            - segmentation_mask: {segmentation_mask_options}
            - institution: {institution_options}
            - country: {country_options}
            - format: {format_options}
            - healthy_control: {healthy_control_options}
            - staging_information: {staging_information_options}
            - clinical_data_score: {clinical_data_score_options}
            - histopathology: {histopathology_options}
            - lab_data: {lab_data_options}
            Analyze the user's query and translate it into a JSON object with a 'filters' key.
            - For each field, choose the single best-matching value from its respective options list.
            - For boolean-like fields (e.g., segmentation_mask), map terms like 'with segmentation' to 'Yes' and 'without' to 'No'.
            - For numerical fields like 'year' or 'subjects', create a sub-object with 'operator' and 'value'.
            - If a filter is not mentioned, omit it. Respond with ONLY the JSON object.
            """
        )
        parser_chain = parser_prompt | _llm

        all_options = {
            'category': _sheet_names,
            'access_type': get_unique_options_from_column(_combined_df[_col('access_type')]) if _col('access_type') in _combined_df else [],
            'institution': get_unique_options_from_column(_combined_df[_col('institution')]) if _col('institution') in _combined_df else [],
            'country': get_unique_options_from_column(_combined_df[_col('country')]) if _col('country') in _combined_df else [],
            'modality': get_unique_options_from_column(_combined_df[_col('modality')]) if _col('modality') in _combined_df else [],
            'format': get_unique_options_from_column(_combined_df[_col('format')]) if _col('format') in _combined_df else [],
            'segmentation_mask': get_unique_options_from_column(_combined_df[_col('segmentation_mask')]) if _col('segmentation_mask') in _combined_df else [],
            'disease': get_unique_options_from_column(_combined_df[_col('disease')]) if _col('disease') in _combined_df else [],
            'healthy_control': get_unique_options_from_column(_combined_df[_col('healthy_control')]) if _col('healthy_control') in _combined_df else [],
            'staging_information': get_unique_options_from_column(_combined_df[_col('staging_information')]) if _col('staging_information') in _combined_df else [],
            'clinical_data_score': get_unique_options_from_column(_combined_df[_col('clinical_data_score')]) if _col('clinical_data_score') in _combined_df else [],
            'histopathology': get_unique_options_from_column(_combined_df[_col('histopathology')]) if _col('histopathology') in _combined_df else [],
            'lab_data': get_unique_options_from_column(_combined_df[_col('lab_data')]) if _col('lab_data') in _combined_df else [],
        }

        prompt_input = {"query": user_query}
        for key, value in all_options.items():
            prompt_input[f"{key}_options"] = value

        filter_json_str = parser_chain.invoke(prompt_input).content
        filtered_df = _combined_df.copy()
        try:
            clean_json_str = re.sub(r"```json\n?|```", "", filter_json_str).strip()
            parsed = json.loads(clean_json_str)
            filters = parsed.get("filters", {})
            if not filters:
                return json.dumps({"summary_text": "I couldn't identify any specific search criteria in your request. Please try again.", "data": None})

            for key, value in filters.items():
                key_col = _col(key) if key != 'category' else 'category'

                if isinstance(value, dict): 
                    op, val = value.get('operator'), value.get('value')
                    if key_col in filtered_df.columns:
                        filtered_df[key_col] = pd.to_numeric(filtered_df[key_col], errors='coerce')
                        if isinstance(val, (int, float)):
                            if op == '>': filtered_df = filtered_df[filtered_df[key_col] > val]
                            elif op == '>=': filtered_df = filtered_df[filtered_df[key_col] >= val]
                            elif op == '<': filtered_df = filtered_df[filtered_df[key_col] < val]
                            elif op == '<=': filtered_df = filtered_df[filtered_df[key_col] <= val]
                            elif op == '==': filtered_df = filtered_df[filtered_df[key_col] == val]
                else: 
                    if key == 'category':
                        filtered_df = filtered_df[filtered_df['category'].astype(str).str.fullmatch(str(value), case=False, na=False)]
                    elif key_col in filtered_df.columns:
                        filtered_df = filtered_df[filtered_df[key_col].astype(str).str.contains(str(value), case=False, na=False)]
        except (json.JSONDecodeError, TypeError, KeyError) as e:
            return json.dumps({"summary_text": f"I had trouble understanding your request's structure. Error: {e}", "data": None})

        if filtered_df.empty:
            return json.dumps({"summary_text": "No datasets were found that match your specific criteria.", "data": None})

        count = len(filtered_df)
        summary_text = f"I found {count} dataset(s) matching your criteria. Here are the results:"
        data_as_dict = filtered_df.to_dict(orient='records')
        return json.dumps({"summary_text": summary_text, "data": data_as_dict})
    

    def research_advisor_tool(user_query: str) -> str:

        try:
            finder_output_str = dataset_finder(user_query)
            finder_output = json.loads(finder_output_str)

            datasets = finder_output.get("data", [])
            if not datasets:
                return json.dumps({
                    "summary_text": "No relevant datasets were found for this research topic.",
                    "data": None
                })

            advisor_prompt = PromptTemplate.from_template("""
                You are a research advisor specializing in neuroradiology.
                Given the user's research goal and the list of available datasets,
                identify and rank the most suitable datasets to use.

                Research Goal: "{query}"

                Datasets (as JSON list): {datasets}

                Analyze them and return a concise JSON object with:
                {{
                    "recommendation": "<one short paragraph summarizing which datasets are best and why>",
                    "selected": [{{ <top dataset entries> }}]
                }}
                """)
            advisor_chain = advisor_prompt | _llm

            result = advisor_chain.invoke({
                "query": user_query,
                "datasets": json.dumps(datasets, ensure_ascii=False, default=str)
            }).content

            clean_json = re.sub(r"```json\n?|```", "", result).strip()
            parsed = json.loads(clean_json)
            recommendation = parsed.get("recommendation", "Here are my dataset recommendations.")
            selected = parsed.get("selected", datasets[:5]) 

            return json.dumps({
                "summary_text": recommendation,
                "data": selected
            }, ensure_ascii=False, default=str)

        except Exception as e:
            return json.dumps({
                "summary_text": f"Error running research advisor: {e}",
                "data": None
            })

    def python_repl_wrapper(code: str) -> str:
        try:
            plt.figure(figsize=(10, 6))
            tool_result = PythonAstREPLTool(locals={"pd": pd, "combined_df": _combined_df, "plt": plt, "sns": sns}).run(code)
            fig = plt.gcf()
            if fig.get_axes():
                buf = BytesIO()
                fig.savefig(buf, format="png", bbox_inches='tight')
                buf.seek(0)
                img_base64 = base64.b64encode(buf.read()).decode('utf-8')
                plt.close(fig)
                summary_text = f"Here is the plot you requested. It visualizes the result of your query. The underlying data shows: {str(tool_result)}"
                return json.dumps({"image": img_base64, "text": summary_text})
            else:
                plt.close(fig)
                return json.dumps({"text": str(tool_result)})
        except Exception as e:
            plt.close('all')
            return json.dumps({"text": f"Error executing Python code: {e}"})


    tools = [
        Tool(name="category_summarizer", func=get_category_summary, description="Use this tool for a general overview or summary of a whole data category. The input is the user's natural language query."),
        Tool(name="dataset_finder", func=dataset_finder, description="Use this tool to find and filter datasets based on specific criteria like disease, modality, year, etc. The input is the user's natural language query."),
        Tool( name="research_advisor", func=research_advisor_tool, description="Use this when the user asks for dataset recommendations for a research project or study idea. It analyzes the results from the dataset_finder tool to select the most suitable datasets."),
        Tool(name="python_code_interpreter", func=python_repl_wrapper, description="Use this for complex queries, calculations, comparisons, rankings, or creating any type of plot (bar, pie, line, scatter, etc.). The input must be valid Python code. For plotting, create a plot but DO NOT call plt.show(). The plot will be captured automatically.")
    ]

    prompt_template = """
    You are NeuroAI, a helpful and friendly assistant for exploring neuroradiology datasets. Your goal is to answer user questions accurately by using the tools provided.
    You have access to the following tools: {tools}
    To use a tool, please use the following format:
    ```
    Thought: Do I need to use a tool? Yes
    Action: the action to take, should be one of [{tool_names}]
    Action Input: the input to the action
    tool_outputervation: the result of the action
    ```
    When you have a response to say to the user, or if you do not need to use a tool, you MUST use the format:
    ```
    Thought: Do I need to use a tool? No
    Final Answer: [your response here]
    ```
    **--- CRITICAL TOOL SELECTION RULES ---**
    1. **Summarization Task:** If the user asks for a 'summary', 'overview', or 'description' of a whole data category (e.g., 'summarize the brain tumor datasets'), use `category_summarizer`.
    2. **Finding Task:** For any request to **find, search, or list** datasets with specific filters (e.g., 'find datasets with MRI', 'list stroke datasets after 2020'), you MUST use `dataset_finder`.
    3. **Plotting/Calculation Task:** For any request that requires calculation, ranking, or **creating a plot/chart/graph** (e.g., 'most common', 'compare', 'plot the number of datasets per year', 'create a line chart'), you MUST use `python_code_interpreter`.
    4. **Research Advisory Task:** If the user asks for dataset recommendations for a research goal (e.g., "I want to study glioma segmentation"), use `research_advisor`. It will internally use `dataset_finder` and then analyze which datasets are most relevant.


    Additional Rules:
    - Prefer *_clean columns (e.g., disease_clean, modality_clean) for grouping/counting/plotting to ignore parenthetical notes.
    - When you create categorical plots, limit to the **top 14** categories by count and aggregate the remainder under a single category named **'Others'** (maximum 15 total slices/bars).

    Begin!

    Previous conversation history (last 5 turns):
    {chat_history}

    New input: {input}
    {agent_scratchpad}
    """
    prompt = PromptTemplate.from_template(prompt_template)
    agent = create_react_agent(_llm, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True, return_intermediate_steps=True, max_iterations=5)
    return agent_executor
