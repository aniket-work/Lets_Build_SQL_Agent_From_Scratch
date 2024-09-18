import ast

import streamlit as st

import json
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

                if parsed_data:
                    st.json(parsed_data)
                else:
                    try:
                        # If it's not a list of tuples, try to parse as JSON
                        json_data = json.loads(content)
                        st.json(json_data)
                    except json.JSONDecodeError:
                        # If it's not valid JSON, display as text
                        st.text(content)
        else:
            st.warning("Please enter a query.")


if __name__ == "__main__":
    main()