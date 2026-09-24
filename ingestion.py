import os
import glob
from pathlib import Path
from dotenv import load_dotenv

from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

load_dotenv(override=True)
MODEL = "gpt-4.1-nano"

KNOWLEDGE_BASE = "company_docs"
DB_NAME = "vector_db"


# Load genuine PDFs as PDFs. Some sample policy files are plain text despite
# having a .pdf extension, so detect their content before choosing a loader.
def fetch_documents(knowledge_base):
    document_files = glob.glob(str(Path(knowledge_base) / "*.pdf"))
    document_files += glob.glob(str(Path(knowledge_base) / "*.txt"))
    documents = []
    for document_file in document_files:
        with open(document_file, "rb") as file:
            is_pdf = file.read(5) == b"%PDF-"
            if is_pdf:
                loader = PyPDFLoader(document_file)
            else:
                loader = TextLoader(document_file, encoding="utf-8")
        documents.extend(loader.load())
    return documents


# Split documents into small chunks for further RAG processing
def create_chunks(documents):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size = 1000, chunk_overlap = 200)
    chunks = text_splitter.split_documents(documents)
    return chunks


# Convert the chunks into vectors and store them into the vector database
embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
def create_embeddings(chunks, db_name):
    if os.path.exists(db_name):
        return Chroma(persist_directory=db_name, embedding_function=embeddings)

    return Chroma.from_documents(documents=chunks,embedding=embeddings,persist_directory=db_name)


def process_document():
    documents = fetch_documents(KNOWLEDGE_BASE)
    chunks = create_chunks(documents)
    vectorstore = create_embeddings(chunks, DB_NAME)
    return vectorstore
    
