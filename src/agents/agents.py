from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from tools.tools import web_search, scrape_url 
from dotenv import load_dotenv

load_dotenv()


