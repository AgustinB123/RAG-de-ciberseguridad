from langchain_chroma import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_ollama import ChatOllama, OllamaEmbeddings

from src.config import CHROMA_DIR, EMBEDDING_MODEL, LLM_MODEL


def obtener_cadenas():
    embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL)
    vectorstore = Chroma(
        persist_directory=str(CHROMA_DIR),
        embedding_function=embeddings,
    )
    retriever = vectorstore.as_retriever(search_kwargs={"k": 4})

    llm_json = ChatOllama(model=LLM_MODEL, temperature=0.0, format="json")
    llm_texto = ChatOllama(model=LLM_MODEL, temperature=0.3)

    # --- CADENA 1: ENTREVISTADOR ---
    system_prompt_entrevista = """Sos un auditor de ciberseguridad. Estás entrevistando a una PYME.

REGLAS CRÍTICAS:
1. SOLO HACÉ PREGUNTAS. No des consejos.
2. Si el usuario dice "NO", "NO TENEMOS" o "NINGUNO", es una respuesta válida:
   usá "util": true y avanzá al siguiente tema.
3. NUNCA REPITAS una pregunta que ya aparezca en el historial.
4. Hacé preguntas naturales y adaptadas al rubro del usuario.

RESUMEN:
{resumen_actual}

TEMAS PENDIENTES:
{temas_pendientes}

RESPONDÉ ÚNICAMENTE CON ESTE JSON:
{{
  "mensaje": "Entendido. [Pregunta del siguiente tema pendiente]",
  "tema": "el_tema_que_acabas_de_evaluar",
  "util": true,
  "nuevo_resumen": "Dato concreto aportado por el usuario"
}}
"""
    prompt_entrevista = ChatPromptTemplate.from_messages([
        ("system", system_prompt_entrevista),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{question}"),
    ])
    cadena_entrevista = (
        {
            "resumen_actual": lambda values: values["resumen_actual"],
            "temas_pendientes": lambda values: values["temas_pendientes"],
            "chat_history": lambda values: values["chat_history"],
            "question": lambda values: values["question"],
        }
        | prompt_entrevista
        | llm_json
    )

    # --- GENERACIÓN DEL INFORME EN TRES PASOS ---
    def generar_informe_profundo(chat_history, resumen_actual):
        analisis_prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                """Sos un analista senior de ciberseguridad.
Analizá la conversación y el resumen de la PYME. Extraé en español:
- el rubro y los procesos críticos;
- los controles existentes;
- las ausencias o debilidades observables;
- el impacto concreto para el negocio.

No inventes información. Si un dato no aparece, indicá "No informado".

RESUMEN:
{resumen_actual}
""",
            ),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "Prepará el análisis estructurado de la situación actual."),
        ])
        analisis = (analisis_prompt | llm_texto | StrOutputParser()).invoke({
            "resumen_actual": resumen_actual,
            "chat_history": chat_history,
        })

        consultas = (
            f"{analisis}\n"
            "NIST CSF 2.0 CIS Controls IG1 políticas gobernanza backups MFA "
            "monitoreo capacitación respuesta a incidentes proveedores"
        )
        documentos = retriever.invoke(consultas)
        contexto_recuperado = "\n\n--- FUENTE ---\n\n".join(
            documento.page_content for documento in documentos
        )

        evidencia_prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                """Sos un especialista en marcos de ciberseguridad.
Relacioná las brechas del análisis con la evidencia técnica recuperada.
Trabajá únicamente con controles y códigos que aparezcan explícitamente en
la evidencia. Si no hay una correspondencia exacta, escribí "Sin código
verificado en la evidencia". Nunca inventes códigos ni asignes un control de
un dominio distinto solo porque el tema parezca relacionado.

ANÁLISIS DE LA EMPRESA:
{analisis}

EVIDENCIA RECUPERADA:
{contexto}
""",
            ),
            ("human", "Prepará una matriz de brecha, riesgo, evidencia y control válido."),
        ])
        mapeo_evidencia = (evidencia_prompt | llm_texto | StrOutputParser()).invoke({
            "analisis": analisis,
            "contexto": contexto_recuperado,
        })

        informe_prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                """Sos un Consultor Senior en Ciberseguridad. Redactá un informe
ejecutivo PREMIUM, EXTENSO Y PROFESIONAL para el dueño de una PYME.

REGLAS OBLIGATORIAS:
1. Todo debe estar en español. Traducí los conceptos técnicos.
2. No uses frases en inglés como "Lack of Security Policies".
3. No inventes controles, códigos, niveles ni datos de la empresa.
4. Usá un código NIST/CIS solo cuando figure como verificado en la matriz.
5. Explicá el impacto real para el negocio y pasos concretos de implementación.
6. Si falta evidencia para una recomendación, indicá qué dato falta.

ANÁLISIS:
{analisis}

MATRIZ DE EVIDENCIA Y CONTROLES:
{mapeo_evidencia}

ESTRUCTURA OBLIGATORIA, CON ESTOS TÍTULOS EXACTOS:

# 🛡️ Informe de Diagnóstico de Ciberseguridad

## 1. Resumen Ejecutivo
Dos párrafos sobre el estado general, principales riesgos y prioridad.

## 2. Análisis de Situación Actual
Describí cómo opera hoy la empresa según la conversación.

## 3. Vulnerabilidades y Riesgos Detectados
Para cada brecha, explicá probabilidad, impacto operativo y consecuencia de negocio.

## 4. Plan de Acción Recomendado
Para cada brecha incluí: **Riesgo**, **Control verificado**, **Cómo implementarlo**
y **Evidencia o limitación**.

## 5. ¿Por dónde empezar? (Prioridades)
Indicá los 2 o 3 pasos más urgentes para esta semana.

## 6. A qué aspirar (Nivel de Madurez)
Estimá el nivel actual solo con la evidencia disponible y proponé un objetivo a seis meses.

## 7. Roadmap (30/60/90 días)
Detallá acciones, responsables sugeridos y resultados esperados.
""",
            ),
            ("human", "Redactá el informe completo en Markdown, con suficiente detalle para varias páginas."),
        ])
        return (informe_prompt | llm_texto | StrOutputParser()).invoke({
            "analisis": analisis,
            "mapeo_evidencia": mapeo_evidencia,
        })

    return cadena_entrevista, generar_informe_profundo