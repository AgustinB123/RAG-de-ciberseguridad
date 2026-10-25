import sys
import os
import json
from pathlib import Path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from src.rag.pipeline import obtener_cadenas
from src.scoring.engine import ScoringEngine
from src.documents.generator import generar_word
from langchain_core.messages import HumanMessage, AIMessage

st.set_page_config(page_title="Auditor CISO Virtual", page_icon="🛡️", layout="wide")
st.title("🛡️ Auditor de Ciberseguridad para PYMES")
st.markdown("Hola. Soy tu consultor virtual. Contame sobre tu empresa y te haré las preguntas necesarias.")

# Inicializar estado
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({"role": "assistant", "content": "¡Hola! Para arrancar, contame: **¿A qué se dedica tu empresa, cuántos empleados tienen y qué herramientas usan?**"})
if "engine" not in st.session_state:
    st.session_state.engine = ScoringEngine()
if "resumen_actual" not in st.session_state:
    st.session_state.resumen_actual = "Aún no tenemos información."
if "informe_final" not in st.session_state:
    st.session_state.informe_final = None
if "ruta_word" not in st.session_state:
    st.session_state.ruta_word = None

@st.cache_resource
def cargar_modelos():
    return obtener_cadenas()

try:
    cadena_entrevista, generar_informe_profundo = cargar_modelos()
except Exception as e:
    st.error(f"Error al cargar el modelo: {e}")
    st.stop()

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("📊 Estado del Diagnóstico")
    
    st.markdown("### Etapas del Relevamiento")
    for tema, completado in st.session_state.engine.temas.items():
        if completado:
            st.markdown(f"✅ **{tema.title()}**")
        else:
            st.markdown(f"⏳ {tema.title()}")
    
    st.divider()
    progreso_actual = st.session_state.engine.obtener_porcentaje()
    st.progress(progreso_actual / 100)
    st.caption(f"Información recopilada: {progreso_actual}%")
    
    st.divider()
    st.markdown("### 📝 Lo que sabemos:")
    st.info(st.session_state.resumen_actual)
    
    st.divider()
    if st.button("📄 GENERAR INFORME AHORA", type="primary", use_container_width=True):
        with st.spinner("Generando informe..."):
            try:
                historial_langchain = [HumanMessage(content=m["content"]) if m["role"]=="user" else AIMessage(content=m["content"]) for m in st.session_state.messages]
                informe_md = generar_informe_profundo(historial_langchain, st.session_state.resumen_actual)
                st.session_state.informe_final = informe_md
                st.session_state.ruta_word = generar_word(informe_md, "outputs/Informe_PYME.docx")
                st.rerun()
            except Exception as e:
                st.error(f"No se pudo generar el informe: {e}")

if st.session_state.informe_final:
    st.divider()
    st.subheader("📄 Informe generado")
    st.success("El informe se generó correctamente. Podés revisarlo o descargarlo en formato Word.")
    st.markdown(st.session_state.informe_final)

    if st.session_state.ruta_word:
        ruta_word = Path(st.session_state.ruta_word)
        if ruta_word.exists():
            st.download_button(
                "⬇️ Descargar informe Word",
                data=ruta_word.read_bytes(),
                file_name=ruta_word.name,
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True,
            )
        else:
            st.error(f"El informe se generó, pero no se encontró el archivo: {ruta_word}")

# Mostrar chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input
if prompt := st.chat_input("Escribí tu respuesta acá..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    historial_langchain = [HumanMessage(content=m["content"]) if m["role"]=="user" else AIMessage(content=m["content"]) for m in st.session_state.messages[:-1]]

    with st.chat_message("assistant"):
        with st.spinner("Analizando..."):
            try:
                temas_pendientes = st.session_state.engine.obtener_temas_pendientes()
                
                respuesta_json_str = cadena_entrevista.invoke({
                    "question": prompt,
                    "chat_history": historial_langchain,
                    "temas_pendientes": ", ".join(temas_pendientes) if temas_pendientes else "Ninguno. Avisá que ya se puede generar el informe.",
                    "resumen_actual": st.session_state.resumen_actual
                }).content
                
                # Parseamos el JSON
                try:
                    datos = json.loads(respuesta_json_str)
                    mensaje_ia = datos.get("mensaje", "No pude generar la pregunta.")
                    tema = datos.get("tema", "")
                    es_util = datos.get("util", False)
                    nuevo_resumen = datos.get("nuevo_resumen", "")
                    
                    # Lógica de validación
                    if es_util:
                        st.session_state.engine.actualizar_progreso(tema, True)
                        if nuevo_resumen:
                            st.session_state.resumen_actual += f"\n- {nuevo_resumen}"
                    
                    # --- CORTAFUEGOS ANTI-BUCLE ---
                    # Si el mensaje de la IA es idéntico al mensaje anterior, la IA se trabó.
                    if len(st.session_state.messages) > 1:
                        ultimo_mensaje_ia = st.session_state.messages[-1]["content"]
                        if mensaje_ia.strip() == ultimo_mensaje_ia.strip():
                            # Forzamos el avance del tema actual a la fuerza
                            st.session_state.engine.actualizar_progreso(tema, True)
                            mensaje_ia = "Entendido perfectamente. "
                            temas_pendientes = st.session_state.engine.obtener_temas_pendientes()

                    # Red de seguridad
                    if temas_pendientes and "?" not in mensaje_ia:
                        siguiente_tema = temas_pendientes[0].lower()
                        preguntas_respaldo = {
                            "gobernanza": "¿Tienen algún manual o política escrita sobre cómo manejar las contraseñas y la seguridad de la información?",
                            "inventario": "¿Tienen un registro detallado de todos los dispositivos (computadoras, celulares, GPS) y quién los usa?",
                            "proteccion": "¿Usan autenticación de dos pasos (MFA) o tienen contraseñas únicas para acceder a los sistemas de stock y pagos?",
                            "respaldos": "¿Hacen copias de seguridad (backups) de los datos de los clientes y de los camiones? ¿Cada cuánto?",
                            "deteccion": "¿Alguien revisa si hay actividad sospechosa en los sistemas o si alguien intenta acceder sin permiso?",
                            "respuesta": "¿Tienen un plan o protocolo sobre qué hacer si los sistemas se caen o si les piden un rescate por los datos?",
                            "capacitacion": "¿Los empleados recibieron alguna capacitación sobre cómo detectar correos falsos (phishing) o estafas?",
                            "proveedores": "¿Tienen un contrato formal con el programador o proveedor de los sistemas que incluya cláusulas de seguridad?"
                        }
                        pregunta_segura = preguntas_respaldo.get(siguiente_tema, f"¿Me podrías contar un poco más sobre cómo manejan el tema de {siguiente_tema}?")
                        mensaje_ia += f"\n\n{pregunta_segura}"
                except (json.JSONDecodeError, TypeError):
                    mensaje_ia = "No pude interpretar la respuesta del modelo. ¿Podés repetir la información?"

                st.session_state.messages.append({"role": "assistant", "content": mensaje_ia})
                st.markdown(mensaje_ia)
            except Exception as e:
                st.error(f"Error al procesar la respuesta: {e}")