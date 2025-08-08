#!/bin/bash

# SSO Consultant MVP - Script de Inicio
# =====================================

echo "🛡️ Iniciando SSO Consultant MVP"
echo "================================"

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 no está instalado"
    exit 1
fi

echo "✅ Python 3 encontrado"

# Crear entorno virtual si no existe
if [ ! -d "venv_redesigned" ]; then
    echo "📦 Creando entorno virtual..."
    python3 -m venv venv_redesigned
fi

# Activar entorno virtual
echo "🔧 Activando entorno virtual..."
source venv_redesigned/bin/activate

# Instalar dependencias
echo "📚 Instalando dependencias..."
pip install -r requirements.txt --quiet

# Verificar API Key
if [ ! -f ".env" ]; then
    echo "⚠️ Archivo .env no encontrado"
    echo "📝 Creando plantilla..."
    cat > .env << EOF
# Configuración SSO Consultant
OPENAI_API_KEY=tu_api_key_real_aqui
FLASK_ENV=development
FLASK_DEBUG=True
EOF
    echo "🔑 Por favor, edita el archivo .env con tu API key de OpenAI"
    echo "   Obtén tu API key en: https://platform.openai.com/account/api-keys"
    exit 1
fi

# Verificar que la API key no sea la plantilla
API_KEY=$(grep "OPENAI_API_KEY" .env | cut -d '=' -f2)
if [ "$API_KEY" = "tu_api_key_real_aqui" ]; then
    echo "⚠️ Por favor, configura tu API key real en el archivo .env"
    echo "   Obtén tu API key en: https://platform.openai.com/account/api-keys"
    exit 1
fi

echo "✅ Configuración completada"
echo ""
echo "🚀 Iniciando SSO Consultant Enhanced..."
echo "🌐 Servidor disponible en: http://localhost:8085"
echo "🛑 Presiona Ctrl+C para detener"
echo ""
echo "🔮 NUEVAS CAPACIDADES ANALÍTICAS:"
echo "   • Análisis predictivo de riesgos basado en datos históricos"
echo "   • Identificación de patrones en accidentes laborales"
echo "   • Recomendaciones específicas basadas en estadísticas"
echo "   • Eliminación de sesgos mediante análisis cuantitativo"
echo ""
echo "💬 Ejemplos de consultas analíticas:"
echo "   • Basándote en nuestros datos, ¿qué áreas presentan mayor riesgo?"
echo "   • ¿Cuál es la predicción de riesgo para este mes?"
echo "   • ¿Qué medidas preventivas recomiendas según los patrones?"
echo "   • Analiza las tendencias temporales de accidentes"
echo ""
echo "📋 Consultas tradicionales SSO:"
echo "   • Mi empresa tiene 50 trabajadores, ¿qué obligaciones SST tenemos?"
echo "   • ¿Qué multas aplican por no tener comité de SST?"
echo "   • ¿Cómo implementar un sistema de gestión SST?"
echo ""

# Limpiar variables de entorno conflictivas
unset OPENAI_API_KEY

# Ejecutar aplicación enhanced
python3 sso_enhanced.py
