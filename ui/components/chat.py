import re
import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage
from ui.components.progress_bar import render_topic_pills


# Cada etapa tiene 5 botones horizontales pastel (Verde, Celeste, Lila, Amarillo, Gris) como en la imagen
OPCIONES_5_TARJETAS = [
    # Pregunta 1: Rubro
    [
        {
            "label": "🏪  Comercio  ›",
            "texto": "Tenemos un comercio o local de atención al público. Usamos WhatsApp, Gmail, Excel y sistema de facturación.",
        },
        {
            "label": "⚙️  Servicio profesional  ›",
            "texto": "Somos un estudio o empresa de servicios profesionales. Trabajamos con notebooks, correo y archivos en la nube.",
        },
        {
            "label": "🏭  Producción  ›",
            "texto": "Nos dedicamos a producción o taller. Usamos computadoras en oficina, correo y sistema de gestión local.",
        },
        {
            "label": "🖥️  Trabajo remoto  ›",
            "texto": "Trabajamos de forma remota con herramientas en la nube, videollamadas, WhatsApp y carpetas compartidas.",
        },
        {
            "label": "•••  Otro  ›",
            "texto": "Somos una PYME que usa correo electrónico, WhatsApp y planillas todos los días para trabajar.",
        },
    ],
    # Pregunta 2: Compus y celus
    [
        {
            "label": "💻  Solo compus del local  ›",
            "texto": "Usamos únicamente las computadoras del negocio y sabemos bien cuáles son.",
        },
        {
            "label": "📱  Mezcla con celus propios  ›",
            "texto": "Usamos computadoras de la empresa pero también los celulares personales de cada empleado.",
        },
        {
            "label": "🏠  Cada uno usa su notebook  ›",
            "texto": "Varios trabajan desde sus propias notebooks o computadoras personales sin un registro formal.",
        },
        {
            "label": "📋  Tenemos lista de equipos  ›",
            "texto": "Llevamos un control anotado de las computadoras y programas que tiene la empresa.",
        },
        {
            "label": "•••  No llevamos control  ›",
            "texto": "No tenemos anotado qué dispositivos ni qué programas están instalados hoy.",
        },
    ],
    # Pregunta 3: Contraseñas
    [
        {
            "label": "📓  Anotadas en papel/Excel  ›",
            "texto": "Anotamos las contraseñas en un cuaderno o planilla y varios usan la misma clave.",
        },
        {
            "label": "🔓  Sin segundo código celu  ›",
            "texto": "Cada uno tiene su contraseña pero no tenemos activado el segundo código en el celular (MFA).",
        },
        {
            "label": "📲  Con código en el celu  ›",
            "texto": "Tenemos activada la verificación de dos pasos en el celular para el correo principal.",
        },
        {
            "label": "🔐  Usamos gestor de claves  ›",
            "texto": "Guardamos las contraseñas en un programa gestor seguro y usamos segundo factor.",
        },
        {
            "label": "•••  Compartimos las claves  ›",
            "texto": "Compartimos las claves por WhatsApp cuando alguien necesita entrar.",
        },
    ],
    # Pregunta 4: Copias de archivos y estafas
    [
        {
            "label": "💾  Solo en la computadora  ›",
            "texto": "Guardamos todo en las computadoras sin hacer copias automáticas afuera.",
        },
        {
            "label": "🔌  Disco externo cada tanto  ›",
            "texto": "Cada tanto pasamos archivos importantes a un pendrive o disco externo de forma manual.",
        },
        {
            "label": "☁️  Google Drive / Nube  ›",
            "texto": "Subimos las cosas a Google Drive o OneDrive, aunque nunca probamos restaurar ni tenemos guía ante virus.",
        },
        {
            "label": "🛡️  Copia diaria + antivirus  ›",
            "texto": "Tenemos copias en la nube y antivirus, pero nos falta capacitar al equipo contra estafas.",
        },
        {
            "label": "•••  No sabemos qué hacer  ›",
            "texto": "No tenemos copias automáticas ni sabemos bien a quién llamar si nos entra un virus o estafa.",
        },
    ],
]


def limpiar_texto(texto: str) -> str:
    """Elimina la etiqueta interna [PROGRESO: X] para mostrar el mensaje limpio."""
    return re.sub(r"\[PROGRESO:\s*\d+\]", "", texto).strip()


def _construir_historial_lc(messages: list[dict]) -> list:
    historial = []
    for msg in messages:
        if msg["role"] == "user":
            historial.append(HumanMessage(content=msg["content"]))
        else:
            historial.append(AIMessage(content=msg["content"]))
    return historial


def _extraer_y_actualizar_progreso(respuesta_cruda: str) -> None:
    match = re.search(r"\[PROGRESO:\s*(\d+)\]", respuesta_cruda)
    progreso_actual = int(st.session_state.get("progreso", 5))
    if match:
        valor = int(match.group(1))
        if valor >= 100:
            st.session_state.progreso = 100
        else:
            st.session_state.progreso = min(100, progreso_actual + valor)
    else:
        st.session_state.progreso = min(100, progreso_actual + 25)


def _enviar_respuesta(prompt: str, cadena_entrevista) -> None:
    st.session_state.messages.append({"role": "user", "content": prompt})
    historial_lc = _construir_historial_lc(st.session_state.messages[:-1])

    with st.spinner("Un segundo..."):
        try:
            respuesta_cruda = cadena_entrevista.invoke(
                {
                    "question": prompt,
                    "chat_history": historial_lc,
                }
            )
            _extraer_y_actualizar_progreso(respuesta_cruda)
            st.session_state.messages.append(
                {"role": "assistant", "content": respuesta_cruda}
            )
        except Exception as e:
            st.error(f"Hubo un inconveniente al consultar al asistente: {e}")


def render_chat(cadena_entrevista, generar_informe_fn) -> None:
    """Renderiza la tira de 5 temas, la tarjeta blanca idéntica al mockup y las 5 tarjetas pastel."""
    messages = st.session_state.get("messages", [])
    respuestas_dadas = sum(1 for m in messages if m["role"] == "user")
    ultimo_msg = next(
        (limpiar_texto(m["content"]) for m in reversed(messages) if m["role"] == "assistant"),
        "",
    )

    # 1. Tira de las 5 tarjetas de temas (Ahora: Tu rubro | Compus y celus | Contraseñas | Copias | Cuidado)
    render_topic_pills()

    # 2. Tarjeta Blanca Principal de la Pregunta (idéntica al mockup en el turno inicial)
    if respuestas_dadas == 0:
        cuerpo_html = """
        <div class="mockup-question-box">
            <div class="mockup-q-pill">💬 Pregunta 1 del Asistente</div>
            <div class="mockup-hola">¡Hola! <span class="mockup-hola-rays">☄️</span></div>
            <p class="mockup-intro-text">
                Vamos a revisar cómo proteger tu negocio de estafas o pérdida de archivos.<br>
                Para empezar, contame o elegí un botón:
            </p>
            <p class="mockup-bold-question">
                ¿A qué se dedica tu negocio, cuántas personas trabajan con vos y qué usan todos los días
                (WhatsApp, Gmail, Excel, sistema de facturación)?
            </p>
        </div>
        """
    else:
        cuerpo_html = f"""
        <div class="mockup-question-box">
            <div class="mockup-q-pill">💬 Pregunta {respuestas_dadas + 1} del Asistente</div>
            <p class="mockup-bold-question" style="margin-top: 0.2rem;">
                {ultimo_msg}
            </p>
        </div>
        """

    st.markdown(cuerpo_html, unsafe_allow_html=True)

    # 3. Las 5 Tarjetas Pastel en una fila horizontal (Verde, Celeste, Lila, Amarillo, Gris)
    grupo_idx = min(respuestas_dadas, len(OPCIONES_5_TARJETAS) - 1)
    opciones = OPCIONES_5_TARJETAS[grupo_idx]

    cols = st.columns(5)
    for idx, op in enumerate(opciones):
        with cols[idx]:
            if st.button(
                op["label"],
                key=f"pastel_btn_{respuestas_dadas}_{idx}",
                use_container_width=True,
            ):
                _enviar_respuesta(op["texto"], cadena_entrevista)
                st.rerun()

    # Input por si prefiere escribir con teclado
    if prompt := st.chat_input(
        "O escribí acá con tus palabras y presioná Enter..."
    ):
        _enviar_respuesta(prompt, cadena_entrevista)
        st.rerun()

    # Barra de avance hacia el Paso 2 cuando ya contestó al menos 1 pregunta
    if respuestas_dadas > 0:
        st.write("")
        c_left, c_mid, c_right = st.columns([1.2, 1.5, 1.5])
        with c_left:
            if st.button("🔄 Volver a empezar", use_container_width=True):
                st.session_state.messages = [messages[0]]
                st.session_state.progreso = 5
                st.session_state.informe_final = None
                st.rerun()
        with c_mid:
            with st.expander(f"👀 Ver mis respuestas ({respuestas_dadas})"):
                for m in messages:
                    if m["role"] == "user":
                        st.markdown(f"- 🙋 _{m['content']}_")
        with c_right:
            if st.button(
                "Ir al Paso 2: Mirá tu semáforo y plan ›",
                type="primary",
                use_container_width=True,
            ):
                with st.spinner("Armando tu semáforo y plan en palabras simples..."):
                    historial_lc = _construir_historial_lc(st.session_state.get("messages", []))
                    st.session_state.informe_final = generar_informe_fn(historial_lc)
                    st.session_state.wizard_step = 2
                    st.rerun()