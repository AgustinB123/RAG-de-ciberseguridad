import sys
import os
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from src.rag.pipeline import obtener_cadenas
from ui.components.progress_bar import render_wizard_header
from ui.components.chat import render_chat
from ui.components.report_panel import render_report_panel, render_resources_panel

# --- CONFIGURACIÓN DE PÁGINA (Sin barra lateral, centrada como Wizard) ---
st.set_page_config(
    page_title="Cuidá tu Negocio · Asistente PYME",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed",
)


def cargar_estilos() -> None:
    css_path = Path(__file__).resolve().parent / "styles" / "main.css"
    if css_path.exists():
        st.markdown(
            f"<style>{css_path.read_text(encoding='utf-8')}</style>",
            unsafe_allow_html=True,
        )


cargar_estilos()

# --- INICIALIZACIÓN DE ESTADO ---
MENSAJE_BIENVENIDA = (
    "¡Hola! 👋 Vamos a revisar cómo proteger tu negocio de estafas o pérdida de archivos, "
    "**sin palabras difíciles**.\n\n"
    "Para empezar, contame o elegí un botón abajo: **¿A qué se dedica tu negocio, cuántas personas "
    "trabajan con vos y qué usan todos los días (WhatsApp, Gmail, Excel, sistema de facturación)?**\n\n"
    "[PROGRESO: 5]"
)

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": MENSAJE_BIENVENIDA}]
if "progreso" not in st.session_state:
    st.session_state.progreso = 5
if "informe_final" not in st.session_state:
    st.session_state.informe_final = None
if "wizard_step" not in st.session_state:
    st.session_state.wizard_step = 1
if "modo_demo" not in st.session_state:
    st.session_state.modo_demo = False


# --- MOTORES DE SIMULACIÓN (DEMO AMIGABLE) ---
class _CadenaEntrevistaDemo:
    """Simulador con lenguaje cercano y cotidiano para probar el Wizard."""

    PREGUNTAS_ETAPAS = [
        (
            "¡Clarísimo! Ahora pasemos a las **computadoras y celulares**: "
            "¿Trabajan solo con equipos propios del local/oficina o los empleados también usan "
            "sus propios celulares y notebooks personales?\n\n[PROGRESO: 25]"
        ),
        (
            "Súper común en las PYMES. Ahora contame sobre las **contraseñas**: "
            "¿Cómo hacen para acordarse las claves del correo, redes o bancos? ¿Tienen activado "
            "el segundo código que llega al celular para poder entrar?\n\n[PROGRESO: 25]"
        ),
        (
            "Anotado. Pensemos ahora en los **archivos importantes** (planillas de clientes, "
            "facturación, pedidos): Si mañana se rompe o roban una computadora, "
            "¿tienen una copia guardada automáticamente en otro lugar?\n\n[PROGRESO: 25]"
        ),
        (
            "¡Excelente! Ya cubrimos todos los puntos clave de tu negocio. 🎉\n\n"
            "👉 **Tocá el botón verde '¡Listo! Ver mi Semáforo y Plan →' acá abajo para ver tu resultado.**\n\n[PROGRESO: 100]"
        ),
    ]

    def invoke(self, inputs: dict) -> str:
        historial = inputs.get("chat_history", [])
        respuestas_previas = sum(1 for m in historial if m.type == "human")
        idx = min(respuestas_previas, len(self.PREGUNTAS_ETAPAS) - 1)
        return self.PREGUNTAS_ETAPAS[idx]


def _generar_informe_demo(_chat_history) -> str:
    return """# 🛡️ Tu Plan Simple para Cuidar el Negocio

## 1. ¿Cómo están hoy? (Resumen en criollo)
Tu negocio está en un **Nivel Inicial**. Usan herramientas muy útiles todos los días (WhatsApp, correo, planillas), pero hoy tienen algunas puertas sin llave que un estafador o una falla técnica podrían aprovechar. **La buena noticia: podés resolver lo más importante esta misma semana y sin gastar plata.**

## 2. Lo que está bien y lo que corre peligro
- **✅ Lo que hacen bien:** Tienen digitalizado el trabajo diario y usan plataformas conocidas que ya traen opciones de protección listas para encender.
- **⚠️ El mayor peligro hoy:** Si alguien entra al correo o WhatsApp del negocio, o si una computadora deja de prender, podrían frenar las ventas o perder información de clientes y pagos.

## 3. Los 4 puntos a mejorar primero
- Las cuentas principales (correo, WhatsApp, redes) no tienen activado el segundo código en el celular.
- Las claves se anotan o se comparten entre varias personas sin control.
- No se hacen copias automáticas diarias de las planillas y facturación fuera de la oficina.
- No hay una regla clara para que el equipo sepa qué hacer si llega un comprobante o enlace falso.

## 4. ¿Cómo lo solucionamos gratis? (Paso a Paso)
1. **Poner doble llave a las cuentas (`Control CIS 6.3`):**
   - **Qué hacer:** Entrá a la configuración de Gmail, WhatsApp y redes y activá la **"Verificación en dos pasos"**.
   - **Programa gratis recomendado:** **Bitwarden** (guarda todas las claves bajo llave sin anotarlas en un cuaderno).
2. **Guardar copia automática de archivos (`Control CIS 11.2`):**
   - **Qué hacer:** Que la carpeta con facturación y clientes se sincronice sola todos los días en la nube, y una vez por semana en un disco externo desenchufado.
   - **Programa gratis recomendado:** **Google Drive / OneDrive** o **Duplicati**.
3. **Tener a mano la Hoja de Emergencia (`Control CIS 17.4`):**
   - **Qué hacer:** En el **Paso 3** de este asistente, descargá la *Hoja 3: Qué Hacer ante una Estafa* y mandala al grupo de WhatsApp de tu equipo.

## 5. Tu guía para los próximos días
- **🟢 Esta semana (30 minutos):** Activar la verificación en 2 pasos en el correo y WhatsApp del negocio.
- **🔵 Este mes:** Dejar andando la copia automática en la nube de los archivos importantes.
- **🟡 El mes que viene:** Charlar 10 minutos con tus empleados sobre cómo reconocer mensajes falsos de bancos o proveedores.
"""


# --- CARGA DE MODELOS ---
@st.cache_resource(show_spinner="Abriendo tu asistente...")
def cargar_modelos():
    return obtener_cadenas()


modo_online = True
try:
    cadena_entrevista_real, generar_informe_real = cargar_modelos()
except Exception:
    modo_online = False
    st.session_state.modo_demo = True
    cadena_entrevista_real, generar_informe_real = None, None

if st.session_state.modo_demo or not modo_online:
    cadena_activa = _CadenaEntrevistaDemo()
    generador_activo = _generar_informe_demo
else:
    cadena_activa = cadena_entrevista_real
    generador_activo = generar_informe_real


# --- ENCABEZADO COLORIDO + STEPPER WIZARD (PASOS 1 -> 2 -> 3) ---
render_wizard_header()

# --- CONTENIDO SEGÚN EL PASO ACTUAL DEL WIZARD ---
paso = int(st.session_state.get("wizard_step", 1))

if paso == 1:
    render_chat(cadena_entrevista=cadena_activa, generar_informe_fn=generador_activo)
elif paso == 2:
    render_report_panel(generar_informe_fn=generador_activo)
else:
    render_resources_panel()

# --- PIE DISCRETO DE MODO PRUEBA ---
st.write("")
with st.expander("⚙️ Opciones de prueba rápida (Modo Demo / IA Local)"):
    st.session_state.modo_demo = st.toggle(
        "Usar respuestas instantáneas de prueba (sin esperar a Ollama)",
        value=st.session_state.get("modo_demo", not modo_online),
        disabled=not modo_online,
    )