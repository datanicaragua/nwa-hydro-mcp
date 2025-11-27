---
date: 2025-11-26
title: "Limpieza de Memoria y Reinicio del Proyecto NWA Hydro MCP"
author: Gustavo Ernesto Martínez Cárdenas
ai assistant: Gemini 3.0 Pro
---

### 1. Evaluación Crítica del Plan Estratégico v1.0 (Análisis de Riesgos)

He revisado el PDF "Plan Estratégico y de Ejecución" con una lente de arquitectura de software y riesgos de implementación. Estas son mis alertas rojas que **no** mencioné antes:

- **Riesgo Crítico en la "Herramienta Bronce" (Fusión de Datos):**

  - El plan asume que integrar Open-Meteo (API) y CSV Local (Fallback) es trivial. **No lo es.**
  - _El Problema:_ La API devuelve JSON con una estructura específica de series de tiempo. El CSV tiene otra. Si la Herramienta Bronce no normaliza ambos outputs en un **Esquema Pydantic Unificado** estricto, la Herramienta Plata (Hargreaves) fallará o tendrá que escribir lógica condicional ("si viene de CSV haz X, si viene de API haz Y"). Eso es código sucio.
  - _Mi Aporte:_ Debemos diseñar primero el **Data Contract (Contrato de Datos)**. La herramienta no es solo "fetch", es "fetch and normalize".

- **La Trampa de Gradio (Track 2):**

  - El plan dice "Día 11-12: Integrar Gradio".
  - _El Problema:_ Gradio funciona bien, pero conectar un Frontend Web a un servidor MCP (que corre en stdio/local) requiere un cliente MCP intermedio dentro de la app de Python. No es una conexión directa habitual.
  - _Mi Aporte:_ Necesitamos decidir si la App Gradio importará las funciones de Python directamente (monolito lógico) o si realmente actuará como un Cliente MCP (arquitectura distribuida). Para el Hackathon, sugiero que Gradio importe el módulo `src.nwa_hydro` directamente para evitar latencia, aunque viole purismos de MCP.

- **Complejidad Oculta de Hargreaves:**
  - El plan elige Hargreaves por ser "stateless". Correcto.
  - _El Problema:_ Hargreaves requiere **Radiación Extraterrestre (Ra)**, que depende de la latitud y el día del año. La librería `pyeto` lo calcula, pero necesitamos asegurar que la latitud pase correctamente desde la Herramienta Bronce. Si el usuario pide datos de una estación CSV sin metadatos de latitud, el modelo colapsa.

---

### 2. Estrategia Metodológica: "Clean Slate Protocol"

Para limpiar la mente del proyecto y alinear las incongruencias (código viejo vs. Plan PDF), sugiero **SÍ iniciar un nuevo chat**, pero no con las manos vacías.

El workflow debe ser el siguiente:

#### Paso 1: Consolidación de Artefactos (En este chat actual)

Antes de irnos, debemos generar un único documento maestro que contenga la "Verdad". No podemos confiar en que recuerdes subir el PDF en el nuevo chat y que la IA lo interprete igual.

- **Acción:** Redactar la **Nota Técnica NT_000 (Project Charter)** corregida. Esta nota debe fusionar la estructura de carpetas que ya aprobamos con la lógica de negocio del PDF (Hargreaves + Fusión de Datos).

#### Paso 2: El "Meta-Prompt" de Inyección (El Puente)

Diseñaremos un prompt masivo que inyectarás al inicio del nuevo chat. Este prompt definirá:

1.  **Rol:** Arquitecto Crítico (no asistente pasivo).
2.  **Contexto:** El contenido íntegro de la NT_000.
3.  **Restricciones:** Stack tecnológico y reglas de Clean Architecture.

#### Paso 3: Ejecución en Nuevo Entorno (Nuevo Chat)

En el nuevo chat, la IA ya no tendrá "alucinaciones" de códigos anteriores. Solo conocerá la NT_000. Desde ahí, generaremos el código del `server.py` desde cero, esta vez alineado perfectamente al plan.

---

### 3. El Meta-Prompt Maestro (Propuesta)

Copia y guarda este bloque. Será tu primera interacción en el nuevo chat.

---

**INSTRUCCIÓN DE SISTEMA: REINICIO DE PROYECTO NWA-HYDRO-MCP**

Actúa como **Arquitecto de Software Senior y Lead Developer** para la startup NWA Clima Centro.
Estamos participando en el Hackathon "MCP 1st Birthday".
Hemos realizado una fase de pre-análisis y hemos definido una Estrategia y Arquitectura sólidas. Tu objetivo es ayudarme a implementar el código basándote ESTRICTAMENTE en la documentación que te proveeré a continuación.

**TUS REGLAS DE COMPORTAMIENTO:**

1.  **Pensamiento Crítico:** No asumas que mis instrucciones son perfectas. Si ves un riesgo técnico (especialmente en tipos de datos, integración de APIs o estructura de archivos), señálalo antes de generar código.
2.  **Clean Architecture:** El código debe ser modular. Separa la lógica de negocio (cálculo de Hargreaves) de la capa de transporte (Servidor FastMCP).
3.  **Single Source of Truth:** La Nota Técnica `NT_000` adjunta es la ley. Si te pido algo que contradice la nota, adviérteme.

**CONTEXTO DEL PROYECTO (NOTA TÉCNICA NT_000):**

> **Nombre:** NWA Hydro-Compute MCP
> **Misión:** Crear un motor de cómputo hidrológico (no un bot del clima) que exponga herramientas científicas a agentes de IA.
> **Diferenciador:** Fusión de datos (API Open-Meteo + CSV Local) y Cómputo de Evapotranspiración (Modelo Hargreaves).
> **Stack:** Python 3.10+, `mcp[fastmcp]`, `pandas`, `xarray`, `pyeto` (para FAO-56), `pydantic`.
>
> **ARQUITECTURA DE HERRAMIENTAS (SCOPE):**
>
> 1. **Herramienta Bronce (`fetch_climate_data`):**
>
>    - Input: Latitud, Longitud, Rango de Fechas.
>    - Lógica: Intenta buscar en Open-Meteo (ERA5). Si falla o se solicita, busca en `data/local_station.csv`.
>    - Output: Un DataFrame estandarizado (Pydantic Model) con Tmin, Tmax, Tmean, Pcp.
>
> 2. **Herramienta Plata (`calculate_eto_hargreaves`):**
>    - Input: El objeto de datos estandarizado de la herramienta anterior + Latitud.
>    - Lógica: Usa `pyeto` para calcular la Radiación Extraterrestre (Ra) y luego la ETo diaria.
>    - Output: Serie temporal de demanda hídrica.

**ESTADO ACTUAL DEL REPO:**
El repo existe en `datanicaragua/nwa-hydro-mcp` (Privado).
Tenemos la estructura de carpetas creada (`src/`, `docs/`, `tests/`, `.ai/`).
Tenemos `pyproject.toml` configurado.

**TU PRIMERA TAREA:**
Analiza este contexto. Confirma que entiendes la diferencia entre una herramienta de "fetch" y una de "cómputo". Luego, propón el contenido actualizado para `pyproject.toml` incluyendo las librerías científicas (`pyeto`, `httpx`) y genera el código para el modelo de datos Pydantic (`src/nwa_hydro/schemas.py`) que servirá de contrato entre las herramientas.
