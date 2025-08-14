# Plan de Trabajo Adaptado: Cerebro SSO con DeepSeek API

## 🔄 Migración Completada: OpenAI → DeepSeek

### Cambios Realizados
- ✅ Cliente OpenAI actualizado con `base_url="https://api.deepseek.com"`
- ✅ Modelo cambiado de `gpt-4-turbo-preview` → `deepseek-chat`
- ✅ Variable de entorno: `OPENAI_API_KEY` → `DEEPSEEK_API_KEY`
- ✅ Compatibilidad total mantenida (DeepSeek es OpenAI-compatible)

### Configuración Requerida
```bash
# En tu archivo .env
DEEPSEEK_API_KEY=tu_deepseek_api_key_aqui
FLASK_ENV=development
FLASK_DEBUG=True
```

## 📋 Análisis del Estado Actual del Sistema

### ✅ Componentes Ya Implementados
1. **Analytics Engine** (`accident_analytics.py`)
   - ✅ Procesamiento de Excel con 754 registros
   - ✅ Modelos ML (RandomForest, GradientBoosting)
   - ✅ Cálculo de KPIs básicos
   - ✅ Análisis de patrones temporales

2. **Knowledge Base** (`knowledge_base.py`)
   - ✅ Sistema RAG básico implementado
   - ✅ Indexación de documentos normativos
   - ✅ 147 chunks procesados

3. **Web Interface**
   - ✅ Flask app con interfaz moderna
   - ✅ Chat interactivo
   - ✅ Chips de sugerencias dinámicas
   - ✅ Dashboard de estado analítico

4. **Core Features**
   - ✅ Procesamiento de consultas contextuales
   - ✅ Integración normativa + datos
   - ✅ Respuestas estructuradas en HTML

### 🔧 Gaps Identificados vs Plan Original

| Componente | Estado Actual | Gap vs Plan Original |
|------------|---------------|---------------------|
| **RAG System** | ✅ Básico | Falta metadatos por artículo, re-ranking |
| **ETL Pipeline** | ✅ Funcional | Falta normalización a parquet/SQLite |
| **KPI Engine** | ⚠️ Básico | Falta config/kpis.yaml, estados needs_input |
| **Query Templates** | ❌ Ausente | Falta sistema de plantillas parametrizadas |
| **JSON Contract** | ❌ Ausente | Respuestas en HTML, no JSON estándar |
| **Intent Router** | ⚠️ Básico | Falta clasificación LEGAL/DATA/MIXED |
| **Audit Logging** | ❌ Ausente | Sin trazabilidad estructurada |
| **API Endpoints** | ⚠️ Parcial | Falta /admin/reindex, estructura REST |

## 🎯 Plan de Trabajo Adaptado (3 Semanas)

### Semana 1: Fundaciones y Estandarización

#### H1: Estandarización del Contrato JSON (Prioridad Alta)
**Objetivo**: Implementar el contrato JSON único como interfaz estándar

**Tareas**:
1. Crear `models/response_contract.py` con esquema JSON
2. Modificar `SSOConsultantEnhanced.process_query()` para retornar JSON
3. Actualizar frontend para consumir JSON
4. Validador de esquema con Pydantic

**DoD**:
- ✅ Todas las respuestas cumplen el esquema JSON
- ✅ Frontend renderiza correctamente desde JSON
- ✅ Validación automática de estructura

```python
# Esquema objetivo
{
  "resumen": ["hallazgo 1", "hallazgo 2", "recomendación"],
  "kpis": [{"nombre":"IF","valor":null,"estado":"needs_input","formula":"AT_incap*1e6/HH","periodo":"2024"}],
  "tablas": [{"titulo":"Top formas 2024","columns":["forma","accidentes"],"rows":[["Caída a nivel",162]]}],
  "graficos": [{"tipo":"bar","titulo":"Accidentes por año","data_ref":"tabla:Accidentes por año"}],
  "citas_normativas": [{"documento":"DS 005-2012-TR","articulo":"33","paginas":"12-13"}],
  "citas_datos": [{"dataset":"accidentes","sql":"SELECT ...","filtros":{"anio":[2023,2024]}}],
  "suposiciones": ["faltan horas-hombre por año"],
  "siguientes_pasos": ["implementar 5S en área X","programar ergonomía Y"]
}
```

#### H2: Sistema de KPIs Configurable
**Objetivo**: Implementar `config/kpis.yaml` y motor de evaluación

**Tareas**:
1. Crear `config/kpis.yaml` con definiciones IF, IG, IA, Incidencia
2. Implementar `engines/kpi_engine.py`
3. Sistema de estados (calculado/needs_input)
4. Tests unitarios para fórmulas

**DoD**:
- ✅ KPIs se calculan desde configuración YAML
- ✅ Estado "needs_input" cuando faltan datos
- ✅ Fórmulas mostradas en respuesta
- ✅ Tests unitarios ≥90% cobertura

#### H3: ETL Mejorado y Normalización
**Objetivo**: Migrar de procesamiento en memoria a base de datos estructurada

**Tareas**:
1. Crear esquema SQLite en `data/sso_database.db`
2. ETL pipeline: Excel → SQLite con validación
3. Índices optimizados para consultas frecuentes
4. Script de migración de datos existentes

**DoD**:
- ✅ Datos normalizados en SQLite
- ✅ Performance ≤2s para consultas en 100k registros
- ✅ Validación de calidad de datos
- ✅ Backup/restore funcional

### Semana 2: Agentes y Orquestación

#### H4: Intent Router Agent
**Objetivo**: Clasificación inteligente de consultas

**Tareas**:
1. Implementar `agents/intent_router.py`
2. Clasificación: LEGAL, DATA, MIXED, ADMIN
3. Detección de KPIs solicitados
4. Dataset de prueba con 20 consultas etiquetadas

**DoD**:
- ✅ Accuracy ≥90% en dataset de prueba
- ✅ Detección automática de KPIs en consulta
- ✅ Fallback a LLM cuando reglas fallan

#### H5: Query Templates Engine
**Objetivo**: Sistema de consultas parametrizadas

**Tareas**:
1. Crear `engines/query_engine.py`
2. Implementar 8 plantillas base:
   - top_forma, top_parte_cuerpo, top_agente
   - tendencia_anual, costos_por_anio, descansos_por_anio
   - por_turno, por_area
3. Sistema de parámetros y filtros
4. Validación de resultados

**DoD**:
- ✅ Todas las plantillas responden en ≤2s
- ✅ Manejo explícito de "sin datos"
- ✅ SQL generado incluido en respuesta
- ✅ Filtros aplicados correctamente

#### H6: Orchestrator Agent
**Objetivo**: Coordinación inteligente del pipeline

**Tareas**:
1. Implementar `agents/orchestrator.py`
2. Flujos por tipo de intención
3. Manejo de errores y timeouts
4. Métricas de performance

**DoD**:
- ✅ 3 flujos (LEGAL/DATA/MIXED) funcionando
- ✅ Manejo robusto de errores
- ✅ Métricas P95 ≤ 6s para consultas mixtas
- ✅ Logging estructurado

### Semana 3: Refinamiento y Producción

#### H7: RAG Mejorado con Metadatos
**Objetivo**: Indexación por artículo y re-ranking

**Tareas**:
1. Mejorar `knowledge_base.py` con metadatos por artículo
2. Implementar re-ranking por relevancia normativa
3. Sistema de citas precisas
4. Optimización de retrieval

**DoD**:
- ✅ Retrieval@5 ≥ 0.85 en 20 preguntas legales
- ✅ Citas incluyen artículo y páginas exactas
- ✅ Re-ranking mejora relevancia
- ✅ Metadatos estructurados por documento

#### H8: API REST y Administración
**Objetivo**: Endpoints completos para administración

**Tareas**:
1. Reestructurar endpoints REST:
   - `POST /api/v1/ask` - Consulta principal
   - `GET /api/v1/kpis` - Lista KPIs disponibles
   - `POST /api/v1/admin/reindex` - Reindexación
   - `GET /api/v1/admin/status` - Estado del sistema
2. Documentación OpenAPI
3. Validación de entrada con Pydantic

**DoD**:
- ✅ API REST completa documentada
- ✅ Validación automática de requests
- ✅ Endpoints de administración seguros
- ✅ Documentación Swagger disponible

#### H9: Audit Logging y Observabilidad
**Objetivo**: Trazabilidad completa del sistema

**Tareas**:
1. Implementar `utils/audit_logger.py`
2. Logging estructurado JSON por consulta
3. Métricas de performance y uso
4. Dashboard de observabilidad básico

**DoD**:
- ✅ Cada consulta genera log completo
- ✅ Trazabilidad: intent → passages → SQL → respuesta
- ✅ Métricas de latencia y errores
- ✅ Rotación automática de logs

## 🏗️ Arquitectura Objetivo

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Client    │    │   API Gateway   │    │  Orchestrator   │
│   (React/Vue)   │◄──►│   (FastAPI)     │◄──►│     Agent       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                        │
                       ┌─────────────────────────────────┼─────────────────────────────────┐
                       │                                 ▼                                 │
              ┌─────────────────┐              ┌─────────────────┐              ┌─────────────────┐
              │ Intent Router   │              │ Legal Retriever │              │ Data Query      │
              │     Agent       │              │     Agent       │              │     Agent       │
              └─────────────────┘              └─────────────────┘              └─────────────────┘
                       │                                 │                                 │
                       ▼                                 ▼                                 ▼
              ┌─────────────────┐              ┌─────────────────┐              ┌─────────────────┐
              │   KPI Engine    │              │   FAISS Index   │              │   SQLite DB     │
              │     Agent       │              │   + Metadata    │              │   + Templates   │
              └─────────────────┘              └─────────────────┘              └─────────────────┘
                       │                                                                 │
                       └─────────────────────────────────────────────────────────────────┘
                                                        │
                                                        ▼
                                              ┌─────────────────┐
                                              │ Answer Builder  │
                                              │     Agent       │
                                              └─────────────────┘
                                                        │
                                                        ▼
                                              ┌─────────────────┐
                                              │ Audit Logger    │
                                              │     Agent       │
                                              └─────────────────┘
```

## 🚀 Configuración DeepSeek

### Variables de Entorno
```bash
# .env
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxx
FLASK_ENV=development
FLASK_DEBUG=True
DATABASE_URL=sqlite:///data/sso_database.db
LOG_LEVEL=INFO
```

### Ventajas de DeepSeek
1. **Costo**: ~90% más económico que GPT-4
2. **Performance**: Latencia comparable, buena calidad
3. **Compatibilidad**: Drop-in replacement para OpenAI
4. **Especialización**: Fuerte en tareas analíticas y técnicas

## 📊 Métricas de Éxito

### Performance
- P95 Latencia: LEGAL ≤ 3s, DATA ≤ 4s, MIXED ≤ 6s
- Throughput: ≥10 consultas/minuto
- Uptime: ≥99.5%

### Calidad
- Accuracy Intent Classification: ≥90%
- Retrieval@5 Legal: ≥85%
- KPI Calculation Accuracy: 100%
- JSON Schema Compliance: 100%

### Observabilidad
- Error Rate: ≤5%
- Log Coverage: 100% de consultas
- Audit Trail: Completo y reproducible

## 🔧 Comandos de Desarrollo

```bash
# Instalación
pip install -r requirements.txt

# Migración de datos
python scripts/migrate_to_sqlite.py

# Reindexación
python scripts/reindex_knowledge_base.py

# Tests
pytest tests/ -v --cov=src --cov-report=html

# Servidor de desarrollo
python sso_enhanced.py

# Validación de configuración
python scripts/validate_config.py
```

## 📝 Próximos Pasos Inmediatos

1. **Configurar DeepSeek API Key** en `.env`
2. **Implementar Response Contract** (H1)
3. **Crear config/kpis.yaml** (H2)
4. **Migrar a SQLite** (H3)
5. **Implementar Intent Router** (H4)

Este plan mantiene la funcionalidad existente mientras evoluciona hacia la arquitectura objetivo con agentes especializados y el contrato JSON estándar.
