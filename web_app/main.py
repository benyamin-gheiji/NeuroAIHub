import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import re
import base64
import json
from data_utils import load_data
from ui_utils import display_paginated_dataframe, get_unique_options_from_column
from agent_setup import setup_agent
from memory_utils import DatasetAwareMemory


st.set_page_config(page_title="NeuroAI Hub", page_icon="🧠", layout="wide")

st.markdown("""
<style>
.stSpinner > div > div { border-top-color: #9c27b0; }
.main .block-container { padding-top: 2rem; }
</style>""", unsafe_allow_html=True)

st.sidebar.header("🔑 API Configuration")
user_api_key = st.sidebar.text_input("Enter your API Key:", type="password", placeholder="sk-...")
user_base_url = st.sidebar.text_input("Base URL:", placeholder="https://api.openai.com/v1")
user_model = st.sidebar.text_input("Model Name:", placeholder="gpt-5")

llm, agent_executor = None, None
if user_api_key:
    try:
        from langchain_openai import ChatOpenAI
        llm = ChatOpenAI(
            openai_api_key=user_api_key.strip(),
            base_url=user_base_url.strip(),
            model_name=user_model.strip(),
            temperature=0
        )
    except Exception as e:
        st.error(f"Failed to initialize LLM: {e}")
else:
    st.sidebar.info("ℹ️ Enter your API key, base URL, and model name to activate the chat agent.")

dataframes, combined_df, sheet_names = load_data()

if llm:
    agent_executor = setup_agent(llm, combined_df, dataframes, sheet_names, user_api_key, user_base_url, user_model)

st.title("🧠 NeuroAI Hub")
st.markdown("Welcome! I'm **NeuroAI**, your assistant for exploring neuroradiology datasets.")
st.info("""
You can interact with the datasets in two ways:

1️⃣ **Direct Controls**: Use the expandable sections below for quick tasks like browsing, filtering, or creating simple plots.

2️⃣ **Chat with NeuroAI**: Use it for more complex questiosns, dataset recommendations, and analytics.
""", icon="👋")

st.divider()

st.subheader("Direct Controls")

with st.expander("📊 **Browse a Category**"):
    selected_category_browse = st.selectbox("Select a category to view its datasets:", options=sheet_names, key="browse_category")
    if st.button("Show Datasets"):
        st.session_state.browse_df = dataframes[selected_category_browse]
        st.session_state.browse_category_name = selected_category_browse
        if 'browse_table' in st.session_state: st.session_state.browse_table = 1 # Reset pagination

if 'browse_df' in st.session_state and st.session_state.browse_df is not None:
    st.markdown(f"### Datasets in the {st.session_state.browse_category_name} Category:")
    display_paginated_dataframe(st.session_state.browse_df, state_key="browse_table")


with st.expander("🔍 **Find Specific Datasets**"):
    with st.form("find_form"):
        st.write("Select your filters. Leave fields blank to ignore them.")
        c1, c2 = st.columns(2)
        with c1:
            sel_category = st.selectbox("Category:", options=["Any"] + sheet_names)
            disease_opt_col = 'disease_clean' if 'disease_clean' in combined_df.columns else 'disease'
            modality_opt_col = 'modality_clean' if 'modality_clean' in combined_df.columns else 'modality'
            sel_disease = st.multiselect("Disease(s):", options=get_unique_options_from_column(combined_df[disease_opt_col]))
            sel_modality = st.multiselect("Modality(s):", options=get_unique_options_from_column(combined_df[modality_opt_col]))
        with c2:
            access_opt_col = 'access_type_clean' if 'access_type_clean' in combined_df.columns else 'access_type'
            segmask_opt_col = 'segmentation_mask_clean' if 'segmentation_mask_clean' in combined_df.columns else 'segmentation_mask'
            sel_access = st.selectbox("Access Type:", options=["Any"] + get_unique_options_from_column(combined_df[access_opt_col]) if access_opt_col in combined_df else ["Any", "Open", "Restricted"])
            seg_mask_options = get_unique_options_from_column(combined_df[segmask_opt_col]) if segmask_opt_col in combined_df else []
            sel_seg_mask = st.selectbox("Segmentation Mask:", options=["Any"] + seg_mask_options)
            year_col = "year_clean" if "year_clean" in combined_df.columns else "year"
            years = pd.to_numeric(combined_df[year_col].replace(["Not specified", "nan", "None", ""], pd.NA), errors="coerce").dropna()
            min_year_val, max_year_val = (int(years.min()), int(years.max())) if not years.empty else (2000, 2025)
            sel_year_range = st.slider("Year Range:", min_value=min_year_val, max_value=max_year_val, value=(min_year_val, max_year_val))

        submitted = st.form_submit_button("Search Datasets")

    if 'find_results' not in st.session_state: st.session_state.find_results = None

    if submitted:
        with st.spinner("Filtering data..."):
            results_df = combined_df.copy()
            if sel_category != "Any": results_df = results_df[results_df['category'] == sel_category]

            disease_col = disease_opt_col
            modality_col = modality_opt_col
            access_col = access_opt_col
            segmask_col = segmask_opt_col

            if sel_disease and disease_col in results_df.columns:
                pattern = '|'.join([re.escape(d) for d in sel_disease])
                results_df = results_df[results_df[disease_col].astype(str).str.contains(pattern, na=False, case=False)]
            if sel_modality and modality_col in results_df.columns:
                pattern = '|'.join([re.escape(m) for m in sel_modality])
                results_df = results_df[results_df[modality_col].astype(str).str.contains(pattern, na=False, case=False)]
            if sel_access != "Any" and access_col in results_df.columns:
                results_df = results_df[results_df[access_col].astype(str).str.fullmatch(re.escape(sel_access), case=False, na=False)]
            if sel_seg_mask != "Any" and segmask_col in results_df.columns:
                results_df = results_df[results_df[segmask_col].astype(str).str.contains(re.escape(sel_seg_mask), na=False, case=False)]

            if 'year_clean' in results_df.columns:
                results_df = results_df[(results_df['year_clean'] >= sel_year_range[0]) & (results_df['year_clean'] <= sel_year_range[1])]
            st.session_state.find_results = results_df
            if 'find_table' in st.session_state: st.session_state.find_table = 1

    if st.session_state.find_results is not None:
        st.markdown(f"### Found {len(st.session_state.find_results)} dataset(s)")
        if not st.session_state.find_results.empty:
            display_paginated_dataframe(st.session_state.find_results, state_key="find_table")


with st.expander("📈 **Create a Quick Plot**"):
    c1, c2, c3 = st.columns(3)
    with c1:
        plot_category = st.selectbox("Filter by Category:", options=["All Categories"] + sheet_names)
    with c2:
        plot_chart_type = st.selectbox("Chart Type:", options=["Bar Chart", "Pie Chart"])
    with c3:
        plot_data_options = {
            "Access Type": "access_type_clean" if "access_type_clean" in combined_df.columns else "access_type",
            "Country": "country_clean" if "country_clean" in combined_df.columns else "country",
            "Modality": "modality_clean" if "modality_clean" in combined_df.columns else "modality",
            "Disease": "disease_clean" if "disease_clean" in combined_df.columns else "disease",
            "Format": "format_clean" if "format_clean" in combined_df.columns else "format",
            "Segmentation Mask": "segmentation_mask_clean" if "segmentation_mask_clean" in combined_df.columns else "segmentation_mask"
        }
        plot_column = st.selectbox("Data to Plot:", options=list(plot_data_options.keys()))

    if st.button("Generate Plot"):
        with st.spinner("Generating plot..."):
            df_for_plot = combined_df
            if plot_category != "All Categories":
                df_for_plot = combined_df[combined_df['category'] == plot_category]

            column_to_plot = plot_data_options[plot_column]
            full_series = df_for_plot[column_to_plot].dropna().astype(str).str.split(',').explode().str.strip()
            full_series = full_series[~full_series.str.lower().isin(['', 'nan', 'not specified'])].value_counts()

            if len(full_series) > 5:
                plot_series = full_series.nlargest(5)
                others_sum = full_series.iloc[5:].sum()
                if others_sum > 0:
                    plot_series = pd.concat([plot_series, pd.Series([others_sum], index=['Others'])])
            else:
                plot_series = full_series

            plot_series = plot_series.sort_values(ascending=False)

            fig, ax = plt.subplots(figsize=(10, 6))
            if "Bar" in plot_chart_type:
                sns.barplot(x=plot_series.index, y=plot_series.values, palette="viridis", ax=ax)
                plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
                ax.set_xlabel(''); ax.set_ylabel('')
            else:
                ax.pie(plot_series.values, labels=plot_series.index, autopct='%1.1f%%', startangle=140, rotatelabels=True, textprops={'fontsize': 8})
                ax.set_ylabel('')

            plt.tight_layout()
            st.pyplot(fig)

            summary_text = f"The chart shows the distribution of **{plot_column}** for **{plot_category}**. "
            summary_list = [f"**{index}** ({value} dataset{'s' if value > 1 else ''})" for index, value in plot_series.items()]
            summary_text += "The breakdown is as follows: " + ", ".join(summary_list) + "."
            st.info(summary_text)

st.divider()
st.subheader("💬 Chat with NeuroAI")

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hello! How can I help you explore the neuroradiology datasets today? Ask me anything!"}]
if "memory" not in st.session_state:
    st.session_state.memory = DatasetAwareMemory(k=5, memory_key="chat_history", return_messages=True)

for i, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"]):
        if "content" in msg and msg["content"]:
            st.markdown(msg["content"])
        if "image_b64" in msg and msg["image_b64"]:
            st.image(base64.b64decode(msg["image_b64"]))
        if "table" in msg and msg["table"] is not None and not msg["table"].empty:
            display_paginated_dataframe(msg["table"], state_key=f"page_agent_{i}")

if not llm or not agent_executor:
    st.info("🧠 Enter your API details in the sidebar to enable the AI chat assistant.")
else:
    if user_query := st.chat_input("Let's talk about neuroradiology datasets!"):
        st.session_state.messages.append({"role": "user", "content": user_query})
        with st.chat_message("user"):
            st.markdown(user_query)
        with st.chat_message("assistant"):
            with st.spinner("🧠 Thinking..."):
                try:
                    inputs = {"input": user_query, "chat_history": st.session_state.memory.load_memory_variables({})['chat_history']}
                    response = agent_executor.invoke(inputs)
                    final_answer = response.get('output', "I'm sorry, I encountered an issue.")

                    assistant_message = {"role": "assistant", "content": final_answer, "table": None, "image_b64": None}

                    if 'intermediate_steps' in response and response['intermediate_steps']:
                        last_action, last_tool_outputervation = response['intermediate_steps'][-1]
                        try:
                            tool_output = json.loads(last_tool_outputervation)
                            if 'data' in tool_output and tool_output['data']:
                                df = pd.DataFrame(tool_output['data'])
                                if not st.session_state.get("last_found_datasets") is df:
                                    assistant_message["table"] = df
                                    st.session_state["last_found_datasets"] = df
                                    st.session_state.memory.save_datasets(df)
                                assistant_message["content"] = final_answer.strip()

                            elif 'image' in tool_output and tool_output['image']:
                                assistant_message["image_b64"] = tool_output['image']
                                text_part = tool_output.get('text', '')
                                combined_text = final_answer.strip()
                                if text_part and text_part not in combined_text:
                                    combined_text += "\n\n" + text_part
                                assistant_message["content"] = combined_text

                            elif 'text' in tool_output:
                                assistant_message["content"] = tool_output['text']
                        except (json.JSONDecodeError, TypeError):
                            assistant_message["content"] = final_answer

                    if assistant_message["content"]:
                        st.markdown(assistant_message["content"])
                    if assistant_message["image_b64"]:
                        st.image(base64.b64decode(assistant_message["image_b64"]))
                    if assistant_message["table"] is not None and not assistant_message["table"].empty:
                        display_paginated_dataframe(assistant_message["table"], state_key=f"page_agent_{len(st.session_state.messages)}")
                        
                    st.session_state.memory.save_context(inputs, {"output": final_answer})
                    st.session_state.messages.append(assistant_message)

                except Exception as e:
                    error_message = f"An unexpected error occurred: {e}"
                    st.error(error_message)
                    st.session_state.messages.append({"role": "assistant", "content": error_message})