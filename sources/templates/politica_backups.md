# Política de Copias de Seguridad (Backups)

**Versión:** 1.0 | **Aplica a:** [Nombre de la Empresa] | **Nivel de Madurez:** Básico / Gestionado

## 1. Objetivo

Garantizar la disponibilidad e integridad de la información crítica de la empresa, asegurando que los datos puedan ser recuperados en caso de pérdida, robo, error humano o ataque cibernético (como Ransomware).

## 2. Alcance

Aplica a todos los dispositivos de la empresa, servidores, cuentas en la nube y bases de datos que contengan información de clientes, facturación o procesos operativos.

## 3. Directrices

### 3.1. Regla de Oro (3-2-1)

Para los datos críticos, se debe aplicar la regla:

- **3** copias de los datos.
- **2** tipos de soporte diferentes (Ej: Nube y Disco Externo).
- **1** copia fuera de la oficina (Off-site).

### 3.2. Frecuencia y Automatización

- **Backups Automáticos:** Se deben configurar copias automáticas diarias para los documentos críticos (Ej: Google Drive, OneDrive, Dropbox).
- **Backups Locales:** Si se usan discos externos, la copia debe ser semanal y el disco debe desconectarse tras la copia (para evitar infecciones de Ransomware).

### 3.3. Seguridad de los Backups

- **Cifrado:** Las copias de seguridad deben estar cifradas (protegidas con contraseña).
- **Acceso:** Solo el personal autorizado (Dirección o Responsable de TI) debe tener acceso a las copias de seguridad.

### 3.4. Pruebas de Recuperación

- **Prueba obligatoria:** Cada 3 meses se debe realizar una prueba de restauración de un archivo al azar para verificar que el backup funciona. Un backup que no se prueba, no se considera un backup válido.

## 4. Responsabilidades

- **Responsable de TI:** Configurar los backups automáticos y realizar las pruebas de restauración.
- **Empleados:** Guardar los archivos de trabajo exclusivamente en las carpetas compartidas de la nube (no en el escritorio local).

## 5. Referencias Normativas

- **CIS Control 11.2:** Realizar backups automáticos.
- **CIS Control 11.1:** Probar la restauración de backups.
- **NIST CSF 2.0:** PR.DS-11 (Protección de datos) y RC.RP (Plan de recuperación).
- **CISA Cyber Essentials:** Elemento "Sus Datos".
