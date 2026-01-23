import os
from dotenv import load_dotenv

from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(__file__))  # backend/
KB_DIR = os.path.join(BASE_DIR, "data", "kb_raw")
DB_DIR = os.path.join(BASE_DIR, "data", "vectordb")

EMB_MODEL = "text-embedding-3-large"

def build_index() -> None:
    os.makedirs(DB_DIR, exist_ok=True)

    loaders = [
        DirectoryLoader(KB_DIR, glob="**/*.md", loader_cls=TextLoader, show_progress=True),
        DirectoryLoader(KB_DIR, glob="**/*.txt", loader_cls=TextLoader, show_progress=True),
    ]

    docs = []
    for l in loaders:
        docs.extend(l.load())

    if not docs:
        raise RuntimeError(f"No documents found in {KB_DIR}. Add .md/.txt files first.")

    splitter = RecursiveCharacterTextSplitter(chunk_size=1200, chunk_overlap=200)
    chunks = splitter.split_documents(docs)

    embeddings = OpenAIEmbeddings(model=EMB_MODEL)
    db = FAISS.from_documents(chunks, embeddings)
    db.save_local(DB_DIR)

    print(f"[OK] Saved FAISS index: {DB_DIR}")
    print(f"docs={len(docs)} chunks={len(chunks)}")

if __name__ == "__main__":
    build_index()