import cassio
from langchain_community.document_loaders import WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Cassandra
from langchain.indexes.vectorstore import VectorStoreIndexWrapper
from app.config import ASTRA_DB_ID , ASTRA_DB_APPLICATION_TOKEN

print("document ingestion start......................")

# Initialize AstraDB connection
cassio.init(token=ASTRA_DB_APPLICATION_TOKEN, database_id=ASTRA_DB_ID)

print("done cassio init......................")

# Initialize embeddings and vector store
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
astra_vector_store = Cassandra(
    embedding=embeddings,
    table_name="qa_mini_demo",
    session=None,
    keyspace=None
)

def ingest_data(urls: list[str]):
    """
    Ingest data from the provided list of URLs into AstraDB.
    """
    print("urls--------->" , urls)
    docs = [WebBaseLoader(url).load() for url in urls]
    print("docs---------->")
    docs_list = [item for sublist in docs for item in sublist]
    print("before recursive---------->")
    # Split documents into smaller chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=0)
    print("before text splitt---------->")
    doc_splits = text_splitter.split_documents(docs_list)
    print("before doc add---------->")
    # Add the documents to the Astra vector store
    astra_vector_store.add_documents(doc_splits)
    print("end of function---------->")

def clear_database():
    """
    Clears all data from the AstraDB vector store.
    """
    astra_vector_store.clear()  # Clear the entire vector store
    print("Database cleared.")

astra_vector_index = VectorStoreIndexWrapper(vectorstore=astra_vector_store)
retriever = astra_vector_store.as_retriever()