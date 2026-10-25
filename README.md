# ciberseguridad-pyme-rag

Sistema RAG local para diagnosticar el nivel de ciberseguridad de pequeñas y
medianas empresas (PYMES). El proyecto combina documentación de referencia,
embeddings locales y un modelo de lenguaje ejecutado con Ollama para responder
consultas y generar recomendaciones basadas en fuentes verificables.

## Objetivo

La aplicación ayuda a una PYME a:

- identificar riesgos y controles de seguridad relevantes;
- consultar recomendaciones fundamentadas en NIST, CIS y CISA;
- estimar su nivel de madurez mediante un cuestionario;
- recuperar evidencias desde documentación local;
- generar informes y plantillas de políticas de seguridad.

El sistema está pensado para ejecutarse localmente. Los documentos y las
consultas no necesitan enviarse a una API externa.

## Stack tecnológico

- Python 3.11 o superior
- Streamlit para la interfaz web
- LangChain Community para la orquestación RAG
- ChromaDB como base vectorial persistente
- Ollama para ejecutar los modelos localmente
- Llama 3.1 8B como modelo de lenguaje
- Nomic Embed Text como modelo de embeddings
- `pypdf` para procesar documentos PDF
- `reportlab` y `python-docx` para generar informes

## Arquitectura

El flujo principal del sistema es:

1. Los documentos se colocan en `sources/`.
2. El proceso de ingesta recorre los PDFs, extrae su texto y lo divide en
   fragmentos.
3. Los fragmentos se convierten en embeddings con Nomic Embed Text.
4. ChromaDB almacena los embeddings de forma persistente en `chroma_db/`.
5. Ante una consulta, el retriever recupera los fragmentos más relevantes.
6. Llama 3.1 genera una respuesta utilizando el contexto recuperado.
7. La aplicación muestra el diagnóstico y permite preparar un informe.

## Estructura del proyecto

```text
ciberseguridad-pyme-rag/
├── src/
│   ├── ingestion/       # carga, limpieza y división de documentos
│   ├── embedding/       # generación de embeddings
│   ├── vectorstore/     # cliente, indexación y recuperación en ChromaDB
│   ├── rag/              # prompts, pipeline y validación de respuestas
│   ├── scoring/          # preguntas y cálculo de madurez
│   └── documents/        # generación de informes y documentos
├── ui/                   # aplicación Streamlit y componentes visuales
├── sources/              # documentación NIST, CIS, CISA y plantillas
├── data/                 # datos procesados, embeddings e historial local
├── chroma_db/            # persistencia del índice vectorial
├── scripts/              # ingesta y utilidades de ejecución
└── tests/                # pruebas del sistema
```

## Requisitos previos

Se necesita:

- Python 3.11+;
- Ollama instalado y ejecutándose;
- suficiente espacio de disco para los modelos y el índice vectorial.

Descargar los modelos locales:

```bash
ollama pull qwen2.5:7b
ollama pull nomic-embed-text
```

Si Ollama no está ejecutándose, iniciarlo con:

```bash
ollama serve
```

## Instalación

Crear un entorno virtual e instalar las dependencias:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

Crear la configuración local a partir del ejemplo:

```bash
cp .env.example .env
```

Las variables principales son:

| Variable          | Valor por defecto        | Descripción                              |
| ----------------- | ------------------------ | ---------------------------------------- |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | URL del servicio Ollama                  |
| `LLM_MODEL`       | `qwen2.5:7b`             | Modelo utilizado para generar respuestas |
| `EMBEDDING_MODEL` | `nomic-embed-text`       | Modelo utilizado para embeddings         |
| `CHROMA_PATH`     | `./chroma_db`            | Ubicación persistente de ChromaDB        |

## Uso

Colocar los documentos fuente en las carpetas correspondientes dentro de
`sources/` y ejecutar la ingesta:

```bash
python scripts/ingest.py
```

Luego iniciar la interfaz:

```bash
streamlit run ui/app.py
```

También se puede utilizar el script de arranque:

```bash
./scripts/run.sh
```

La aplicación estará disponible normalmente en `http://localhost:8501`.

## Pruebas

Ejecutar las pruebas con:

```bash
pytest
```

Los tests cubren el particionado de documentos, la recuperación vectorial y
el cálculo del nivel de madurez.

## Estado del proyecto

La estructura inicial y los puntos de integración están preparados. Los
módulos marcados con `TODO` deben completarse para conectar todos los pasos del
pipeline: carga y limpieza de documentos, embeddings, indexación, recuperación,
scoring y generación de informes.

## Privacidad y datos generados

El proyecto está diseñado para trabajar localmente. Los directorios
`chroma_db/`, `outputs/` y `data/chat_history/` contienen datos generados y
están excluidos del control de versiones. No se debe subir el archivo `.env`,
porque puede contener configuración específica del entorno.
