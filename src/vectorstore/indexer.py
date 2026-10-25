from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from src.config import CHROMA_DIR, EMBEDDING_MODEL, CHUNK_SIZE, CHUNK_OVERLAP

def crear_base_vectorial(documentos):
    print("Dividiendo documentos en fragmentos...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ".", " ", ""]
    )
    chunks = text_splitter.split_documents(documentos)
    print(f"Se generaron {len(chunks)} fragmentos.")
    
    print("Generando embeddings y guardando en ChromaDB (esto puede tardar)...")
    embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL)
    
    # Creamos y persistimos la base de datos
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=str(CHROMA_DIR)
    )
    print("¡Base vectorial creada con éxito!")
    return vectorstore