
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_community.document_loaders import WebBaseLoader
import bs4
from langchain_community.document_loaders import UnstructuredMarkdownLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os

os.environ["OPENAI_API_KEY"] = ""

def format_docs(docs):
  return "\n".join(doc.page_content for doc in docs)

def job_retriever():
  # Good match
  # job_link = "https://www.absolventa.de/jobs/channel/webentwicklung/job/angular?job=8814368"
  
  # Bad match
  job_link = "https://www.absolventa.de/stellenangebote?gad_source=1&gclid=CjwKCAjw65-zBhBkEiwAjrqRMByx4MjR15rjQor8ZMFsRHYWdsEvVtpEZgd9GFYXyT1yEzpajXOcCxoCJS8QAvD_BwE&job=8787338"

  job_loader = WebBaseLoader(
      web_paths=(job_link,),
      bs_kwargs=dict(
          parse_only=bs4.SoupStrainer(
              id="inbox-design-main"
          )
      ),
  )

  job = job_loader.load()
  return format_docs(job)
  # text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200, add_start_index=True)
  # job_splits = text_splitter.split_documents(job)
  # embedding = OpenAIEmbeddings()
  # job_store = Chroma(collection_name="job_collection").from_documents(job_splits, embedding=embedding)
  # print(f"[JOB] calling job store as retriever")
  # return job_store.as_retriever()
