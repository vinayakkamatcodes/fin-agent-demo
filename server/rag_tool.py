import os
from langchain_community.document_loaders import TextLoader
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import CharacterTextSplitter
from langchain_core.tools import tool

# --- 1. SETUP API KEY ---
# (Ensure your real key is here)
if "GOOGLE_API_KEY" not in os.environ:
    os.environ["GOOGLE_API_KEY"] = "" # PASTE KEY HERE

# --- 2. SETUP EMBEDDINGS (Updated Model) ---
# We use the newer 'text-embedding-004' which is more stable
embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")

vector_db = None

def initialize_rag():
    global vector_db
    file_path = "/media/vinayak/New Volume2/programms/python/agents/aiagnets/fin-agent/data/market_report.txt"
    
    # Debug Check 1: Does file exist?
    if not os.path.exists(file_path):
        print(f"❌ Error: File not found at {os.path.abspath(file_path)}")
        return

    # Debug Check 2: Load File
    try:
        loader = TextLoader(file_path)
        documents = loader.load()
        if not documents:
            print("❌ Error: File is empty.")
            return
            
        print(f"✅ Loaded {len(documents)} document(s).")
    except Exception as e:
        print(f"❌ Error loading file: {e}")
        return

    # Debug Check 3: Split Text
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    texts = text_splitter.split_documents(documents)
    
    if len(texts) == 0:
        print("❌ Error: Text splitter resulted in 0 chunks.")
        return
        
    print(f"✅ Split into {len(texts)} chunks. Creating Vector DB...")

    # Create the Vector Database
    try:
        vector_db = FAISS.from_documents(texts, embeddings)
        print("✅ RAG Knowledge Base Built Successfully.")
    except Exception as e:
        print(f"❌ Error creating FAISS index: {e}")

@tool
def ask_market_analyst(question: str) -> str:
    """
    Use this tool to ask questions about the market, trends, or investment advice.
    """
    if vector_db is None:
        initialize_rag()
    
    if vector_db is None:
        return "System Error: Could not load market report."

    try:
        docs = vector_db.similarity_search(question)
        if not docs:
            return "I couldn't find any relevant info in the report."
        return docs[0].page_content
    except Exception as e:
        return f"Error searching data: {e}"