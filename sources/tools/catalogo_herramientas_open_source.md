# Catálogo de Herramientas Open Source y Gratuitas para PYMES

## 1. Introducción

Este catálogo reúne herramientas de código abierto o de uso gratuito que permiten a las PYMES implementar controles de seguridad sin incurrir en costos de licenciamiento. Han sido seleccionadas por su madurez, comunidad de soporte y facilidad de implementación en entornos con recursos limitados.

---

## 2. Función: Gobernar (Gobernanza y Documentación)

Herramientas para organizar políticas, procedimientos y planes de acción.

- **Trello / Notion**
  - **Tipo:** Gestión de proyectos y documentación.
  - **Costo:** Gratuito (plan básico).
  - **Uso para la PYME:** Organizar las políticas de seguridad, crear tableros de seguimiento para las tareas de mejora y documentar los procedimientos internos.
- **Google Docs / Sheets**
  - **Tipo:** Documentación y hojas de cálculo.
  - **Costo:** Gratuito.
  - **Uso para la PYME:** Crear y compartir plantillas de políticas, registrar inventarios (ej. lista de equipos) y llevar el control de incidentes.

---

## 3. Función: Identificar (Inventario y Vulnerabilidades)

Herramientas para saber qué activos tiene la empresa y cuáles son sus puntos débiles.

- **OpenVAS / Greenbone**
  - **Tipo:** Escáner de vulnerabilidades.
  - **Costo:** Gratuito (Open Source).
  - **Uso para la PYME:** Detectar fallas de seguridad en sistemas y redes (ej. contraseñas débiles, software desactualizado) antes de que los atacantes lo hagan.
- **CMDB.io**
  - **Tipo:** Gestión de activos (Configuration Management Database).
  - **Costo:** Gratuito (básico).
  - **Uso para la PYME:** Mantener un inventario ordenado del hardware y software de la empresa.
- **OCS Inventory**
  - **Tipo:** Inventario de activos TI.
  - **Costo:** Gratuito.
  - **Uso para la PYME:** Descubrir y gestionar automáticamente todos los dispositivos conectados a la red de la empresa.

---

## 4. Función: Proteger (Defensas Básicas)

Herramientas para blindar el acceso y proteger la información.

- **Bitwarden**
  - **Tipo:** Gestor de contraseñas.
  - **Costo:** Gratuito (versión personal/equipos pequeños).
  - **Uso para la PYME:** Almacenar contraseñas seguras, generar claves aleatorias y compartir accesos de forma cifrada entre empleados autorizados.
- **VeraCrypt**
  - **Tipo:** Cifrado de discos.
  - **Costo:** Gratuito.
  - **Uso para la PYME:** Cifrar datos en reposo (discos rígidos, pendrives) para que, si un equipo es robado, la información sea ilegible.
- **pfSense**
  - **Tipo:** Firewall / Router.
  - **Costo:** Gratuito.
  - **Uso para la PYME:** Actuar como el "portero" de la red, bloqueando tráfico no deseado y gestionando el acceso a internet de forma segura.
- **ClamAV**
  - **Tipo:** Antivirus.
  - **Costo:** Gratuito.
  - **Uso para la PYME:** Proteger servidores y estaciones de trabajo contra malware y virus.

---

## 5. Función: Detectar (Monitoreo)

Herramientas para enterarse a tiempo si algo extraño está pasando en la red.

- **Wazuh**
  - **Tipo:** SIEM / XDR (Monitoreo de seguridad).
  - **Costo:** Gratuito (Open Source).
  - **Uso para la PYME:** Centralizar los registros (logs) de los equipos, detectar intrusiones y recibir alertas tempranas ante comportamientos sospechosos.
- **Snort**
  - **Tipo:** IDS/IPS (Sistema de Detección/Prevención de Intrusiones).
  - **Costo:** Gratuito.
  - **Uso para la PYME:** Analizar el tráfico de red en tiempo real para identificar y bloquear ataques comunes.
- **Zeek (antes Bro)**
  - **Tipo:** Análisis de tráfico de red.
  - **Costo:** Gratuito.
  - **Uso para la PYME:** Monitorear el tráfico de la red y detectar anomalías (ej. un equipo enviando datos a un servidor desconocido).

---

## 6. Función: Responder (Gestión de Incidentes)

Herramientas para organizar la reacción ante un ataque.

- **TheHive**
  - **Tipo:** Plataforma de respuesta a incidentes.
  - **Costo:** Gratuito (Open Source).
  - **Uso para la PYME:** Organizar casos de incidentes, asignar tareas al equipo y documentar los pasos seguidos para resolver un ataque.
- **MISP**
  - **Tipo:** Sharing de inteligencia de amenazas.
  - **Costo:** Gratuito.
  - **Uso para la PYME:** Intercambiar información sobre amenazas (ej. listas de correos de phishing) con otras organizaciones o comunidades de seguridad.

---

## 7. Función: Recuperar (Continuidad)

Herramientas para no perder la información y poder volver a operar.

- **Duplicati**
  - **Tipo:** Backups.
  - **Costo:** Gratuito.
  - **Uso para la PYME:** Realizar copias de seguridad cifradas y automatizadas a la nube o a un disco local.
- **Rclone**
  - **Tipo:** Sincronización de backups.
  - **Costo:** Gratuito.
  - **Uso para la PYME:** Sincronizar y replicar los backups en múltiples destinos (ej. Google Drive y un disco externo) para cumplir con la regla 3-2-1.

---

## 8. Nota para el Asistente IA

Al recomendar una herramienta, considera el nivel de madurez de la PYME. Para el **Nivel 1 (Básico)**, prioriza herramientas de interfaz gráfica y fácil configuración (ej. Bitwarden, Duplicati). Para niveles **3 y 4 (Definido/Optimizado)**, puedes sugerir herramientas que requieran un poco más de conocimiento técnico (ej. Wazuh, pfSense).
