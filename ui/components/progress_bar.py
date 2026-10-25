import streamlit as st


ESTACIONES_CHARLA = [
    {"nombre": "Tu rubro", "umbral": 15, "icono": "📖"},
    {"nombre": "Compus y celus", "umbral": 35, "icono": "💻"},
    {"nombre": "Contraseñas", "umbral": 55, "icono": "🔑"},
    {"nombre": "Copias de archivos", "umbral": 80, "icono": "📄"},
    {"nombre": "Cuidado ante estafas", "umbral": 100, "icono": "⚠️"},
]

SVG_SHIELD_ICON = """
<svg width="46" height="46" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M32 6L12 14V30C12 43.8 20.5 55.9 32 60C43.5 55.9 52 43.8 52 30V14L32 6Z" fill="#2563EB"/>
  <path d="M32 6V60C43.5 55.9 52 43.8 52 30V14L32 6Z" fill="#60A5FA"/>
  <circle cx="32" cy="31" r="9" fill="#FFFFFF"/>
</svg>
"""

SVG_LAPTOP_PLANT = """
<svg width="260" height="125" viewBox="0 0 280 130" fill="none" xmlns="http://www.w3.org/2000/svg">
  <ellipse cx="155" cy="115" rx="95" ry="12" fill="#E2F2EE"/>
  <!-- Planta -->
  <path d="M72 95C62 78 48 72 48 72C48 72 52 88 66 98" fill="#0D9488"/>
  <path d="M74 95C74 74 65 56 65 56C65 56 82 68 78 94" fill="#14B8A6"/>
  <path d="M76 96C86 80 98 72 98 72C98 72 94 89 79 98" fill="#0D9488"/>
  <rect x="63" y="94" width="22" height="22" rx="4" fill="#F8FAFC" stroke="#CBD5E1" stroke-width="2"/>
  <!-- Laptop -->
  <rect x="112" y="34" width="116" height="74" rx="8" fill="#1E293B"/>
  <rect x="118" y="40" width="104" height="62" rx="4" fill="#EFF6FF"/>
  <rect x="96" y="108" width="148" height="8" rx="4" fill="#64748B"/>
  <!-- Escudo en pantalla -->
  <path d="M170 48L152 55V69C152 80.5 159.7 90.6 170 94C180.3 90.6 188 80.5 188 69V55L170 48Z" fill="#3B82F6"/>
  <circle cx="170" cy="70" r="9" fill="#FFFFFF"/>
  <path d="M166 70L169 73L175 67" stroke="#2563EB" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
  <!-- Rayos -->
  <line x1="192" y1="22" x2="196" y2="12" stroke="#0D9488" stroke-width="3" stroke-linecap="round"/>
  <line x1="205" y1="26" x2="213" y2="18" stroke="#0D9488" stroke-width="3" stroke-linecap="round"/>
  <line x1="214" y1="35" x2="224" y2="30" stroke="#0D9488" stroke-width="3" stroke-linecap="round"/>
</svg>
"""


def render_wizard_header() -> None:
    """Renderiza el Hero Banner idéntico al mockup y los 3 escalones conectados."""
    paso_actual = int(st.session_state.get("wizard_step", 1))

    # 1. Hero Banner Blanco con Escudo, Título Bicolor, Ilustración Laptop/Planta y Tarjeta Crema
    st.markdown(
        f"""
        <div class="mockup-hero">
            <div class="mockup-hero-left">
                <div class="mockup-shield-circle">
                    {SVG_SHIELD_ICON}
                </div>
                <div>
                    <h1 class="mockup-hero-title">
                        Cuidá tu Negocio
                        <span>en 3 Pasos Simples</span>
                    </h1>
                    <p class="mockup-hero-sub">
                        Te damos herramientas prácticas para proteger tu trabajo diario sin complicaciones.
                    </p>
                </div>
            </div>
            <div class="mockup-hero-art">
                {SVG_LAPTOP_PLANT}
            </div>
            <div class="mockup-cream-box">
                <div class="mockup-cream-item">
                    <span class="mockup-check-dot">✓</span> Práctico
                </div>
                <div class="mockup-cream-item">
                    <span class="mockup-check-dot">✓</span> Paso a paso
                </div>
                <div class="mockup-cream-item">
                    <span class="mockup-check-dot">✓</span> Sin tecnicismos
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 2. Stepper Horizontal con línea conectora (Paso 1 de 3 — Paso 2 de 3 — Paso 3 de 3)
    c1_active = "active" if paso_actual == 1 else ""
    c2_active = "active" if paso_actual == 2 else ""
    c3_active = "active" if paso_actual == 3 else ""

    st.markdown(
        f"""
        <div class="mockup-stepper-wrap">
            <div class="mockup-step-card {c1_active}">
                <div class="mockup-step-left">
                    <div class="mockup-step-num">1</div>
                    <div>
                        <div class="mockup-step-small">PASO 1 DE 3</div>
                        <div class="mockup-step-big">Contanos cómo trabajan</div>
                    </div>
                </div>
                <div class="mockup-step-arrow">›</div>
            </div>
            <div class="mockup-connector"></div>
            <div class="mockup-step-card {c2_active}">
                <div class="mockup-step-left">
                    <div class="mockup-step-num">2</div>
                    <div>
                        <div class="mockup-step-small">PASO 2 DE 3</div>
                        <div class="mockup-step-big">Mirá tu semáforo y plan</div>
                    </div>
                </div>
                <div class="mockup-step-arrow">›</div>
            </div>
            <div class="mockup-connector"></div>
            <div class="mockup-step-card {c3_active}">
                <div class="mockup-step-left">
                    <div class="mockup-step-num">3</div>
                    <div>
                        <div class="mockup-step-small">PASO 3 DE 3</div>
                        <div class="mockup-step-big">Llevate tus guías listas</div>
                    </div>
                </div>
                <div class="mockup-step-arrow">›</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_topic_pills() -> None:
    """Renderiza la tira de 5 tarjetas blancas/menta para los temas (Tu rubro, Compus y celus, etc.)."""
    progreso = min(max(int(st.session_state.get("progreso", 5)), 0), 100)
    html_cards = ['<div class="mockup-topics-bar">']
    actual_marcado = False

    for est in ESTACIONES_CHARLA:
        if progreso >= est["umbral"]:
            cls = "mockup-topic-card done"
            sub = '<span class="mockup-topic-now">✓ Listo:</span>'
        elif not actual_marcado:
            cls = "mockup-topic-card current"
            sub = '<span class="mockup-topic-now">Ahora:</span>'
            actual_marcado = True
        else:
            cls = "mockup-topic-card"
            sub = ""

        html_cards.append(
            f'<div class="{cls}">'
            f'<span class="mockup-topic-icon">{est["icono"]}</span>'
            f'<div class="mockup-topic-meta">'
            f"{sub}"
            f'<span class="mockup-topic-name">{est["nombre"]}</span>'
            f"</div>"
            f"</div>"
        )
    html_cards.append("</div>")
    st.markdown("".join(html_cards), unsafe_allow_html=True)