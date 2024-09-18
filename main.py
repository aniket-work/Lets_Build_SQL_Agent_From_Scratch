import streamlit as st
import sqlite3
import pandas as pd
import re
from langchain_community.utilities.sql_database import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_experimental.llms.ollama_functions import OllamaFunctions
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import MessageGraph, END
from langgraph.prebuilt import ToolNode

from constants import SQL_AGENT_INSTRUCTIONS
from database import create_database_from_sql


# Database setup functions

def load_database(db_file_path):
    return SQLDatabase.from_uri(f"sqlite:///{db_file_path}")


# SQL query extraction and execution
def extract_sql_query(text):
    match = re.search(r'```sql\n(.*?)\n```', text, re.DOTALL)
    if match:
        return match.group(1)
    return None


def execute_sql_query(db, query):
    try:
        result = db.run(query)
        return pd.read_sql_query(query, db.engine)
    except Exception as e:
        return str(e)


# LangChain and LangGraph setup
def setup_langchain_graph(db):
    llm = OllamaFunctions(model="llama3.1", format="json", temperature=0)
    toolkit = SQLDatabaseToolkit(db=db, llm=llm, use_query_checker=True)
    tools = toolkit.get_tools()
    llm_with_tools = llm.bind_tools(tools)


    prompt = ChatPromptTemplate.from_messages([
        ("system", SQL_AGENT_INSTRUCTIONS),
        ("human", "{input}")
    ])

    oracle_chain = prompt | llm_with_tools

    builder = MessageGraph()

    def oracle_node(state):
        last_message = state[-1]
        response = oracle_chain.invoke({"input": last_message.content})

        # Extract and execute SQL query if present
        sql_query = extract_sql_query(response.content)
        if sql_query:
            query_result = execute_sql_query(db, sql_query)
            response.content += f"\n\nExecuted SQL Query:\n{sql_query}\n\nQuery Result:\n{query_result}"

        return response

    tools_node = ToolNode(tools)

    builder.add_node("oracle_node", oracle_node)
    builder.add_node("tools_node", tools_node)
    builder.add_edge("oracle_node", "tools_node")
    builder.add_edge("tools_node", END)
    builder.set_entry_point("oracle_node")

    return builder.compile()


# Streamlit app
def main():
    st.title("SQL Database Query Assistant")

    # Initialize database and graph
    sql_file_path = "ecommerce_db.sql"
    db_file_path = "ecommerce.db"

    if 'db' not in st.session_state:
        create_database_from_sql(sql_file_path, db_file_path)
        st.session_state.db = load_database(db_file_path)
        st.session_state.graph = setup_langchain_graph(st.session_state.db)

    # User input
    user_query = st.text_input("Enter your database query:")

    if st.button("Submit"):
        if user_query:
            with st.spinner("Processing your query..."):
                result = st.session_state.graph.invoke(user_query)
                st.write("Response:")
                response_content = result[-1].content

                # Split the response into parts
                parts = response_content.split("\n\n")

                # Display LLM's interpretation
                st.write("LLM's Interpretation:")
                st.write(parts[0])

                # Display SQL query if present
                if len(parts) > 1 and parts[1].startswith("Executed SQL Query:"):
                    st.write("Generated SQL Query:")
                    st.code(parts[1].split("\n", 1)[1], language="sql")

                # Display query result if present
                if len(parts) > 2 and parts[2].startswith("Query Result:"):
                    st.write("Query Result:")
                    result_str = parts[2].split("\n", 1)[1]
                    try:
                        result_df = pd.read_json(result_str)
                        st.dataframe(result_df)
                    except:
                        st.write(result_str)
        else:
            st.warning("Please enter a query.")


if __name__ == "__main__":
    main()