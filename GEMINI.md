# Project Overview

This project, "SSO Consultant Enhanced," is a web-based application that provides expert advice on Peruvian Occupational Health and Safety (OHS) regulations. It combines a rule-based expert system with a data-driven predictive analytics module to offer comprehensive and actionable insights. The application is built with a Flask backend and a single-page web interface.

## Key Technologies

*   **Backend:** Flask (Python)
*   **Frontend:** HTML, CSS, JavaScript (embedded in the Flask application)
*   **AI/ML:** OpenAI GPT-3.5-turbo, scikit-learn, xgboost
*   **Data Analysis:** pandas, numpy
*   **Data Visualization:** plotly, matplotlib

## Architecture

The application is divided into two main components:

1.  **SSO Consultant:** A Flask application that serves the web interface and handles user queries. It uses the OpenAI API to provide expert advice on OHS regulations.
2.  **Accident Analytics:** A data analysis module that uses machine learning to predict accident risks and provide data-driven recommendations. It reads data from an Excel file and uses scikit-learn and xgboost to train predictive models.

# Building and Running

To build and run the project, follow these steps:

1.  **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

2.  **Set up environment variables:**

    Create a `.env` file in the root directory of the project and add the following line:

    ```
    OPENAI_API_KEY=<your_openai_api_key>
    ```

3.  **Run the application:**

    ```bash
    python sso_enhanced.py
    ```

The application will be available at `http://localhost:8085`.

# Development Conventions

*   **Coding Style:** The code follows the PEP 8 style guide.
*   **Testing:** There are no automated tests in the project.
*   **Contribution Guidelines:** There are no contribution guidelines in the project.

# Roadmap

## 1. Mapeo y Validación de Campos
- Revisar y documentar todos los campos del Excel.
- Validar la calidad y consistencia de los datos (fechas, texto, numéricos, categorías).
- Estandarizar nombres y formatos para facilitar el análisis automático.

## 2. Procesamiento y Enriquecimiento de Datos
- Mejorar la limpieza y normalización de texto (por ejemplo, “Descripción del Accidente”, “Forma de Accidente”).
- Implementar extracción de palabras clave y categorización automática para descripciones largas.
- Codificar todos los campos relevantes como variables para modelos predictivos y análisis estadístico.

## 3. Análisis Estadístico y Predictivo
- Ampliar el análisis de patrones por:
  - Área, sector, puesto, turno, antigüedad, experiencia, tipo de trabajador, etc.
  - Forma y causa del accidente, actividad/tarea, agente causante, parte del cuerpo, naturaleza de lesión, consecuencia.
- Entrenar modelos predictivos para:
  - Probabilidad de accidente por perfil de trabajador, área, turno, etc.
  - Severidad esperada y consecuencias.
  - Detección de factores de riesgo emergentes.

## 4. Generación de Insights y Recomendaciones
- Crear funciones que generen resúmenes ejecutivos y recomendaciones automáticas para cada consulta.
- Incluir alertas sobre tendencias, áreas críticas, actividades peligrosas y medidas preventivas.
- Generar reportes personalizados según filtros (por área, fecha, tipo de accidente, etc.).

## 5. Integración con LLM (OpenAI)
- Definir prompts y plantillas para que el LLM explique, resuma y contextualice los resultados del análisis.
- Permitir consultas en lenguaje natural sobre cualquier campo o combinación de campos del Excel.
- Enriquecer las respuestas con normativa, mejores prácticas y sugerencias personalizadas.

## 6. Interfaz de Usuario y Experiencia
- Permitir al usuario consultar por cualquier campo o combinación (ej: “¿Qué accidentes ocurrieron en el turno noche en almacén?”).
- Mostrar visualizaciones y tablas dinámicas con los resultados.
- Ofrecer recomendaciones accionables y explicaciones claras, generadas por el LLM.

## 7. Ciclo de Mejora Continua
- Recopilar feedback de usuarios sobre la utilidad y claridad de las respuestas.
- Ajustar los modelos y prompts del LLM según nuevas necesidades o cambios en los datos.
- Automatizar la actualización y reentrenamiento de modelos con nuevos datos.