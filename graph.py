from langgraph.graph import MessageGraph, END
from langgraph.prebuilt import ToolNode

def create_graph(llm_with_tools, tools, prompt):
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

    return builder.compile()