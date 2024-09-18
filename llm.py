from langchain_experimental.llms.ollama_functions import OllamaFunctions
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_core.prompts import ChatPromptTemplate
from database import load_config

def initialize_llm_and_tools(db):
    config = load_config()
    llm_config = config['llm']

    llm = OllamaFunctions(
        model=llm_config['model'],
        format=llm_config['format'],
        temperature=llm_config['temperature']
    )

    toolkit = SQLDatabaseToolkit(db=db, llm=llm, use_query_checker=True)
    tools = toolkit.get_tools()

    llm_with_tools = llm.bind_tools(tools)

    return llm_with_tools, tools

def create_prompt():
    from constants import SQL_AGENT_INSTRUCTIONS
    return ChatPromptTemplate.from_messages([
        ("system", SQL_AGENT_INSTRUCTIONS),
        ("human", "{input}")
    ])