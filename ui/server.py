import sys
import os
import re
import json
from pathlib import Path
from typing import List, Dict, Any

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from langchain_core.messages import HumanMessage, AIMessage

from src.config import SOURCES_DIR
from src.rag.pipeline import obtener_cadenas

app = FastAPI(title="Cuidá tu Negocio · API PYME")

UI_DIR = Path(__file__).resolve().parent
WEB_DIR = UI_DIR / "web"

# Intentar conectar con el pipeline real de Ollama/ChromaDB
MODO_ONLINE = False
cadena_entrevista_real = None
generar_informe_real = None

try:
    cadena_entrevista_real, generar_informe_real = obtener_cadenas()
    MODO_ONLINE = True
except Exception as e:
    print(f"Aviso: Iniciando en modo simulación UI ({e})")


PREGUNTAS_SIMULADAS = [
    {
        "pregunta": "¿Qué dispositivos usan para trabajar?",
        "intro": "Podés elegir todas las opciones que correspondan.",
        "progreso": 40,
    },
    {
        "pregunta": "¿Cómo cuidan las contraseñas del negocio?",
        "intro": "Podés elegir todas las opciones que correspondan.",
        "progreso": 60,
    },
    {
        "pregunta": "¿Dónde guardan copias de los archivos importantes?",
        "intro": "Por ejemplo: planillas de clientes, ventas, proveedores o facturación. Podés elegir varias opciones.",
        "progreso": 80,
    },
    {
        "pregunta": "Si reciben un mensaje sospechoso o falla una computadora, ¿qué hacen?",
        "intro": "Elegí la opción que mejor describa cómo actúan hoy.",
        "progreso": 100,
    },
]

INFORME_DEMO = """# 🛡️ Tu Plan Simple para Cuidar el Negocio

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
   - **Qué hacer:** En el **Paso 3** de este asistente, descargá la *Guía 3: Qué Hacer ante una Estafa* y mandala al grupo de WhatsApp de tu equipo.

## 5. Tu guía para los próximos días
- **🟢 Esta semana (30 minutos):** Activar la verificación en 2 pasos en el correo y WhatsApp del negocio.
- **🔵 Este mes:** Dejar andando la copia automática en la nube de los archivos importantes.
- **🟡 El mes que viene:** Charlar 10 minutos con tus empleados sobre cómo reconocer mensajes falsos de bancos o proveedores.
"""


class ChatRequest(BaseModel):
    message: str
    history: List[Dict[str, str]] = []
    use_ollama: bool = False


class ReportRequest(BaseModel):
    history: List[Dict[str, str]] = []
    use_ollama: bool = False


def limpiar_progreso(texto: str) -> str:
    return re.sub(r"\[PROGRESO:\s*\d+\]", "", texto).strip()


@app.post("/api/chat")
def api_chat(req: ChatRequest):
    respuestas_usuario = sum(1 for m in req.history if m.get("role") == "user")

    if req.use_ollama and MODO_ONLINE and cadena_entrevista_real is not None:
        try:
            lc_history = []
            for m in req.history:
                if m.get("role") == "user":
                    lc_history.append(HumanMessage(content=m.get("content", "")))
                else:
                    lc_history.append(AIMessage(content=m.get("content", "")))

            raw = cadena_entrevista_real.invoke(
                {"question": req.message, "chat_history": lc_history}
            )
            match = re.search(r"\[PROGRESO:\s*(\d+)\]", raw)
            incremento = int(match.group(1)) if match else 20
            texto_limpio = limpiar_progreso(raw)
            return {
                "intro": "Gracias por contarme. Seguimos con el próximo punto:",
                "pregunta": texto_limpio,
                "incremento": incremento,
                "source": "ollama",
            }
        except Exception as e:
            print(f"Fallback a modo guiado por error en Ollama: {e}")

    idx = min(respuestas_usuario, len(PREGUNTAS_SIMULADAS) - 1)
    step_data = PREGUNTAS_SIMULADAS[idx]
    return {
        "intro": step_data["intro"],
        "pregunta": step_data["pregunta"],
        "progreso_sugerido": step_data["progreso"],
        "source": "guided",
    }


@app.post("/api/report")
def api_report(req: ReportRequest):
    if req.use_ollama and MODO_ONLINE and generar_informe_real is not None:
        try:
            lc_history = []
            for m in req.history:
                if m.get("role") == "user":
                    lc_history.append(HumanMessage(content=m.get("content", "")))
                else:
                    lc_history.append(AIMessage(content=m.get("content", "")))
            informe = generar_informe_real(lc_history)
            return {"report": informe, "source": "ollama"}
        except Exception as e:
            print(f"Fallback reporte guiado: {e}")

    return {"report": INFORME_DEMO, "source": "guided"}


@app.get("/api/resources")
def api_resources(empresa: str = ""):
    templates_dir = SOURCES_DIR / "templates"
    plantillas = []
    meta_info = {
        "politica_contrasenas": {
            "titulo": "Guía 1: Cuidado de Claves",
            "desc": "Reglas simples para que nadie use claves fáciles ni las comparta por chat.",
            "color": "green",
            "icono": "🔑",
        },
        "politica_backups": {
            "titulo": "Guía 2: Copias de Archivos",
            "desc": "Cómo guardar las planillas y facturación para no perder nada si falla una PC.",
            "color": "blue",
            "icono": "☁️",
        },
        "plan_respuesta_incidentes": {
            "titulo": "Guía 3: Qué Hacer ante Estafas",
            "desc": "Los 5 pasos de emergencia si entra un virus o un mensaje falso.",
            "color": "amber",
            "icono": "🛟",
        },
    }

    if templates_dir.exists():
        for p in sorted(templates_dir.glob("*.md")):
            content = p.read_text(encoding="utf-8")
            if empresa.strip():
                content = content.replace("[Nombre de la Empresa]", empresa.strip())
            info = meta_info.get(
                p.stem,
                {
                    "titulo": p.stem.replace("_", " ").title(),
                    "desc": "Plantilla lista para usar",
                    "color": "blue",
                    "icono": "📄",
                },
            )
            plantillas.append(
                {
                    "id": p.stem,
                    "filename": p.name,
                    "titulo": info["titulo"],
                    "desc": info["desc"],
                    "color": info["color"],
                    "icono": info["icono"],
                    "content": content,
                }
            )

    glosario_path = SOURCES_DIR / "tools" / "glosario.md"
    tools_path = SOURCES_DIR / "tools" / "catalogo_herramientas_open_source.md"

    return {
        "templates": plantillas,
        "glosario": glosario_path.read_text(encoding="utf-8") if glosario_path.exists() else "",
        "herramientas": tools_path.read_text(encoding="utf-8") if tools_path.exists() else "",
    }


@app.get("/")
def serve_index():
    return FileResponse(WEB_DIR / "index.html")


app.mount("/static", StaticFiles(directory=str(WEB_DIR)), name="static")
