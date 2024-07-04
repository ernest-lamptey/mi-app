
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
import os

from langchain_community.document_loaders import UnstructuredMarkdownLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

os.environ["OPENAI_API_KEY"] = ""


def format_docs(docs):
  return "\n".join(doc.page_content for doc in docs)

def resume_retriever():
  resume_loader = UnstructuredMarkdownLoader('resume.md', mode="elements")
  resume = resume_loader.load()
  return format_docs(resume)
  # text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=200, add_start_index=True)
  # resume_splits = text_splitter.split_documents(resume)
  # embedding = OpenAIEmbeddings(chunk_size=2000)
  # resume_store = Chroma(collection_name="resume_collection").from_documents(resume_splits, embedding=embedding)
  # print(f"[RESUME] calling resume store as retriever")
  # return resume_store.similarity_search("")