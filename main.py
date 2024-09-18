from langchain_community.utilities.sql_database import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_experimental.llms.ollama_functions import (
    OllamaFunctions,
    convert_to_ollama_tool,
)
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import MessageGraph, END
from langgraph.prebuilt import ToolNode


db = SQLDatabase.from_uri("sqlite:///Chinook.db")

import sqlite3
from langchain.sql_database import SQLDatabase


def create_database_from_sql(sql_file_path, db_file_path):
    conn = sqlite3.connect(db_file_path)

    # Try different encodings
    encodings = ['utf-8', 'latin-1', 'utf-16']

    for encoding in encodings:
        try:
            with open(sql_file_path, "r", encoding=encoding) as sql_file:
                sql_script = sql_file.read()
            break  # If successful, break the loop
        except UnicodeDecodeError:
            if encoding == encodings[-1]:  # If this is the last encoding to try
                raise  # Re-raise the exception if all encodings fail
            continue  # Try the next encoding

    conn.executescript(sql_script)
    conn.commit()
    conn.close()
    print(f"Database created at {db_file_path}")


def load_database(db_file_path):
    return SQLDatabase.from_uri(f"sqlite:///{db_file_path}")


# Execute the steps
sql_file_path = "ecommerce_db.sql"
db_file_path = "Chinook.db"

create_database_from_sql(sql_file_path, db_file_path)
db = load_database(db_file_path)

print("Database loaded successfully")


llm = OllamaFunctions(model="llama3.1", format="json", temperature=0)


toolkit = SQLDatabaseToolkit(db=db, llm=llm, use_query_checker=True)
tools = toolkit.get_tools()

llm_with_tools = llm.bind_tools(tools)


SQL_PREFIX = """You are an agent designed to interact with a SQL database.
Given an input question, create a syntactically correct SQLite query to run, then look at the results of the query and return the answer.
Unless the user specifies a specific number of examples they wish to obtain, always limit your query to at most 5 results.
You can order the results by a relevant column to return the most interesting examples in the database.
Never query for all the columns from a specific table, only ask for the relevant columns given the question.
You have access to tools for interacting with the database.
Only use the below tools. Only use the information returned by the below tools to construct your final answer.
You MUST double check your query before executing it. If you get an error while executing a query, rewrite the query and try again.

DO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP etc.) to the database.

To start you should ALWAYS look at the tables in the database to see what you can query.
Do NOT skip this step.
Then you should query the schema of the most relevant tables.
You have access to the following tools:"""

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", SQL_PREFIX),
        ("human", "{input}")
    ]
)

oracle_chain = prompt | llm_with_tools


builder = MessageGraph()

def oracle_node(state):
    last_message = state[-1]
    return oracle_chain.invoke({"input": last_message.content})


tools_node = ToolNode(tools)

builder.add_node("oracle_node", oracle_node)
builder.add_node("tools_node", tools_node)

builder.add_edge("oracle_node", "tools_node")
builder.add_edge("tools_node", END)

builder.set_entry_point("oracle_node")

graph = builder.compile()


query1= "how many tables I have in the database?"
print(query1)
result = graph.invoke(query1)
print(result[-1].content)

query2 = "what is the schema of the Artist table?"
print(query2)
result = graph.invoke(query2)
print(result[-1].content)

query3="Show the first 5 records of the Artist table"
print(query3)
result = graph.invoke(query3)
print(result[-1].content)





