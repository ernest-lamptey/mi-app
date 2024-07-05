import os
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
import bs4
from langchain_chroma import Chroma
from langchain_community.document_loaders import UnstructuredMarkdownLoader
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import PromptTemplate
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

st.title("Job Application Assistant")


LANGCHAIN_TRACING_V2 = os.getenv("LANGCHAIN_TRACING_V2")
LANGCHAIN_API_KEY=  os.getenv("LANGCHAIN_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


markdown_path = "resume.md"
resume_loader = UnstructuredMarkdownLoader(markdown_path)

def format_docs(docs):
    print('docs length: ', len(docs))
    return "\n\n".join(doc.page_content for doc in docs)



llm = ChatOpenAI(model="gpt-3.5-turbo-0125", temperature=0.2, max_tokens=1000)
print('llm instantiated...')

with st.chat_message('Assistant'):
  st.write("Hello! I am your assistant. I can help you answer questions based on the context of a job description. Please enter the job link below and ask a question.")
# Load, chunk and index the contents of the blog.
job_link = st.text_input('Enter the job link: ')
if job_link:
  loader = WebBaseLoader(
      web_paths=(job_link,),
      bs_kwargs=dict(
          parse_only=bs4.SoupStrainer(
              id="inbox-design-main"
          )
      ),
  )

  def load_docs():
    return loader.load()

  docs = load_docs()
  resume = resume_loader.load()

  text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200, add_start_index=True)
  job_splits = text_splitter.split_documents(docs)
  resume_splits = text_splitter.split_documents(resume)
  embedding = OpenAIEmbeddings()

  @st.cache_resource
  def update_docs():
    vectorstore = Chroma()
    cvstore = Chroma()

    for i in range(0, len(job_splits), 3):  # Adjust the 20 based on your token size
      documents = job_splits[i:i+3]  # Adjust the 20 based on your token size
      vectorstore = vectorstore.from_documents(documents=documents, embedding=embedding)
  
    for i in range(0, len(resume_splits), 3):  # Adjust the 20 based on your token size
      markdown = resume_splits[i:i+3]  # Adjust the 20 based on your token size
      cvstore = cvstore.from_documents(documents=markdown, embedding=embedding)

    return vectorstore, cvstore
  vectorstore, cvstore = update_docs()


  # Retrieve and generate using the relevant snippets of the blog.
  retriever = vectorstore.as_retriever()
  retriever2 = cvstore.as_retriever()


  system_prompt = """You are a highly skilled assistant for cover letter and resume writing related
  tasks. Use the following pieces of retrieved context, the job description and resume to perform the writing tasks.
  If you don't know the answer, say that you don't know. Use only information from the context provided.

  Job Description: {context}

  Resume: {context2}
  """

  prompt = ChatPromptTemplate.from_messages(
    [
      ("system", system_prompt),
      ("human", "{input}")
    ]
  )


  rag_chain = (
      {"context": retriever | format_docs, "context2": retriever2}
      | prompt
      | llm
      | StrOutputParser()
  )


  user_message = st.chat_input('Enter the question: ')

  with st.spinner("Thinking..."):
    if user_message:
      with st.chat_message("user"):
        st.write(user_message)
      response1 = rag_chain.invoke({"input": "Write me a cover letter"})
      with st.chat_message("Assistant"):
        st.write(response1)

