import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage
from src.config import SOURCES_DIR


def _estimar_semaforo(informe_md: str, progreso: int) -> dict:
    texto_lower = informe_md.lower()
    if "optimizado" in texto_lower or "avanzado" in texto_lower:
        estado = "🟢 Bien Cuidado"
        sub = "Buenos hábitos en el equipo"
    elif "gestionado" in texto_lower or "intermedio" in texto_lower:
        estado = "🟡 A Mitad de Camino"
        sub = "Faltan pequeños ajustes"
    else:
        estado = "🟡 Atención Temprana"
        sub = "Fácil de mejorar esta semana"

    lineas = informe_md.splitlines()
    en_brechas = False
    brechas_count = 0
    for linea in lineas:
        if "brechas" in linea.lower() or "puntos" in linea.lower():
            if linea.strip().startswith("#"):
                en_brechas = True
                continue
        if en_brechas and linea.strip().startswith("#"):
            break
        if en_brechas and linea.strip().startswith(("-", "*", "•")):
            brechas_count += 1

    if brechas_count == 0:
        brechas_count = max(3, informe_md.count("- ") // 3)

    return {
        "estado": estado,
        "sub": sub,
        "acciones": f"{brechas_count} mejoras simples",
        "avance": f"{min(progreso, 100)}% completado",
    }


def render_report_panel(generar_informe_fn) -> None:
    """Paso 2 del Wizard con tarjetas pastel y navegación clara."""
    informe = st.session_state.get("informe_final")
    progreso = int(st.session_state.get("progreso", 5))

    if not informe:
        st.markdown(
            """
            <div class="mockup-question-box">
                <div class="mockup-q-pill">🚦 Paso 2 de 3</div>
                <div class="mockup-hola">¡Armemos tu Semáforo!</div>
                <p class="mockup-intro-text">
                    Tocá el botón de abajo para generar tu diagnóstico en palabras simples con lo que ya contaste, o volvé al Paso 1 si querés agregar algo más.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        c1, c2 = st.columns([1, 2])
        with c1:
            if st.button("‹ Volver al Paso 1", use_container_width=True):
                st.session_state.wizard_step = 1
                st.rerun()
        with c2:
            if st.button(
                "✨ Generar mi Semáforo y Plan Ahora ›",
                type="primary",
                use_container_width=True,
            ):
                with st.spinner("Preparando tu semáforo en palabras simples..."):
                    historial_lc = [
                        HumanMessage(content=m["content"])
                        if m["role"] == "user"
                        else AIMessage(content=m["content"])
                        for m in st.session_state.get("messages", [])
                    ]
                    st.session_state.informe_final = generar_informe_fn(historial_lc)
                    st.rerun()
        return

    datos = _estimar_semaforo(informe, progreso)
    k1, k2, k3 = st.columns(3)
    with k1:
        st.markdown(
            f"""
            <div class="pastel-card-amber">
                <div style="font-size: 0.8rem; font-weight: 800; text-transform: uppercase;">🚦 Semáforo Hoy</div>
                <div style="font-size: 1.45rem; font-weight: 800; margin: 0.25rem 0;">{datos["estado"]}</div>
                <div style="font-size: 0.88rem; font-weight: 600;">{datos["sub"]}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with k2:
        st.markdown(
            f"""
            <div class="pastel-card-blue">
                <div style="font-size: 0.8rem; font-weight: 800; text-transform: uppercase;">🛠️ Por Dónde Empezar</div>
                <div style="font-size: 1.45rem; font-weight: 800; margin: 0.25rem 0;">{datos["acciones"]}</div>
                <div style="font-size: 0.88rem; font-weight: 600;">Con programas 100% gratis</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with k3:
        st.markdown(
            f"""
            <div class="pastel-card-green">
                <div style="font-size: 0.8rem; font-weight: 800; text-transform: uppercase;">✅ Tu Relevamiento</div>
                <div style="font-size: 1.45rem; font-weight: 800; margin: 0.25rem 0;">{datos["avance"]}</div>
                <div style="font-size: 0.88rem; font-weight: 600;">Adaptado a tu negocio</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.write("")
    with st.container(border=True):
        st.markdown(informe)

    st.write("")
    c_prev, c_dl, c_next = st.columns([1, 1.3, 1.5])
    with c_prev:
        if st.button("‹ Volver al Paso 1", use_container_width=True):
            st.session_state.wizard_step = 1
            st.rerun()
    with c_dl:
        st.download_button(
            label="📥 Descargar mi Plan (.md)",
            data=informe,
            file_name="Plan_Cuidado_Mi_Negocio.md",
            mime="text/markdown",
            use_container_width=True,
        )
    with c_next:
        if st.button(
            "Ir al Paso 3: Llevate tus guías listas ›",
            type="primary",
            use_container_width=True,
        ):
            st.session_state.wizard_step = 3
            st.rerun()


def render_resources_panel() -> None:
    """Paso 3 del Wizard: Hojas listas para descargar con tarjetas pastel."""
    st.markdown(
        """
        <div class="mockup-question-box">
            <div class="mockup-q-pill">🎁 Paso 3 de 3</div>
            <div class="mockup-hola">Llevate tus Guías Listas</div>
            <p class="mockup-intro-text">
                Poné el nombre de tu comercio o empresa y descargá estas hojas prácticas para compartir por WhatsApp con tu equipo o tener a mano en la oficina.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    nombre_empresa = st.text_input(
        "🏪 Nombre de tu comercio o empresa (opcional):",
        value="",
        placeholder="Ej: Comercio San Martín / Estudio Contable Sur",
    )

    tarjetas = [
        {
            "stem": "politica_contrasenas",
            "clase": "pastel-card-green",
            "icono": "🔑",
            "titulo": "Guía 1: Cuidado de Claves",
            "desc": "Reglas simples para no usar claves fáciles ni compartirlas por chat.",
        },
        {
            "stem": "politica_backups",
            "clase": "pastel-card-blue",
            "icono": "☁️",
            "titulo": "Guía 2: Copias de Archivos",
            "desc": "Cómo guardar las planillas y facturación para no perder nada.",
        },
        {
            "stem": "plan_respuesta_incidentes",
            "clase": "pastel-card-amber",
            "icono": "🛟",
            "titulo": "Guía 3: Qué Hacer ante Estafas",
            "desc": "Los 5 pasos de emergencia si entra un virus o mensaje falso.",
        },
    ]

    cols = st.columns(3)
    templates_dir = SOURCES_DIR / "templates"

    for idx, item in enumerate(tarjetas):
        tpl_path = templates_dir / f"{item['stem']}.md"
        contenido = tpl_path.read_text(encoding="utf-8") if tpl_path.exists() else ""
        if nombre_empresa.strip():
            contenido = contenido.replace("[Nombre de la Empresa]", nombre_empresa.strip())

        with cols[idx]:
            st.markdown(
                f"""
                <div class="{item['clase']}" style="margin-bottom: 0.75rem;">
                    <div style="font-size: 1.9rem; margin-bottom: 0.3rem;">{item['icono']}</div>
                    <div style="font-size: 1.15rem; font-weight: 800; margin-bottom: 0.3rem;">{item['titulo']}</div>
                    <div style="font-size: 0.88rem; font-weight: 600;">{item['desc']}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if contenido:
                st.download_button(
                    label=f"📥 Descargar {item['titulo']}",
                    data=contenido,
                    file_name=f"{item['stem']}.md",
                    mime="text/markdown",
                    key=f"dl_step3_{item['stem']}",
                    use_container_width=True,
                )
                with st.expander("👀 Leer acá mismo"):
                    st.markdown(contenido)

    st.write("")
    c_g1, c_g2 = st.columns(2)
    with c_g1:
        with st.expander("📖 Diccionario en Criollo (Palabras difíciles explicadas fácil)"):
            glosario_path = SOURCES_DIR / "tools" / "glosario.md"
            if glosario_path.exists():
                st.markdown(glosario_path.read_text(encoding="utf-8"))
    with c_g2:
        with st.expander("🛠️ Programas Gratuitos Recomendados para PYMES"):
            tools_path = SOURCES_DIR / "tools" / "catalogo_herramientas_open_source.md"
            if tools_path.exists():
                st.markdown(tools_path.read_text(encoding="utf-8"))

    st.write("")
    c_back, c_reset = st.columns(2)
    with c_back:
        if st.button("‹ Volver al Paso 2 (Mi Semáforo)", use_container_width=True):
            st.session_state.wizard_step = 2
            st.rerun()
    with c_reset:
        if st.button("🔄 Empezar un Diagnóstico Nuevo", type="primary", use_container_width=True):
            st.session_state.wizard_step = 1
            st.session_state.progreso = 5
            st.session_state.informe_final = None
            st.session_state.messages = [st.session_state.messages[0]]
            st.rerun()