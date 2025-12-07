# 🤖🧠 **NeuroAIHub**

**NeuroAIHub** is an AI-driven framework designed to make **neuroradiology dataset discovery** easier, smarter, and always up to date. At its core, it maintains a **continuously updated database** of neuroradiology datasets enriched through an **AI-driven updating pipeline**,  ensuring that new datasets are identified, integrated, and the database is kept up to date with minimal manual effort. Researchers can explore this database either through an **intuitive interactive interface** or by **chatting directly with an AI agent** that understands natural-language questions and retrieves exactly the information they need. Whether you're a **clinician**, **scientist**, or **AI developer**, NeuroAIHub helps you find the right datasets—**quickly, accurately, and effortlessly**. 🚀

---

# 🎥 **Demo Video**

Want a quick overview of how NeuroAIHub works?    
Watch the demo here:    
👉 **[NeuroAIHub Demo Video](https://drive.google.com/file/d/1nG2cF6pN9CP4lofSQuYMhFwRZCHMdxeM/view?usp=drive_link)**  

---

# 🎯 **Key Features**

• **Comprehensive Neuroradiology Dataset Database:** A centrally curated foundational database containing dataset information from six major neuroradiology domains. These entries were initially extracted using a multi-reviewer approach to ensure accuracy, completeness, and consistency. This foundational database is then continuously expanded and maintained through monthly updates, ensuring timely incorporation of newly released neuroradiology datasets.  

• **Conversational Dataset Exploration with the NeuroAI Chat Agent:** Users can interact with the NeuroAI Chat Agent to obtain category-level summaries, retrieve datasets based on natural-language criteria, generate visualizations, and run custom analytical procedures through conversational queries. 

• **Interactive Web Application:** The web application supports both rapid, structured interactions—such as browsing datasets, applying filters, or generating basic plots—and more advanced exploratory tasks through the integrated NeuroAI Chat interface.  

• **Dataset Updating AI Agent:** The NeuroAI Updating Agent autonomously searches the web for newly published neuroradiology datasets and extracts their metadata. This agent is employed in a scheduled monthly workflow to maintain an up-to-date dataset repository.  

• **Open-Source Python Package:** All NeuroAIHub components are available as an open-source Python package, enabling programmatic access, local execution, and full transparency.  

• **Multi-Model Support:** NeuroAIHub supports any OpenAI-compatible model provider. Users can specify their API key, base URL, and model name, enabling flexible integration with a variety of LLM services.  

• **Community-Friendly and Extensible:** Users are encouraged to contribute new datasets, report issues, and propose improvements to strengthen and expand the NeuroAIHub framework.

---

# 🚀 **Getting Started**

NeuroAIHub offers two ways to explore neuroradiology datasets:

🖥️ **1. Interactive Web Application**

🌐 Online Access  
Access instantly at:  
👉 **[https://neuroai.streamlit.app](https://neuroai.streamlit.app)**

💻 Local Access (Run on Your Machine)   
If you prefer to run the app locally or the hosted version is temporarily unavailable, you can launch the exact same interface from the repository:
 ```bash
git clone https://github.com/benyamin-gheiji/NeuroAIHub.git
cd NeuroAIHub/web_app
pip install -r requirements.txt
streamlit run main.py
```
NeuroAIHub web application offers two complementary modes for exploring the database:

🔧 **Direct-Control Interface**

A structured, form-based interface for quick tasks such as browsing datasets, applying filters, inspecting metadata tables, and generating basic plots. Ideal for users who prefer guided, non-conversational interaction.

💬 **NeuroAI Chat Agent Interface**

A conversational mode where users can ask natural-language questions directly to the NeuroAI Chat Agent to obtain information or analyses that go beyond the capabilities of the direct-control interface. This mode is ideal for complex, multi-step, or open-ended queries that require reasoning, interpretation, or dynamic data exploration.

---

📦 **2. Using the NeuroAIHub Python Package**

📥 Install

```bash
pip install neuroaihub
```

The package includes:

* **NeuroAI Chat Agent**
* **NeuroAI Updating Agent**


🤖 **Example: Chat with the NeuroAI Chat Agent**

```python
from neuroaihub import NeuroAIChatAgent

agent = NeuroAIChatAgent(
    api_key="YOUR_API_KEY",
    base_url="e.g https://api.openai.com/v1",
    model="e.g gpt-5"
)

result = agent.chat("I’m planning a deep learning project on brain tumor segmentation. Which datasets would you recommend for this task?")
agent.display(result)
```


🔄 **Example: Run the NeuroAI Updating Agent**

```python
from neuroaihub import NeuroAIUpdater

NeuroAIUpdater(
    llm_api_key="YOUR_API_KEY",
    llm_base_url="https://api.openai.com/v1",
    llm_model="e.g gpt-5",
    serper_api="YOUR_SERPER_KEY",
    tavily_api="YOUR_TAVILY_KEY",
    verbose=True
).run()
```

The Updating Agent will:

✔️ Search the web for new datasets  
✔️ Extract structured metadata  
✔️ Remove duplicates  
✔️ Save new datasets automatically  

---

### 🤝 Community Contributions

NeuroAIHub is designed to grow with the community, and we warmly welcome contributions of all kinds.
Users can help expand and improve the database and platform in several ways:

**• Submit New Datasets via Pull Request**

If you discover a neuroradiology dataset that is not yet included, you can contribute by submitting a Pull Request.  
Users may Use NeuroAIHub’s Updating Agent or any external agentic framework, or Manually search for datasets and extract their metadata.  
Once you obtain the metadata, simply upload a new Excel or CSV file following the standard dataset format (template provided in the repository), and submit it as part of a PR.  
The development team will review the submission, and if validated, add it to the foundational database.  
All contributors whose datasets are accepted will be acknowledged in the GitHub repository.

**• Other Ways to Contribute**

We also welcome contributions such as reporting missing or incorrect metadata, improving code quality, strengthening the agents, enhancing the web application, or providing feedback and suggestions through GitHub Issues.
Any contribution helps advance NeuroAIHub and supports the neuroradiology research community.

---

## 👤 Developed by

**Benyamin Gheiji**

Medical Student  
Machine Learning & Deep Learning Developer  
Passionate about AI/Radiology  

<a href="https://www.linkedin.com/in/benyamin-gheiji-4a0668260">
  <img src="https://img.shields.io/badge/LinkedIn-Connect-blue?style=for-the-badge&logo=linkedin" />
</a>
<a href="https://scholar.google.com/citations?user=0Fdy24gAAAAJ&hl=en">
  <img src="https://img.shields.io/badge/Google_Scholar-Profile-lightgrey?style=for-the-badge&logo=google-scholar" />
</a>
<a href="https://github.com/benyamin-gheiji">
  <img src="https://img.shields.io/badge/GitHub-Profile-black?style=for-the-badge&logo=github" />
</a>
<a href="mailto:benyamingheiji@gmail.com">
  <img src="https://img.shields.io/badge/Email-Contact-red?style=for-the-badge&logo=gmail" />
</a>

-----

# 🙏 **Acknowledgements**

A heartfelt thank you to everyone who contributed to NeuroAIHub.

Special appreciation to my colleagues [**Sina Moradi**](https://www.linkedin.com/in/sinusealpha), [**Mahsa Vatanparast**](https://www.linkedin.com/in/mahsa-vatanparast-24314b2a7), [**Sana Shokrani**](https://www.linkedin.com/in/sana-shokrani-6392512a4), [**Mohammad Aref Bagherzadeh**](https://www.linkedin.com/in/mohammad-aref-bagherzadeh-3a3245a2), [**Danial Elyassirad**](https://www.linkedin.com/in/danial-elyassirad-6aa625245), [**Oluwatobi Iyanuoluwa Akinmuleya**](https://www.linkedin.com/in/akinmuleya), [**Sina Goodarzi**](https://www.linkedin.com/in/sina-goodarzi-6610212a2), and [**Mahsa Heidari-Foroozan**](https://www.linkedin.com/in/mahsa-heidari-foroozan-99969b19a), whose efforts in discovering datasets and extracting metadata were essential in building the foundational database.

Additional thanks to [**Dr. Mana Moassefi**](https://www.linkedin.com/in/mana-moassefi-a6b589119/), [**Dr. Jeffrey Rudie**](https://www.linkedin.com/in/jeff-rudie/), [**Dr. Evan Calabrese**](https://scholar.google.com/citations?user=gNEakpEAAAAJ&hl=en), and [**Dr. Rajan Jain**](https://scholar.google.com/citations?user=Wgi5-XMAAAAJ&hl=en) for their invaluable comments and thoughtful feedback, which helped refine and strengthen the project.

A very special thanks to [**Dr. Shahriar Faghani**](https://www.linkedin.com/in/shahriar-faghani-7b468082) for his visionary idea that inspired this project, and for his invaluable mentorship, encouragement, and guidance. His influence was instrumental in transforming NeuroAIHub from a concept into a working ecosystem.

---

# ⭐ **Support NeuroAIHub**

If you find NeuroAIHub useful or inspiring:  

🌟 **Star the repository** — it truly motivates future development  
🤝 **Contribute** — improve code, add datasets, enhance UI  
📣 **Share** with peers in AI and radiology  

Together, we can make neuroradiology dataset discovery **faster, smarter, and more accessible** for everyone. 🚀







