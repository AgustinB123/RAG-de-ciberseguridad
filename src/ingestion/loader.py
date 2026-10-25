import json
from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_core.documents import Document


def cargar_documentos(directorio_raiz: Path):
    documentos = []

    # 1. Cargar PDFs
    for pdf_path in directorio_raiz.rglob("*.pdf"):
        print(f"Cargando PDF: {pdf_path.name}")
        loader = PyPDFLoader(str(pdf_path))
        docs = loader.load()
        for doc in docs:
            doc.metadata["source"] = pdf_path.name
            doc.metadata["tipo"] = "pdf"
        documentos.extend(docs)

    # 2. Cargar Markdowns (plantillas, glosario, herramientas)
    for md_path in directorio_raiz.rglob("*.md"):
        print(f"Cargando Markdown: {md_path.name}")
        loader = TextLoader(str(md_path), encoding="utf-8")
        docs = loader.load()
        for doc in docs:
            doc.metadata["source"] = md_path.name
            doc.metadata["tipo"] = "markdown"
        documentos.extend(docs)

    # 3. Cargar JSON (mapeo NIST -> CIS -> CISA)
    for json_path in directorio_raiz.rglob("*.json"):
        print(f"Cargando JSON: {json_path.name}")
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if "mapeo" in data:
            for item in data["mapeo"]:
                texto = (
                    f"Función NIST: {item['funcion_nist']}. "
                    f"Control CIS: {item['control_cis']}. "
                    f"Elemento CISA: {item['elemento_cisa']}. "
                    f"Acción para PYME: {item['accion_pyme']}"
                )
                # Crear un objeto Document correctamente
                documentos.append(
                    Document(
                        page_content=texto,
                        metadata={
                            "source": json_path.name,
                            "tipo": "json",
                            "funcion_nist": item["funcion_nist"],
                            "control_cis": item["control_cis"],
                        },
                    )
                )

    return documentos