import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import SOURCES_DIR
from src.ingestion.loader import cargar_documentos
from src.vectorstore.indexer import crear_base_vectorial

if __name__ == "__main__":
    print("Iniciando proceso de ingesta...")
    docs = cargar_documentos(SOURCES_DIR)
    print(f"Total de documentos cargados: {len(docs)}")
    
    if len(docs) > 0:
        crear_base_vectorial(docs)
    else:
        print("No se encontraron documentos en la carpeta sources/")