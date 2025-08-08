#!/bin/bash

# SSO Consultant Enhanced - Inicio con API Key Corregida
# ======================================================

echo "🛡️ Iniciando SSO Consultant Enhanced (API Key Corregida)"
echo "========================================================="

# Limpiar variables de entorno conflictivas
unset OPENAI_API_KEY

# Activar entorno virtual
echo "🔧 Activando entorno virtual..."
source venv_redesigned/bin/activate

# Verificar API key
echo "🔍 Verificando API key..."
python3 test_api_key.py

if [ $? -eq 0 ]; then
    echo ""
    echo "🚀 Iniciando SSO Consultant Enhanced..."
    echo "🌐 Servidor disponible en: http://localhost:8085"
    echo "🛑 Presiona Ctrl+C para detener"
    echo ""
    echo "🔮 CAPACIDADES ANALÍTICAS ACTIVAS:"
    echo "   • 754 registros de accidentes procesados"
    echo "   • Modelos de machine learning entrenados"
    echo "   • Predicción de riesgos en tiempo real"
    echo "   • Recomendaciones basadas en datos"
    echo ""
    echo "💬 Ejemplos de consultas analíticas:"
    echo "   • Basándote en nuestros datos, ¿qué áreas presentan mayor riesgo?"
    echo "   • ¿Cuál es la predicción de riesgo para este mes?"
    echo "   • ¿Qué medidas preventivas recomiendas según los patrones?"
    echo ""
    
    # Ejecutar aplicación
    python3 sso_enhanced.py
else
    echo "❌ Error con API key. No se puede iniciar el sistema."
    exit 1
fi
