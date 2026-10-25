from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from src.config import CHROMA_DIR, EMBEDDING_MODEL, LLM_MODEL

def obtener_cadenas():
    # 1. Conectar a la base de datos
    embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL)
    vectorstore = Chroma(persist_directory=str(CHROMA_DIR), embedding_function=embeddings)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 4}) 
    llm = ChatOllama(model=LLM_MODEL, temperature=0.3)

    # --- CADENA 1: ENTREVISTADOR ESTRICTO ---
    system_prompt_entrevista = """Sos un auditor experto en ciberseguridad para PYMES. 
    Tu ÚNICA tarea en este momento es CONOCER LA EMPRESA Y RELEVAR INFORMACIÓN. 
    
    REGLAS ESTRICTAS (OBLIGATORIO CUMPLIR):
    1. PROHIBIDO DAR SOLUCIONES: No des consejos, no sugieras herramientas (ej. Wazuh, Bitwarden), no expliques cómo hacer un plan de acción. Eso se hará en el informe final.
    2. PROHIBIDO OFRECER AYUDAR: No preguntes "¿Querés que te arme un plan?". Tu trabajo es solo hacer preguntas.
    3. Hacé entre 2 y 3 preguntas por mensaje. No abrumes al usuario.
    4. Validá brevemente lo que dice el usuario (ej: "Entiendo, es común en las PYMES") y pasá INMEDIATAMENTE al siguiente tema.
    5. Si el usuario dice "no tenemos" o "no sé", anotalo internamente y seguí con el siguiente tema. No te quedes dando vueltas sobre la misma falla.
    
    TEMAS A CUBRIR (Seguí este orden mentalmente, si ya preguntaste uno, pasá al siguiente):
    - Contexto (Rubro, empleados, herramientas en la nube).
    - Inventario (¿Saben qué dispositivos y software tienen?).
    - Protección (Contraseñas, MFA, Antivirus, Firewall, Backups).
    - Detección (¿Alguien revisa si hay algo raro?).
    - Respuesta (¿Qué hacen si se rompe todo?).
    - Capacitación (¿El personal sabe detectar estafas?).

    AL FINAL DE TU MENSAJE, incluí SIEMPRE: [PROGRESO: X] (X es un número del 5 al 25 según la calidad de la respuesta). Si ya cubriste todos los temas, escribí [PROGRESO: 100].

    Contexto técnico (Usalo solo para saber qué preguntar, NO para dar soluciones):
    {context}
    """
    
    prompt_entrevista = ChatPromptTemplate.from_messages([
        ("system", system_prompt_entrevista),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{question}")
    ])
    
    cadena_entrevista = (
        {
            "context": lambda x: "\n\n".join(doc.page_content for doc in retriever.invoke(x["question"])),
            "chat_history": lambda x: x["chat_history"],
            "question": lambda x: x["question"]
        }
        | prompt_entrevista
        | llm
        | StrOutputParser()
    )

    # --- CADENA 2: EL GENERADOR DE INFORMES (Multi-pass) ---
    def generar_informe_profundo(chat_history):
        # PASO 1: Extraer brechas y contexto de la conversación
        prompt_extraccion = ChatPromptTemplate.from_messages([
            ("system", "Sos un analista de ciberseguridad. Lee la conversación y extraé una lista en texto plano de las debilidades, faltantes o malas prácticas de la empresa (ej: 'No usan MFA', 'No tienen backups', 'No hay políticas'). Sé conciso."),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "Listá las brechas detectadas.")
        ])
        cadena_extraccion = prompt_extraccion | llm | StrOutputParser()
        brechas = cadena_extraccion.invoke({"chat_history": chat_history})

        # PASO 2: Buscar recomendaciones en la base de datos (NIST/CIS) basadas en las brechas
        contexto_recuperado = "\n\n".join(doc.page_content for doc in retriever.invoke(brechas))

        # PASO 3: Redactar el informe final hermoso
        prompt_final = ChatPromptTemplate.from_messages([
            ("system", """Sos un consultor senior en ciberseguridad. Escribí un informe ejecutivo en formato Markdown.
            Usá un tono profesional pero fácil de entender para dueños de PYMES.
            
            ESTRUCTURA OBLIGATORIA:
            # 🛡️ Informe de Diagnóstico de Ciberseguridad
            
            ## 1. Resumen Ejecutivo
            (Breve texto indicando el nivel de madurez estimado: Básico, Gestionado, etc.)
            
            ## 2. Análisis de Situación Actual
            (Qué está bien y qué es peligroso según la conversación).
            
            ## 3. Brechas Críticas Detectadas
            (Lista con viñetas de los problemas encontrados).
            
            ## 4. Plan de Acción Recomendado (Basado en NIST / CIS)
            (Para cada brecha, dá una solución concreta. Mencioná explícitamente qué control de CIS o función de NIST aplica, y qué herramienta gratuita pueden usar).
            
            ## 5. Próximos Pasos (Roadmap)
            (Qué deberían hacer en los próximos 30, 60 y 90 días).

            Usá la siguiente información de referencia extraída de los estándares para fundamentar tus recomendaciones:
            {contexto}
            """),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "Generá el informe final completo basado en nuestra charla.")
        ])
        cadena_final = prompt_final | llm | StrOutputParser()
        informe = cadena_final.invoke({"chat_history": chat_history, "contexto": contexto_recuperado})
        
        return informe

    return cadena_entrevista, generar_informe_profundo