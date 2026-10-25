import sys
import os
import re
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from src.rag.pipeline import obtener_cadenas
from langchain_core.messages import HumanMessage, AIMessage

# Configuración de la página
st.set_page_config(page_title="Auditor CISO Virtual", page_icon="🛡️", layout="wide")

st.title("🛡️ Auditor de Ciberseguridad para PYMES")
st.markdown("Hola. Soy tu consultor virtual. Contame sobre tu empresa y te haré las preguntas necesarias para diagnosticar tu seguridad.")

# --- INICIALIZAR ESTADO ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "¡Hola! Para arrancar, contame: **¿A qué se dedica tu empresa, cuántos empleados tienen y qué herramientas usan para trabajar (ej. Google Workspace, Microsoft 365, sistemas locales)?**\n\n[PROGRESO: 5]"}
    ]
if "progreso" not in st.session_state:
    st.session_state.progreso = 0
if "informe_final" not in st.session_state:
    st.session_state.informe_final = None

# Cargar modelos
@st.cache_resource
def cargar_modelos():
    return obtener_cadenas()

try:
    cadena_entrevista, generar_informe_profundo = cargar_modelos()
except Exception as e:
    st.error(f"Error al cargar el modelo: {e}")
    st.stop()

# --- BARRA LATERAL (SIDEBAR) CON BOTÓN FLOTANTE ---
with st.sidebar:
    st.header("📊 Estado del Diagnóstico")
    
    # Barra de progreso visual
    st.progress(min(st.session_state.progreso, 100) / 100)
    st.caption(f"Información recopilada: {min(st.session_state.progreso, 100)}%")
    
    st.divider()
    st.markdown("### ¿Ya terminaste?")
    st.markdown("Podés seguir chateando todo lo que quieras. Cuando estés listo, pedí tu informe.")
    
    # EL BOTÓN FLOTANTE
    if st.button("📄 GENERAR INFORME AHORA", type="primary", use_container_width=True):
        with st.spinner("Analizando conversación y buscando en NIST/CIS..."):
            # Preparar historial
            historial_langchain = []
            for msg in st.session_state.messages:
                if msg["role"] == "user":
                    historial_langchain.append(HumanMessage(content=msg["content"]))
                else:
                    historial_langchain.append(AIMessage(content=msg["content"]))
            
            # Generar informe con la función de 3 pasadas
            st.session_state.informe_final = generar_informe_profundo(historial_langchain)
            st.rerun()

# --- FUNCIÓN PARA LIMPIAR EL TEXTO ---
def limpiar_texto(texto):
    return re.sub(r'\[PROGRESO:\s*\d+\]', '', texto).strip()

# --- MOSTRAR HISTORIAL DE CHAT ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(limpiar_texto(message["content"]))

# --- INPUT DEL CHAT (SIEMPRE ABIERTO) ---
if prompt := st.chat_input("Escribí tu respuesta acá..."):
    # Guardar mensaje del usuario
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Preparar historial
    historial_langchain = []
    for msg in st.session_state.messages[:-1]:
        if msg["role"] == "user":
            historial_langchain.append(HumanMessage(content=msg["content"]))
        else:
            historial_langchain.append(AIMessage(content=msg["content"]))

    # Generar respuesta del entrevistador
    with st.chat_message("assistant"):
        with st.spinner("Analizando..."):
            try:
                respuesta_cruda = cadena_entrevista.invoke({
                    "question": prompt,
                    "chat_history": historial_langchain
                })
                
                # Extraer progreso
                match = re.search(r'\[PROGRESO:\s*(\d+)\]', respuesta_cruda)
                if match:
                    incremento = int(match.group(1))
                    if incremento == 100:
                        st.session_state.progreso = 100
                    else:
                        st.session_state.progreso += incremento
                else:
                    st.session_state.progreso += 10

                st.session_state.messages.append({"role": "assistant", "content": respuesta_cruda})
                st.markdown(limpiar_texto(respuesta_cruda))
                st.rerun()

            except Exception as e:
                st.error(f"Error: {e}")

# --- MOSTRAR EL INFORME (Si ya fue generado) ---
if st.session_state.informe_final:
    st.divider()
    st.markdown("## 📄 Tu Informe de Ciberseguridad")
    st.info("👇 Este informe se generó en base a tu conversación. Podés leerlo, descargarlo o copiarlo.")
    
    # Renderizar el informe de forma linda con Markdown
    with st.container(border=True):
        st.markdown(st.session_state.informe_final)
        
    # Botón para descargar el archivo .md
    st.download_button(
        label="⬇️ Descargar Informe en formato de texto (.md)",
        data=st.session_state.informe_final,
        file_name="Informe_Ciberseguridad.md",
        mime="text/markdown"
    )