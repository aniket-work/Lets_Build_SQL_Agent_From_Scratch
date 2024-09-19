import ast
import os

import pandas as pd
import streamlit as st

import json

from matplotlib import pyplot as plt
from pandasai import Agent
from pandasai.llm.local_llm import LocalLLM

from database import initialize_database
from llm import initialize_llm_and_tools, create_prompt
from graph import create_graph


def flexible_parse(s):
    try:
        # First, try to parse as JSON
        return json.loads(s)
    except json.JSONDecodeError:
        try:
            # If not JSON, try to parse as a Python literal (for tuple lists)
            data = ast.literal_eval(s)

            # If it's a list of tuples, convert to list of dicts
            if isinstance(data, list) and all(isinstance(item, tuple) for item in data):
                return [
                    {f"field_{i}": value for i, value in enumerate(item)}
                    for item in data
                ]

            # If it's already a list of dicts or any other valid Python structure, return as is
            return data
        except:
            # If all parsing attempts fail, return the original string
            return s

def create_dataframe(data):
    if isinstance(data, list) and all(isinstance(item, dict) for item in data):
        return pd.DataFrame(data)
    elif isinstance(data, dict):
        return pd.DataFrame([data])
    else:
        return pd.DataFrame({'data': [data]})

def main():
    st.title("SQL Database Query Assistant")

    # Initialize components
    db = initialize_database()
    llm_with_tools, tools = initialize_llm_and_tools(db)
    prompt = create_prompt()
    graph = create_graph(llm_with_tools, tools, prompt)

    # User input
    user_query = st.text_input("Enter your database query:")

    if st.button("Submit"):
        if user_query:
            with st.spinner("Processing your query..."):
                result = graph.invoke(user_query)
                st.write("Response:")

                content = result[-1].content

                # Try to parse as a list of tuples
                parsed_data = flexible_parse(content)
                print(f"parsed_data : {parsed_data}")
                df = create_dataframe(parsed_data)
                print(f"df : {df}")
                ollama_llm = LocalLLM(api_base="http://localhost:11434/v1", model="llama3.1")
                agent = Agent(df, config={"llm": ollama_llm})
                pandasai_result = agent.chat("Create graph visual")
                # Display the generated chart
                chart_path = 'exports/charts/temp_chart.png'
                if os.path.exists(chart_path):
                    st.subheader("Data Visualization")
                    st.image(chart_path)
                else:
                    st.warning("No chart was generated or the file was not found.")

                if parsed_data:
                    st.subheader("Raw Data")
                    st.json(parsed_data)
                else:
                    try:
                        json_data = json.loads(content)
                        st.subheader("Raw Data")
                        st.json(json_data)
                    except json.JSONDecodeError:
                        st.subheader("Raw Response")
                        st.text(content)
        else:
            st.warning("Please enter a query.")


if __name__ == "__main__":
    main()