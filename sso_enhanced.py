#!/usr/bin/env python3
"""
SSO Consultant Enhanced - Sistema Completo con Analytics Predictivo
Sistema de consultoría SSO con capacidades de análisis predictivo y reducción de riesgos
"""

import os
from flask import Flask, render_template_string, request, jsonify
from openai import OpenAI
from dotenv import load_dotenv
from accident_analytics import AccidentAnalytics
import json
from datetime import datetime
import pdfplumber
import glob
from knowledge_base import KnowledgeBase

load_dotenv()

app = Flask(__name__)

class SSOConsultantEnhanced:
    """Consultor SSO Mejorado con Analytics Predictivo"""
    
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
        self.analytics = AccidentAnalytics()
        self.knowledge_base = KnowledgeBase(self.client)
        self.analytics_data = None
        print("✅ SSO Consultant Enhanced inicializado")
        
        # Cargar datos analíticos y normativos al inicio
        self._load_analytics_data()
        self.knowledge_base.build()
    
    def _load_analytics_data(self):
        """Cargar datos analíticos"""
        try:
            print("🔄 Cargando datos analíticos...")
            self.analytics_data = self.analytics.get_comprehensive_analysis()
            if self.analytics_data:
                print(f"📊 {self.analytics_data['data_summary']['total_records']} registros procesados")
            else:
                print("⚠️ No se pudieron cargar datos analíticos")
        except Exception as e:
            print(f"❌ Error cargando analytics: {e}")
            self.analytics_data = None
    
    def process_query(self, message: str) -> str:
        """Procesa la consulta del usuario de forma dinámica y contextual."""
        try:
            # Identificar si la consulta es analítica y qué dimensiones solicita
            analytics_keywords = {
                'risk_by_area': ['área', 'zona', 'ubicación'],
                'risk_by_position': ['puesto', 'cargo', 'rol'],
                'risk_by_shift': ['turno', 'horario'],
                'risk_by_cause': ['causa', 'motivo', 'razón'],
                'risk_by_body_part': ['parte del cuerpo', 'lesión en'],
                'severity_distribution': ['severidad', 'gravedad', 'consecuencia'],
                'predicción': ['predecir', 'pronóstico', 'futuro'],
                'resumen': ['resumen', 'general', 'overview']
            }

            requested_analyses = set()
            for key, keywords in analytics_keywords.items():
                if any(keyword in message.lower() for keyword in keywords):
                    requested_analyses.add(key)

            is_analytics_query = bool(requested_analyses)

            # Generar contexto del sistema
            system_context = self._build_system_context(message, is_analytics_query, requested_analyses)

            # Si es una consulta analítica, añadir un resumen dinámico
            if is_analytics_query and self.analytics_data:
                dynamic_summary = self.analytics.generate_dynamic_executive_summary(self.analytics_data['risk_analysis'])
                message_with_context = f"{message}\n\n--- DATOS RELEVANTES ---\n{dynamic_summary}"
            else:
                message_with_context = message

            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": system_context},
                    {"role": "user", "content": message_with_context}
                ],
                temperature=0.7,
                max_tokens=2000
            )

            return response.choices[0].message.content

        except Exception as e:
            return f'''
            <div style="color: red; border: 1px solid red; padding: 10px; border-radius: 5px;">
            <h3>Error en el Sistema</h3>
            <p>No se pudo procesar su consulta.</p>
            <p><small>Error: {str(e)}</small></p>
            </div>
            '''
    
    def _build_system_context(self, query: str, include_analytics=False, requested_analyses=None):
        """Construir contexto del sistema"""
        base_context = """
        Eres un consultor experto en Seguridad y Salud Ocupacional (SSO) de clase mundial. Tu misión es modelar, predecir y reducir incidentes laborales.
        Tu objetivo principal es ayudar a los usuarios a tomar decisiones proactivas, recomendando medidas preventivas y correctivas específicas.
        Debes basar CADA UNA de tus respuestas en la siguiente información contextual, cruzando los datos estadísticos con la normativa legal para justificar tus recomendaciones.
        Elimina la variabilidad del criterio individual y enfócate en la evidencia.
        """

        # Contexto Normativo Relevante (RAG)
        relevant_context = self.knowledge_base.retrieve_relevant_chunks(query)
        base_context += relevant_context

        # Contexto Analítico
        if include_analytics and self.analytics_data:
            analytics_context = "\n\n--- CONTEXTO ANALÍTICO (DATOS DE ACCIDENTES) ---\n"
            
            # Resumen general
            analytics_context += f"Total de registros de accidentes: {self.analytics_data['data_summary']['total_records']}\n"
            analytics_context += f"Rango de datos: {self.analytics_data['data_summary']['date_range']['start']} a {self.analytics_data['data_summary']['date_range']['end']}\n"
            
            # Indicadores Clave
            if 'key_indicators' in self.analytics_data:
                indicators = self.analytics_data['key_indicators']
                analytics_context += "\n--- INDICADORES CLAVE ---\n"
                if 'top_months' in indicators:
                    analytics_context += f"Meses con mayor incidencia: {json.dumps(indicators['top_months'])}\n"
                if 'critical_areas' in indicators:
                    analytics_context += f"Áreas críticas: {json.dumps(indicators['critical_areas'])}\n"
                if 'frequent_causes' in indicators:
                    analytics_context += f"Causas más frecuentes: {json.dumps(indicators['frequent_causes'])}\n"
                if 'severity_distribution' in indicators:
                    analytics_context += f"Distribución de severidad: {json.dumps(indicators['severity_distribution'])}\n"

            # Predicción actual
            analytics_context += f"\nNivel de riesgo actual: {self.analytics_data['current_prediction']['risk_level']} (Confianza: {self.analytics_data['current_prediction']['confidence']:.1%})\n"

            # Análisis dinámico basado en la consulta
            if requested_analyses:
                analytics_context += "\n--- ANÁLISIS ESPECÍFICO SOLICITADO ---\n"
                analytics_context += self.analytics.generate_dynamic_executive_summary(self.analytics_data['risk_analysis'])

            base_context += analytics_context
        
        base_context += """

        INSTRUCCIONES DE RESPUESTA:
        1.  **Rol:** Actúa como un consultor de riesgos experto, no como un simple chatbot.
        2.  **Justificación:** SIEMPRE justifica tus recomendaciones cruzando los datos (ej. "Dado que el 25% de los accidentes son por caídas...") con la normativa (ej. "...la Ley 29783, Artículo X, exige...").
        3.  **Accionabilidad:** Proporciona recomendaciones claras, específicas y accionables. Distingue entre medidas correctivas (inmediatas) y preventivas (a largo plazo).
        4.  **Formato HTML:** Utiliza el formato HTML profesional definido a continuación para estructurar tus respuestas. Usa encabezados, tablas, listas y elementos de énfasis para máxima claridad.
        5.  **Indicadores Clave:** Aunque el usuario no los pida, incluye SIEMPRE un resumen de los indicadores clave (meses, áreas, causas) en un formato visualmente atractivo (ej. una tabla o una lista destacada), para dar un contexto rápido y valioso.

        FORMATO HTML REQUERIDO:
        - <h3> para títulos principales (ej. "Análisis de Riesgo por Área").
        - <h4> para subtítulos (ej. "Recomendaciones Preventivas").
        - <table class="risk-table"> para datos tabulados.
        - <ul> y <ol> para listas.
        - <strong> para resaltar datos clave y normativas.
        - <div class="recommendation-box"> para encerrar las recomendaciones.
        - <span class="risk-high/medium/low"> para indicar niveles de riesgo.
        """
        
        return base_context

    
    def _format_patterns_for_context(self):
        """Formatear patrones para el contexto"""
        if not self.analytics_data or 'risk_analysis' not in self.analytics_data:
            return "No hay patrones disponibles"
        
        patterns = []
        risk_analysis = self.analytics_data['risk_analysis']
        
        if 'risk_by_area' in risk_analysis and risk_analysis['risk_by_area']:
            top_areas = sorted(risk_analysis['risk_by_area'].items(), key=lambda x: x[1], reverse=True)[:3]
            patterns.append(f"Áreas de mayor riesgo: {', '.join([f'{area} ({count} incidentes)' for area, count in top_areas])}")
        
        if 'risk_by_time' in risk_analysis:
            if 'monthly' in risk_analysis['risk_by_time']:
                monthly = risk_analysis['risk_by_time']['monthly']
                high_month = max(monthly.items(), key=lambda x: x[1]) if monthly else None
                if high_month:
                    patterns.append(f"Mes de mayor riesgo: {high_month[0]} ({high_month[1]} incidentes)")
        
        return '; '.join(patterns) if patterns else "Patrones en análisis"
    
    def _format_recommendations_for_context(self):
        """Formatear recomendaciones para el contexto"""
        if not self.analytics_data or 'recommendations' not in self.analytics_data:
            return "No hay recomendaciones disponibles"
        
        recs = self.analytics_data['recommendations']
        formatted = []
        
        if recs['immediate_actions']:
            formatted.append(f"Acciones inmediatas: {'; '.join(recs['immediate_actions'][:2])}")
        
        if recs['preventive_measures']:
            formatted.append(f"Medidas preventivas: {'; '.join(recs['preventive_measures'][:2])}")
        
        return '; '.join(formatted) if formatted else "Recomendaciones en desarrollo"
    
    def get_analytics_summary(self):
        """Obtener resumen analítico"""
        if not self.analytics_data:
            return {"status": "No data available"}
        
        return {
            "status": "Available",
            "summary": self.analytics_data['data_summary'],
            "current_risk": self.analytics_data['current_prediction'],
            "top_recommendations": {
                "immediate": self.analytics_data['recommendations']['immediate_actions'][:3],
                "preventive": self.analytics_data['recommendations']['preventive_measures'][:3]
            }
        }

# Instancia global del consultor
consultant = None

def get_consultant():
    """Obtiene instancia del consultor"""
    global consultant
    if consultant is None:
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY no configurada")
        consultant = SSOConsultantEnhanced(api_key)
    return consultant

@app.route('/')
def index():
    """Página principal"""
    return render_template_string("""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SSO Consultant Enhanced - Analytics Predictivo</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .container {
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            width: 95%;
            max-width: 1000px;
            padding: 30px;
        }
        
        .header {
            text-align: center;
            margin-bottom: 30px;
        }
        
        .header h1 {
            color: #333;
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .header .subtitle {
            color: #666;
            font-size: 1.1em;
            margin-bottom: 15px;
        }
        
        .analytics-badge {
            display: inline-block;
            background: linear-gradient(45deg, #ff6b6b, #feca57);
            color: white;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 0.9em;
            font-weight: bold;
            margin-bottom: 20px;
        }
        
        .chat-container {
            border: 2px solid #e0e0e0;
            border-radius: 15px;
            height: 400px;
            overflow-y: auto;
            padding: 20px;
            margin-bottom: 20px;
            background: #f9f9f9;
        }
        
        .message {
            margin-bottom: 15px;
            padding: 15px;
            border-radius: 10px;
        }
        
        .user-message {
            background: #667eea;
            color: white;
            margin-left: 20%;
        }
        
        .assistant-message {
            background: white;
            border: 1px solid #e0e0e0;
            margin-right: 20%;
        }

        /* Enhanced HTML Response Formatting Styles */
        .assistant-message h3 {
            color: #2c3e50;
            border-bottom: 2px solid #3498db;
            padding-bottom: 8px;
            margin-top: 20px;
            margin-bottom: 15px;
            font-size: 1.3em;
        }

        .assistant-message h4 {
            color: #34495e;
            margin-top: 15px;
            margin-bottom: 10px;
            font-size: 1.1em;
        }

        .risk-table {
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }

        .risk-table thead {
            background: linear-gradient(135deg, #3498db, #2980b9);
            color: white;
        }

        .risk-table th {
            padding: 12px 15px;
            text-align: left;
            font-weight: 600;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            border: none;
        }

        .risk-table td {
            padding: 12px 15px;
            border-bottom: 1px solid #ecf0f1;
            border-left: none;
            border-right: none;
        }

        .risk-table tbody tr:hover {
            background-color: #f8f9fa;
        }

        .risk-high {
            background: linear-gradient(135deg, #e74c3c, #c0392b);
            color: white;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.8em;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            display: inline-block;
        }

        .risk-medium {
            background: linear-gradient(135deg, #f39c12, #e67e22);
            color: white;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.8em;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            display: inline-block;
        }

        .risk-low {
            background: linear-gradient(135deg, #27ae60, #229954);
            color: white;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.8em;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            display: inline-block;
        }

        .analysis-section {
            background: #f8f9fa;
            border-left: 4px solid #3498db;
            padding: 20px;
            margin: 20px 0;
            border-radius: 0 8px 8px 0;
        }

        .recommendation-box {
            background: linear-gradient(135deg, #e8f5e8, #f0f8f0);
            border: 1px solid #27ae60;
            border-radius: 8px;
            padding: 20px;
            margin: 20px 0;
        }

        .assistant-message ul {
            padding-left: 20px;
            margin: 15px 0;
        }

        .assistant-message ol {
            padding-left: 20px;
            margin: 15px 0;
        }

        .assistant-message li {
            margin-bottom: 8px;
            line-height: 1.6;
        }

        .assistant-message strong {
            color: #2c3e50;
            font-weight: 600;
        }

        .assistant-message em {
            color: #7f8c8d;
            font-style: italic;
        }
        
        .input-container {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
        }
        
        .input-field {
            flex: 1;
            padding: 15px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            font-size: 16px;
        }
        
        .send-button {
            padding: 15px 30px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            font-size: 16px;
            font-weight: bold;
        }
        
        .send-button:hover {
            background: #5a6fd8;
        }
        
        .send-button:disabled {
            background: #ccc;
            cursor: not-allowed;
        }
        
        .suggestions {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 10px;
            margin-bottom: 20px;
        }
        
        .suggestion-chip {
            background: #f0f0f0;
            border: 1px solid #ddd;
            border-radius: 10px;
            padding: 12px 15px;
            cursor: pointer;
            font-size: 14px;
            transition: all 0.3s ease;
            text-align: center;
        }
        
        .suggestion-chip:hover {
            background: #667eea;
            color: white;
            transform: translateY(-2px);
        }
        
        .analytics-chip {
            background: linear-gradient(45deg, #ff6b6b, #feca57);
            color: white;
        }
        
        .analytics-chip:hover {
            background: linear-gradient(45deg, #ff5252, #ffb300);
        }
        
        table:not(.risk-table) {
            width: 100%;
            border-collapse: collapse;
            margin: 10px 0;
        }

        table:not(.risk-table) th,
        table:not(.risk-table) td {
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }

        table:not(.risk-table) th {
            background-color: #f2f2f2;
        }
        
        .analytics-status {
            background: #e8f5e8;
            border: 1px solid #4caf50;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 20px;
            text-align: center;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🛡️ SSO Consultant Enhanced</h1>
            <p class="subtitle">Sistema de Consultoría SSO con Analytics Predictivo</p>
            <div class="analytics-badge">🔮 Powered by Machine Learning & Data Analytics</div>
        </div>
        
        <div class="analytics-status" id="analyticsStatus">
            <strong>🔄 Cargando estado analítico...</strong>
        </div>
        
        <div class="suggestions">
            <div class="suggestion-chip" onclick="sendMessage('Mi empresa tiene 50 trabajadores, ¿qué obligaciones SST tenemos?')">
                🏢 Obligaciones por tamaño
            </div>
            <div class="suggestion-chip analytics-chip" onclick="sendMessage('Basándote en nuestros datos de accidentes, ¿qué áreas presentan mayor riesgo?')">
                📊 Análisis de riesgos por área
            </div>
            <div class="suggestion-chip analytics-chip" onclick="sendMessage('¿Cuál es la predicción de riesgo para este mes basada en datos históricos?')">
                🔮 Predicción de riesgos
            </div>
            <div class="suggestion-chip analytics-chip" onclick="sendMessage('¿Qué medidas preventivas recomiendas basándote en los patrones de accidentes?')">
                🛡️ Recomendaciones preventivas
            </div>
            <div class="suggestion-chip" onclick="sendMessage('¿Qué multas aplican por no tener comité de SST?')">
                💰 Multas y sanciones
            </div>
            <div class="suggestion-chip analytics-chip" onclick="sendMessage('Analiza las tendencias temporales de accidentes y sugiere controles')">
                📈 Análisis temporal
            </div>
            <div class="suggestion-chip" onclick="showDataDictionary()">
                📚 Ver Diccionario de Datos
            </div>
            <div class="suggestion-chip analytics-chip" onclick="sendMessage('Genera un resumen ejecutivo dinámico de los datos')">
                📄 Resumen Ejecutivo Dinámico
            </div>
        </div>
        
        <div class="chat-container" id="chatContainer">
            <div class="message assistant-message">
                <strong>🛡️ SSO Consultant Enhanced</strong><br>
                ¡Hola! Soy tu consultor especializado en SSO con capacidades de análisis predictivo.<br><br>
                <strong>🔮 Nuevas Capacidades Analíticas:</strong>
                <ul>
                    <li><strong>Análisis predictivo</strong> de riesgos basado en datos históricos</li>
                    <li><strong>Identificación de patrones</strong> en accidentes laborales</li>
                    <li><strong>Recomendaciones específicas</strong> basadas en estadísticas</li>
                    <li><strong>Eliminación de sesgos</strong> mediante análisis cuantitativo</li>
                </ul>
                <strong>📋 También puedo ayudarte con:</strong>
                <ul>
                    <li>Obligaciones SST según normativa peruana</li>
                    <li>Cálculo de multas y sanciones</li>
                    <li>Implementación de sistemas de gestión</li>
                </ul>
                ¿En qué puedo ayudarte hoy?
            </div>
        </div>
        
        <div class="input-container">
            <input type="text" id="messageInput" class="input-field" placeholder="Pregunta sobre SSO o solicita análisis predictivo..." onkeypress="handleKeyPress(event)">
            <button onclick="sendMessage()" class="send-button" id="sendButton">Enviar</button>
        </div>
    </div>

    <script>
        // Cargar estado analítico al inicio
        fetch('/analytics-status')
            .then(response => response.json())
            .then(data => {
                const statusDiv = document.getElementById('analyticsStatus');
                if (data.status === 'Available') {
                    statusDiv.innerHTML = `
                        <strong>✅ Sistema Analítico Activo</strong><br>
                        📊 ${data.summary.total_records} registros procesados | 
                        🎯 Riesgo actual: ${data.current_risk.risk_level} 
                        (${(data.current_risk.confidence * 100).toFixed(1)}% confianza)
                    `;
                    statusDiv.style.background = '#e8f5e8';
                } else {
                    statusDiv.innerHTML = '<strong>⚠️ Sistema analítico no disponible - Funcionando en modo básico</strong>';
                    statusDiv.style.background = '#fff3cd';
                }
            })
            .catch(() => {
                document.getElementById('analyticsStatus').innerHTML = '<strong>⚠️ No se pudo verificar estado analítico</strong>';
            });
        
        function handleKeyPress(event) {
            if (event.key === 'Enter') {
                sendMessage();
            }
        }
        
        function sendMessage(predefinedMessage = null) {
            const input = document.getElementById('messageInput');
            const message = predefinedMessage || input.value.trim();
            
            if (!message) return;
            
            // Mostrar mensaje del usuario
            addMessage(message, 'user');
            
            // Limpiar input
            input.value = '';
            
            // Deshabilitar botón
            const sendButton = document.getElementById('sendButton');
            sendButton.disabled = true;
            sendButton.textContent = 'Procesando...';
            
            // Enviar a servidor
            fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: message })
            })
            .then(response => response.json())
            .then(data => {
                if (data.response) {
                    addMessage(data.response, 'assistant');
                } else {
                    addMessage('Error: No se recibió respuesta del servidor', 'assistant');
                }
            })
            .catch(error => {
                addMessage('Error: No se pudo conectar con el servidor', 'assistant');
                console.error('Error:', error);
            })
            .finally(() => {
                sendButton.disabled = false;
                sendButton.textContent = 'Enviar';
            });
        }
        
        function addMessage(content, type) {
            const chatContainer = document.getElementById('chatContainer');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${type}-message`;
            
            if (type === 'user') {
                messageDiv.innerHTML = `<strong>Tú:</strong><br>${content}`;
            } else {
                messageDiv.innerHTML = content;
            }
            
            chatContainer.appendChild(messageDiv);
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }

        function showDataDictionary() {
            fetch('/data-dictionary')
                .then(response => response.json())
                .then(data => {
                    let content = '<h3>📚 Diccionario de Datos</h3>';
                    content += '<table class="risk-table">';
                    content += '<thead><tr><th>Campo</th><th>Tipo</th><th>Valores Únicos</th><th>Valores Faltantes</th><th>Muestra</th></tr></thead>';
                    content += '<tbody>';
                    for (const [key, value] of Object.entries(data)) {
                        content += `<tr><td>${key}</td><td>${value.dtype}</td><td>${value.unique_values}</td><td>${value.missing_values} (${value.missing_percentage})</td><td>${value.sample.join(', ')}</td></tr>`;
                    }
                    content += '</tbody></table>';
                    addMessage(content, 'assistant');
                })
                .catch(error => {
                    addMessage('Error: No se pudo obtener el diccionario de datos', 'assistant');
                    console.error('Error:', error);
                });
        }
    </script>
</body>
</html>
    """)

@app.route('/chat', methods=['POST'])
def chat():
    """Endpoint para consultas"""
    try:
        data = request.get_json()
        message = data.get('message', '').strip()

        if not message:
            return jsonify({'error': 'Mensaje requerido'}), 400

        consultant = get_consultant()
        response = consultant.process_query(message)

        return jsonify({'response': response})

    except Exception as e:
        print(f"Error en endpoint /chat: {e}")
        return jsonify({
            'error': f'Error procesando consulta: {str(e)}'
        }), 500

@app.route('/analytics-status')
def analytics_status():
    """Endpoint para estado analítico"""
    try:
        consultant = get_consultant()
        status = consultant.get_analytics_summary()
        return jsonify(status)
    except Exception as e:
        return jsonify({"status": "Error", "message": str(e)})

@app.route('/data-dictionary')
def data_dictionary():
    """Endpoint para obtener el diccionario de datos"""
    try:
        consultant = get_consultant()
        dictionary = consultant.analytics.get_data_dictionary()
        return jsonify(dictionary)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    try:
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            print("❌ Error: OPENAI_API_KEY no configurada en .env")
            exit(1)
        
        print("🚀 Iniciando SSO Consultant Enhanced...")
        print(f"🔑 API Key: {api_key[:15]}...{api_key[-10:]}")

        # Probar conexión
        test_consultant = SSOConsultantEnhanced(api_key)

        print("✅ Sistema Enhanced listo en http://localhost:8085")
        app.run(host='0.0.0.0', port=8085, debug=True)
        
    except Exception as e:
        print(f"❌ Error iniciando sistema: {e}")
        exit(1)
