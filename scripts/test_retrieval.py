import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from src.config import CHROMA_DIR, EMBEDDING_MODEL

def probar_busqueda():
    embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL)
    vectorstore = Chroma(persist_directory=str(CHROMA_DIR), embedding_function=embeddings)
    
    # Hacemos una pregunta de prueba
    consulta = "¿Cómo puedo proteger las contraseñas de mi empresa?"
    print(f"\n🔍 Consulta: '{consulta}'\n")
    
    # Buscamos los 3 fragmentos más relevantes
    resultados = vectorstore.similarity_search(consulta, k=3)
    
    for i, doc in enumerate(resultados):
        print(f"--- Resultado {i+1} (Fuente: {doc.metadata.get('source', 'Desconocida')}) ---")
        print(doc.page_content[:500] + "...\n")

if __name__ == "__main__":
    probar_busqueda()