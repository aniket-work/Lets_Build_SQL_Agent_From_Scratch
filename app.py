import streamlit as st
from database import initialize_database
from llm import initialize_llm_and_tools, create_prompt
from graph import create_graph

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
                st.write(result[-1].content)
        else:
            st.warning("Please enter a query.")

if __name__ == "__main__":
    main()