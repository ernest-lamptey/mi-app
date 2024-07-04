import os
from typing import Annotated, TypedDict, List
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver
from langchain_openai import ChatOpenAI
from resume import resume_retriever
from job import job_retriever
import operator
import streamlit as st

from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.messages import AnyMessage, SystemMessage, HumanMessage, AIMessage, ChatMessage
from langchain_community.document_loaders import UnstructuredMarkdownLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langgraph.checkpoint.sqlite import SqliteSaver


os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = ""
os.environ["OPENAI_API_KEY"] = ""
os.environ["TAVILY_API_KEY"] = ""

st.set_page_config(page_title="Job Assistant")
st.title("Job Application Assistant")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

model = ChatOpenAI(model="gpt-3.5-turbo-0125", temperature=0)
memory = SqliteSaver.from_conn_string(":memory:")

class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]


FIT_PROMPT = """
As an expert career evaluator, assess whether the candidate is a good match for the job based on their resume and the job description provided.

Instructions:

Begin by analyzing the key requirements and qualifications listed in the job description.
Compare these requirements with the skills, experiences, and qualifications detailed in the candidate's resume.
Provide a clear and reasoned decision on whether the candidate is a good fit for the job.
Support your decision with specific examples from both the job description and the resume.
Your analysis should be thorough, objective, and professionally written.
The final evaluation should be around 75-100 words in length.

Context:
You have been provided with a candidate's resume and a job description for a specific role. Your task is to carefully evaluate the compatibility between the candidate's qualifications and the job requirements to determine if they are a suitable match for the position.

Candidate's Resume: {resume}

and Job Description: {job_description}
"""

class Agent:
  def __init__(self, model, checkpointer, system=""):
    self.system = system
    graph = StateGraph(AgentState)
    graph.add_node("check_fit", self.check_fit_node)
    graph.set_entry_point("check_fit")
    self.graph = graph.compile(checkpointer=checkpointer)
    self.model = model

  def check_fit_node(self, state: AgentState):
    messages = state['messages']
    if self.system:
       messages = [SystemMessage(content=self.system)] + messages
    message = self.model.invoke(messages)
    return {"messages": [message]}
  
if st.button("Click to start today's briefing"):
  messages = [HumanMessage(content="am I a good fit for the job?")]
  thread = {"configurable": {"thread_id": "testing"}}
  bot = Agent(model, checkpointer=memory, system=FIT_PROMPT.format(resume=resume_retriever(), job_description=job_retriever()))
  for event in bot.graph.stream({"messages": messages}, thread):
    for v in event.values():
      # print(v['messages'])
      answer = v['messages'][-1].content
      with st.chat_message("Assistant"):
        st.write(answer)

# Display chat messages from history on app rerun
for message in st.session_state.messages:
  with st.chat_message(message["role"]):
    st.markdown(message["content"])

user_message = st.chat_input('Any further questions: ')
with st.spinner("Working on it..."):
  if user_message:
    messages = [HumanMessage(content=user_message)]
    with st.chat_message("user"):
      st.write(user_message)
    st.session_state.messages.append({"role": "user", "content": user_message})
    for event in bot.graph.stream({"messages": messages}, thread):
      for v in event.values():
        answer = v['messages'][-1].content
        with st.chat_message("Assistant"):
          st.write(answer)
        st.session_state.messages.append({"role": "Assistant", "content": answer})



# user_message = st.chat_input('Any further questions: ')
# with st.spinner("Working on it..."):
#   if user_message:
#     messages = [HumanMessage(content=user_message)]
#     result = bot.graph.stream({"messages": messages}, thread)
#     st.chat_message('Assistant', result['messages'][-1].content)