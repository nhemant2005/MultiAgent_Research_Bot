# MultiAgent Research Bot

A multi-agent AI pipeline that takes any research topic and automatically searches the web, scrapes sources, writes a structured report, critiques it, and **revises it based on the critique** — all powered by **DeepSeek V4 Flash** and **Tavily Search**, with a clean **Streamlit** frontend.

---

## Live Demo

**Try it now:** [hemmogptv1.streamlit.app](https://hemmogptv1.streamlit.app/)

> Enter a topic → watch 5 agents work in real time → get a fully written, reviewed, and revised report.

![pipeline](https://img.shields.io/badge/pipeline-5--step-blue?style=flat-square)
![model](https://img.shields.io/badge/model-DeepSeek%20V4%20Flash-6366f1?style=flat-square)
![search](https://img.shields.io/badge/search-Tavily-22c55e?style=flat-square)
![framework](https://img.shields.io/badge/framework-LangChain%20%2B%20LangGraph-f97316?style=flat-square)
![streamlit](https://img.shields.io/badge/deployed-Streamlit%20Cloud-ff4b4b?style=flat-square)

---

## How It Works

The pipeline runs 5 sequential agents/chains:

```
User Topic
    │
    ▼
┌─────────────────────────────────────────────────┐
│  Step 1 · Search Agent                          │
│  Queries Tavily for the 5 most relevant,        │
│  recent sources on the topic.                   │
└──────────────────────┬──────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────┐
│  Step 2 · Reader Agent                          │
│  Picks the best URL from search results and     │
│  scrapes its full content using trafilatura,    │
│  readability, and BeautifulSoup as fallbacks.   │
└──────────────────────┬──────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────┐
│  Step 3 · Writer Chain                          │
│  Combines search + scraped content and drafts   │
│  a structured report: Introduction, Key         │
│  Findings, Conclusion, and Sources.             │
└──────────────────────┬──────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────┐
│  Step 4 · Critic Chain                          │
│  Reviews the draft and returns a score,         │
│  strengths, areas to improve, and a verdict.    │
└──────────────────────┬──────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────┐
│  Step 5 · Reviser Chain                         │
│  Feeds the critic's feedback back to the LLM   │
│  and rewrites the report, fixing every flagged  │
│  issue while preserving all strengths.          │
└──────────────────────┬──────────────────────────┘
                       │
                       ▼
          Final Revised Report + Critic Feedback
```

The original draft is preserved and accessible via an expander for comparison.

---

## Project Structure

```
MultiAgent_Research_Bot/
├── app.py                     # Streamlit frontend
├── main.py                    # CLI entry point
├── requirements.txt
├── .env                       # API keys (not committed)
└── src/
    ├── agents/
    │   └── agents.py          # LLM setup, agent builders, writer, critic & reviser chains
    ├── pipeline/
    │   └── pipeline.py        # Sequential pipeline logic (CLI)
    └── tools/
        └── tools.py           # web_search (Tavily) + scrape_url tools
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| LLM | DeepSeek V4 Flash (via DeepSeek API) |
| Agent framework | LangChain `create_agent` + LangGraph |
| Web search | Tavily Python SDK |
| Web scraping | trafilatura · readability-lxml · BeautifulSoup4 |
| Frontend | Streamlit |
| Deployment | Streamlit Cloud |
| Env management | python-dotenv |

---

## Getting Started

### 1. Clone the repo

```bash
git clone https://github.com/your-username/MultiAgent_Research_Bot.git
cd MultiAgent_Research_Bot
```

### 2. Create and activate a virtual environment

```bash
conda create -n langagent python=3.11
conda activate langagent
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up environment variables

Create a `.env` file in the project root:

```env
DEEPSEEK_API_KEY=your_deepseek_api_key
TAVILY_API_KEY=your_tavily_api_key
```

- Get your DeepSeek API key at [platform.deepseek.com](https://platform.deepseek.com)
- Get your Tavily API key at [tavily.com](https://tavily.com)

### 5. Run the app

**Streamlit UI (recommended)**
```bash
streamlit run app.py
```

**CLI**
```bash
python main.py
```

---

## Usage

1. Open the Streamlit app in your browser (or visit [hemmogptv1.streamlit.app](https://hemmogptv1.streamlit.app/))
2. Enter a research topic in the input bar and click **🚀 Research**
3. Watch all 5 agent steps complete in real time
4. Read the **final revised report** and critic feedback side-by-side
5. Expand **Original Draft** to compare it against the revised version
6. Expand raw search results and scraped content for source data

---

## Configuration

The LLM is configured in `src/agents/agents.py`:

```python
llm = ChatOpenAI(
    model="deepseek-v4-flash",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com",
    extra_body={"thinking": {"type": "disabled"}}  # required for LangChain agent compatibility
)
```

> **Note:** `thinking` mode is explicitly disabled via `extra_body`. DeepSeek V4 Flash defaults to thinking mode, but multi-turn LangGraph agent loops require it to be off — otherwise the API returns a 400 error asking for `reasoning_content` to be echoed back.

---

## Requirements

```
Python >= 3.10
langchain >= 0.2.0
langchain-openai >= 0.1.0
langchain-community >= 0.2.0
langchain-core >= 0.2.0
streamlit >= 1.0.0
tavily-python >= 0.3.0
beautifulsoup4 >= 4.12.0
readability-lxml
trafilatura
requests >= 2.31.0
lxml >= 5.0.0
python-dotenv >= 1.0.0
```

---

## License

[MIT](LICENSE)
