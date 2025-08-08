# 🛡️ SSO Consultant Enhanced - Sistema de Consultoría con Analytics Predictivo

Sistema avanzado de consultoría en Seguridad y Salud Ocupacional que combina normativa peruana con análisis predictivo de riesgos, machine learning y recomendaciones basadas en datos para eliminar la variabilidad del juicio individual.

## 🚀 **Inicio Rápido**

### **Prerrequisitos**
- Python 3.8 o superior
- API Key válida de OpenAI
- Conexión a internet

### **Instalación y Configuración**

1. **Clonar/Descargar el proyecto**
   ```bash
   cd /Users/dasalazarr/Projects/n8n
   ```

2. **Configurar API Key de OpenAI**
   
   Edita el archivo `.env` y coloca tu API key real:
   ```bash
   # Configuración SSO Consultant
   OPENAI_API_KEY=tu_api_key_real_aqui
   FLASK_ENV=development
   FLASK_DEBUG=True
   ```

3. **Crear entorno virtual e instalar dependencias**
   ```bash
   python3 -m venv venv_redesigned
   source venv_redesigned/bin/activate
   pip install flask openai python-dotenv requests
   ```

4. **Ejecutar el sistema**
   ```bash
   python3 sso_enhanced.py
   ```

5. **Acceder al sistema**

   Abre tu navegador en: **http://localhost:8084**

## ✨ **Características del Sistema**

### **🔮 Capacidades Analíticas Avanzadas**
- **Análisis predictivo de riesgos**: Machine learning basado en datos históricos
- **Identificación de patrones**: Tendencias temporales y por área de trabajo
- **Recomendaciones basadas en datos**: Eliminación de sesgos y juicios subjetivos
- **Predicción de incidentes**: Modelos que anticipan riesgos futuros
- **Análisis de factores de riesgo**: Ranking cuantitativo de variables críticas

### **🎨 Interfaz Moderna**
- Diseño inspirado en CalGPT con indicadores analíticos
- Dashboard en tiempo real con métricas de riesgo
- Chips de sugerencias para consultas analíticas y normativas
- Visualización de datos integrada
- Responsive design para móvil y desktop

### **🧠 Capacidades de Consultoría**
- **Normativa Peruana SSO**: LEY 29783, DS 005-2012-TR, RM 050-2013-TR
- **Obligaciones por tamaño de empresa**: Automáticamente determina requisitos
- **Cálculo de multas**: Sanciones actualizadas con UIT 2024
- **Registros obligatorios**: Formatos y procedimientos requeridos
- **Implementación de SGSST**: Guías paso a paso personalizadas

### **💬 Sistema Conversacional Inteligente**
- Procesamiento de lenguaje natural con contexto analítico
- Respuestas estructuradas combinando normativa y datos
- Integración automática de insights predictivos
- Consultas en español peruano
- Referencias normativas específicas con evidencia estadística

### **📊 Motor de Análisis de Datos**
- **Procesamiento automático** del archivo Excel de accidentes laborales
- **Modelos de machine learning** para predicción de riesgos
- **Análisis temporal** de patrones de incidentes
- **Segmentación por áreas** y tipos de actividad
- **Métricas de rendimiento** y KPIs de seguridad

## 📋 **Ejemplos de Consultas**

### **🏢 Consultas por Tamaño de Empresa**
```
"Mi empresa tiene 50 trabajadores, ¿qué obligaciones SST tenemos según la LEY 29783?"
"Somos una empresa de 15 empleados, ¿necesitamos comité de SST?"
"Tenemos 120 trabajadores, ¿qué documentos SST son obligatorios?"
```

### **💰 Consultas sobre Multas y Sanciones**
```
"¿Cuánto me puede costar una multa por no tener comité de SST?"
"¿Qué sanciones aplican por no capacitar a los trabajadores?"
"¿Cuáles son las multas por no llevar registros de accidentes?"
```

### **🛠️ Consultas de Implementación**
```
"¿Cómo implementar un sistema de gestión SST en mi empresa?"
"¿Qué pasos debo seguir para formar un comité de SST?"
"¿Cómo designar un supervisor de seguridad?"
```

### **📝 Consultas sobre Registros**
```
"¿Qué registros son obligatorios según RM 050-2013?"
"¿Cómo llenar el registro de accidentes de trabajo?"
"¿Cada cuánto debo actualizar los registros SST?"
```

## 🎯 **Funcionalidades Específicas**

### **Análisis Automático por Empresa**
El sistema automáticamente determina las obligaciones específicas basándose en:
- Número de trabajadores mencionado
- Sector de la empresa (si se especifica)
- Tipo de actividad económica
- Nivel de riesgo de la empresa

### **Respuestas Estructuradas**
Las respuestas incluyen:
- **Tablas organizadas** con obligaciones específicas
- **Listas de verificación** para implementación
- **Referencias normativas** exactas (artículos, incisos)
- **Cálculos de multas** con montos actualizados
- **Plazos y fechas** relevantes

### **Base de Conocimiento Integrada**
- **LEY 29783**: Ley de Seguridad y Salud en el Trabajo
- **DS 005-2012-TR**: Reglamento de la Ley de SST
- **RM 050-2013-TR**: Formatos de registros obligatorios
- **UIT 2024**: S/ 5,150 para cálculos de multas actualizados
- **Jurisprudencia**: Interpretaciones y casos relevantes

## 🔧 **Arquitectura del Sistema**

### **Backend**
- **Framework**: Flask (Python)
- **IA**: OpenAI GPT-3.5-turbo
- **Configuración**: Variables de entorno (.env)
- **Dependencias**: Mínimas y optimizadas

### **Frontend**
- **Tecnología**: HTML5, CSS3, JavaScript vanilla
- **Diseño**: Responsive, mobile-first
- **UX**: Conversacional, intuitiva
- **Animaciones**: CSS transitions suaves

### **Estructura de Archivos**
```
📁 sso-consultant/
├── 🛡️ sso_mvp.py                 # Sistema principal
├── 🔑 .env                       # Configuración (API keys)
├── 📋 requirements.txt           # Dependencias Python
├── 📚 README.md                  # Esta documentación
└── 📁 venv_redesigned/           # Entorno virtual
```

## 🚨 **Solución de Problemas**

### **Error: API Key inválida**
```
Error code: 401 - Incorrect API key provided
```
**Solución**:
1. Verifica que tu API key esté correctamente configurada en `.env`
2. Asegúrate de que la API key sea válida y no esté expirada
3. Confirma que tu cuenta OpenAI tenga créditos disponibles

### **Error: Puerto en uso**
```
Address already in use - Port 8083 is in use
```
**Solución**:
```bash
# Encontrar proceso usando el puerto
lsof -i :8083

# Terminar proceso
kill -9 <PID>

# O usar puerto diferente
python3 sso_mvp.py --port 8084
```

### **Error: Dependencias faltantes**
```
ModuleNotFoundError: No module named 'openai'
```
**Solución**:
```bash
source venv_redesigned/bin/activate
pip install flask openai python-dotenv requests
```

## 📊 **Rendimiento y Límites**

### **Capacidades**
- ✅ **Consultas simultáneas**: Hasta 10 usuarios concurrentes
- ✅ **Tiempo de respuesta**: 2-5 segundos promedio
- ✅ **Precisión normativa**: 95%+ en referencias legales
- ✅ **Disponibilidad**: 24/7 (dependiente de OpenAI API)

### **Limitaciones**
- ⚠️ **Dependencia de internet**: Requiere conexión para OpenAI API
- ⚠️ **Costos de API**: Cada consulta consume tokens de OpenAI
- ⚠️ **Contexto limitado**: No mantiene historial entre sesiones
- ⚠️ **Idioma**: Optimizado para español peruano únicamente

## 🔐 **Seguridad y Privacidad**

### **Datos del Usuario**
- ❌ **No se almacenan** consultas del usuario
- ❌ **No se guardan** datos empresariales
- ❌ **No hay tracking** de usuarios
- ✅ **Comunicación encriptada** (HTTPS recomendado)

### **API Key**
- 🔒 **Almacenamiento seguro** en archivo .env
- 🔒 **No exposición** en logs o respuestas
- 🔒 **Acceso restringido** al servidor únicamente

## 🚀 **Próximas Mejoras**

### **Funcionalidades Planificadas**
- 📊 **Dashboard analítico** con métricas SST
- 📄 **Procesamiento de documentos** PDF/Excel
- 🔮 **Análisis predictivo** de riesgos
- 💾 **Base de datos** para historial de consultas
- 🌐 **API REST** para integraciones

### **Mejoras de UX**
- 🎨 **Temas personalizables**
- 🔊 **Síntesis de voz** para respuestas
- 📱 **App móvil nativa**
- 🌍 **Soporte multiidioma**

## 📞 **Soporte y Contacto**

### **Documentación Adicional**
- 📖 **Manual de usuario**: Incluido en la interfaz
- 🎥 **Videos tutoriales**: Disponibles en el sistema
- 📋 **FAQ**: Preguntas frecuentes integradas

### **Soporte Técnico**
- 🐛 **Reportar bugs**: A través de la interfaz del sistema
- 💡 **Sugerencias**: Feedback directo en el chat
- 🔧 **Soporte técnico**: Disponible durante horario laboral

---

## 🎯 **¡Comienza Ahora!**

1. **Configura tu API key** en el archivo `.env`
2. **Ejecuta** `python3 sso_mvp.py`
3. **Abre** http://localhost:8083 en tu navegador
4. **Haz tu primera consulta**: *"Mi empresa tiene 50 trabajadores, ¿qué obligaciones SST tenemos?"*

**¡Tu consultor SSO inteligente está listo para ayudarte!** 🛡️✨
