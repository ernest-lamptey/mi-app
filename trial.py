import streamlit as st
import os
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI
from langchain_community.tools.tavily_search import TavilySearchResults
import json
from langchain_core.messages import ToolMessage

st.title("Job Application Assistant")

os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = ""
os.environ["OPENAI_API_KEY"] = ""
os.environ["TAVILY_API_KEY"] = ""

tool = TavilySearchResults(max_results=2)
tools = [tool]

llm = ChatOpenAI(model="gpt-3.5-turbo-0125")
# Modification: tell the LLM which tools it can call
llm_with_tools = llm.bind_tools(tools)

class State(TypedDict):
    # Messages have the type "list". The `add_messages` function
    # in the annotation defines how this state key should be updated
    # (in this case, it appends messages to the list, rather than overwriting them)
    messages: Annotated[list, add_messages]

class BasicToolNode:
  """A node that runs the tools requested in the last AIMessage."""

  def __init__(self, tools: list) -> None:
    self.tools_by_name = {tool.name: tool for tool in tools}

  def __call__(self, inputs:dict):
    if messages := inputs.get("messages", []):
        message = messages[-1]
    else:
       raise ValueError("No messages found in inputs")
    outputs = []
    for tool_call in message.tool_calls:
       tool_result = self.tools_by_name[tool_call["name"]].invoke(tool_call["args"])
       outputs.append(
          ToolMessage(
             content=json.dumps(tool_result),
             name=tool_call["name"],
             tool_call_id=tool_call["id"],
          )
       )
    return {"messages": outputs}
  

def chatbot(state: State):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}

# if "messages" not in st.session_state:
#     st.session_state["messages"] =

tool_node = BasicToolNode(tools=[tool])

graph_builder = StateGraph(State)

graph_builder.add_node("chatbot", chatbot)

graph_builder.add_node("tools", tool_node)

graph_builder.add_edge("chatbot", "tools")

graph_builder.set_entry_point("chatbot")

graph_builder.set_finish_point("chatbot")

graph = graph_builder.compile()

user_message = st.chat_input('Enter the question: ')


with st.spinner("Thinking..."):
  if user_message:
    with st.chat_message("user"):
      st.write(user_message)
    for event in graph.stream({"messages": ("user", user_message)}):
      for value in event.values():
        with st.chat_message("Assistant"):
          st.write(value["messages"][-1].content)


# while True:
#     user_input = input("User: ")
#     if user_input.lower() in ["quit", "exit", "q"]:
#         print("Goodbye!")
#         break
#     for event in graph.stream({"messages": ("user", user_input)}):
#         for value in event.values():
#             print("Assistant:", value["messages"][-1].content)