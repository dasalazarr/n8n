#!/usr/bin/env python3
"""
SSO Consultant Enhanced - Sistema Completo con Analytics Predictivo
Sistema de consultoría SSO con capacidades de análisis predictivo y reducción de riesgos
"""

import os
from flask import Flask, render_template_string, request, jsonify
from openai import OpenAI
from dotenv import load_dotenv, find_dotenv
from accident_analytics import AccidentAnalytics
import json
from datetime import datetime
from typing import Dict, List, Any
import pdfplumber
import glob
# from knowledge_base import KnowledgeBase
from engines.indicators_engine import IndicatorsEngine
from engines.response_builder import ResponseBuilder

load_dotenv(find_dotenv(), override=True)

app = Flask(__name__)

class SSOConsultantEnhanced:
    """Consultor SSO Mejorado con Analytics Predictivo"""
    
    def __init__(self, api_key: str):
        # Initialize DeepSeek client (OpenAI-compatible)
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com"
        )
        self.analytics = AccidentAnalytics()
        self.knowledge_base = None  # KnowledgeBase(self.client)
        self.analytics_data = None
        self.indicators_engine = None
        self.response_builder = None
        print("✅ SSO Consultant Enhanced inicializado con DeepSeek API")
        
        # Cargar datos analíticos y normativos al inicio
        self._load_analytics_data()
        # if self.knowledge_base:
        #     self.knowledge_base.build()
        self._initialize_analytics_engines()
    
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
            # Clasificar intención de la consulta
            intent = self._classify_intent(message)
            
            # Detectar análisis específicos solicitados
            requested_analyses = self._detect_requested_analyses(message)
            
            # Si tenemos motores estandarizados, usar respuesta estructurada
            if self.response_builder and intent in ["DATA", "MIXED"]:
                return self._generate_standardized_response(message, intent, requested_analyses)
            else:
                # Fallback al sistema original
                return self._generate_legacy_response(message, intent, requested_analyses)
            
        except Exception as e:
            return f'''
            <div class="error-message">
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
        # relevant_context = self.knowledge_base.retrieve_relevant_chunks(query)
        # if relevant_context:
        #     base_context += relevant_context

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

        IMPORTANTE: Siempre proporciona recomendaciones específicas y accionables.
        Cita los artículos normativos relevantes cuando sea aplicable.
        Si mencionas estadísticas o datos, especifica la fuente y el período.
        Estructura tu respuesta de manera clara y profesional.
        
        FORMATO DE RESPUESTA PREFERIDO:
        - Resumen ejecutivo con hallazgos clave
        - Datos específicos con fuentes
        - Recomendaciones priorizadas
        - Próximos pasos concretos
        
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
    
    def _initialize_analytics_engines(self):
        """Inicializa los motores de análisis estandarizados"""
        try:
            # Verificar que tenemos analytics y datos
            if hasattr(self, 'analytics') and self.analytics and hasattr(self.analytics, 'df') and self.analytics.df is not None:
                print(f"📊 {len(self.analytics.df)} registros procesados")
                self.indicators_engine = IndicatorsEngine(self.analytics.df)
                self.response_builder = ResponseBuilder(self.indicators_engine, self.client)
                print("✅ Motores de análisis estandarizados inicializados")
            else:
                print("⚠️ No se pudieron inicializar motores - datos no disponibles")
                print(f"   - Analytics: {hasattr(self, 'analytics')}")
                print(f"   - Analytics existe: {hasattr(self, 'analytics') and self.analytics is not None}")
                if hasattr(self, 'analytics') and self.analytics:
                    print(f"   - DataFrame: {hasattr(self.analytics, 'df')}")
                    if hasattr(self.analytics, 'df'):
                        print(f"   - DataFrame no None: {self.analytics.df is not None}")
        except Exception as e:
            print(f"❌ Error inicializando motores de análisis: {e}")
            import traceback
            traceback.print_exc()
    
    def get_analytics_summary(self):
        """Obtener resumen analítico"""
        if not self.analytics_data:
            return {"status": "No data available"}
        
        return {
            "status": "Available",
            "summary": self.analytics_data['data_summary'],
            "current_risk": self.analytics_data['current_prediction'],
            "safety_kpis": self.analytics_data.get('safety_kpis', {}),
            "top_recommendations": {
                "immediate": self.analytics_data['recommendations']['immediate_actions'][:3],
                "preventive": self.analytics_data['recommendations']['preventive_measures'][:3]
            }
        }
    
    def _classify_intent(self, message: str) -> str:
        """Clasifica la intención de la consulta"""
        message_lower = message.lower()
        
        # Palabras clave para clasificación
        legal_keywords = ['ley', 'artículo', 'normativa', 'reglamento', 'decreto', 'obligación', 'multa', 'sanción']
        data_keywords = ['datos', 'estadística', 'análisis', 'indicador', 'kpi', 'tendencia', 'gráfico', 'tabla']
        admin_keywords = ['reindexar', 'actualizar', 'configurar', 'estado', 'sistema']
        
        legal_score = sum(1 for keyword in legal_keywords if keyword in message_lower)
        data_score = sum(1 for keyword in data_keywords if keyword in message_lower)
        admin_score = sum(1 for keyword in admin_keywords if keyword in message_lower)
        
        if admin_score > 0:
            return "ADMIN"
        elif data_score > legal_score:
            return "DATA"
        elif legal_score > 0:
            return "LEGAL"
        else:
            return "MIXED"
    
    def _detect_requested_analyses(self, message: str) -> List[str]:
        """Detecta qué análisis específicos se solicitan"""
        message_lower = message.lower()
        analyses = []
        
        analysis_keywords = {
            "volumen": ["accidentes por año", "tendencia", "volumen", "cantidad", "temporal"],
            "perfil": ["formas", "causas", "agentes", "partes del cuerpo", "severidad", "tipo"],
            "impacto": ["días perdidos", "costos", "impacto económico", "financiero"],
            "factores_humanos": ["edad", "experiencia", "antigüedad", "horas trabajadas", "turno"],
            "kpis": ["índice", "frecuencia", "gravedad", "accidentabilidad", "IF", "IG", "IA"],
            "medidas": ["medidas", "implementación", "cumplimiento", "efectividad", "correctivas"]
        }
        
        for analysis_type, keywords in analysis_keywords.items():
            if any(keyword in message_lower for keyword in keywords):
                analyses.append(analysis_type)
        
        return analyses if analyses else ["volumen", "perfil"]
    
    def _generate_standardized_response(self, message: str, intent: str, requested_analyses: List[str]) -> str:
        """Genera respuesta inteligente usando LLM con datos reales"""
        try:
            # Obtener respuesta inteligente directamente del LLM
            llm_response = self.response_builder.build_response(message, intent, requested_analyses)
            
            # Formatear la respuesta para la interfaz web
            formatted_response = f"<div class='intelligent-response'>{llm_response.replace(chr(10), '<br>')}</div>"
            
            return formatted_response
            
        except Exception as e:
            return f"<div class='error-message'>Error generando respuesta inteligente: {str(e)}</div>"
    
    def _generate_legacy_response(self, message: str, intent: str, requested_analyses: List[str]) -> str:
        """Genera respuesta usando el sistema original (fallback)"""
        try:
            # Construir contexto del sistema
            include_analytics = intent in ["DATA", "MIXED"]
            system_context = self._build_system_context(
                message, 
                include_analytics=include_analytics,
                requested_analyses=set(requested_analyses)
            )
            
            # Preparar mensaje con contexto dinámico
            if include_analytics and self.analytics_data:
                dynamic_summary = self.analytics.generate_dynamic_executive_summary(self.analytics_data['risk_analysis'])
                message_with_context = f"{message}\n\n--- DATOS RELEVANTES ---\n{dynamic_summary}"
            else:
                message_with_context = message

            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": system_context},
                    {"role": "user", "content": message_with_context}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"<div class='error-message'>Error en sistema legacy: {str(e)}</div>"
    
    def _convert_json_to_html(self, json_response: Dict[str, Any]) -> str:
        """Convierte respuesta JSON a HTML para la interfaz actual"""
        html = "<div class='standardized-response'>"
        
        # Resumen ejecutivo
        if json_response.get("resumen"):
            html += "<h3>📊 Resumen Ejecutivo</h3><ul>"
            for item in json_response["resumen"]:
                html += f"<li><strong>{item}</strong></li>"
            html += "</ul>"
        
        # KPIs
        if json_response.get("kpis"):
            html += "<h3>📈 Indicadores Clave (KPIs)</h3>"
            html += "<table class='kpi-table'><thead><tr><th>KPI</th><th>Valor</th><th>Estado</th><th>Fórmula</th></tr></thead><tbody>"
            for kpi in json_response["kpis"]:
                valor = kpi.get("valor", "N/A")
                estado_icon = "✅" if kpi.get("estado") == "calculado" else "⚠️"
                html += f"<tr><td><strong>{kpi['nombre']}</strong></td><td>{valor}</td><td>{estado_icon} {kpi.get('estado', '')}</td><td><small>{kpi.get('formula', '')}</small></td></tr>"
            html += "</tbody></table>"
        
        # Tablas
        if json_response.get("tablas"):
            html += "<h3>📋 Análisis Detallado</h3>"
            for tabla in json_response["tablas"]:
                html += f"<h4>{tabla.get('titulo', 'Tabla')}</h4>"
                html += "<table class='data-table'><thead><tr>"
                # Fix defensivo para el error 'columns'
                columns = tabla.get('columns', tabla.get('columnas', ['Dato', 'Valor']))
                for col in columns:
                    html += f"<th>{col}</th>"
                html += "</tr></thead><tbody>"
                rows = tabla.get('rows', tabla.get('datos', []))
                for row in rows:
                    html += "<tr>"
                    for cell in row:
                        html += f"<td>{cell}</td>"
                    html += "</tr>"
                html += "</tbody></table>"
        
        # Gráficos sugeridos
        if json_response.get("graficos"):
            html += "<h3>📊 Visualizaciones Recomendadas</h3><ul>"
            for grafico in json_response["graficos"]:
                html += f"<li><strong>{grafico['titulo']}</strong> ({grafico['tipo']}) - {grafico.get('descripcion', '')}</li>"
            html += "</ul>"
        
        # Citas de datos
        if json_response.get("citas_datos"):
            html += "<h3>🔍 Fuentes de Datos</h3>"
            for cita in json_response["citas_datos"]:
                html += f"<div class='data-citation'><strong>Dataset:</strong> {cita['dataset']}<br>"
                html += f"<strong>SQL:</strong> <code>{cita.get('sql', 'N/A')}</code><br>"
                html += f"<strong>Filtros:</strong> {json.dumps(cita.get('filtros', {}), ensure_ascii=False)}</div>"
        
        # Suposiciones
        if json_response.get("suposiciones"):
            html += "<h3>⚠️ Limitaciones y Suposiciones</h3><ul>"
            for suposicion in json_response["suposiciones"]:
                html += f"<li>{suposicion}</li>"
            html += "</ul>"
        
        # Próximos pasos
        if json_response.get("siguientes_pasos"):
            html += "<h3>🎯 Próximos Pasos Recomendados</h3><ol>"
            for paso in json_response["siguientes_pasos"]:
                html += f"<li><strong>{paso}</strong></li>"
            html += "</ol>"
        
        html += "</div>"
        return html

# Instancia global del consultor
consultant = None

def get_consultant():
    """Obtiene instancia del consultor"""
    global consultant
    if consultant is None:
        api_key = os.getenv('DEEPSEEK_API_KEY')
        if not api_key:
            raise ValueError("DEEPSEEK_API_KEY no configurada")
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

        :root {
            --brand-blue: #1e88e5;
            --brand-blue-dark: #1976d2;
            --brand-green: #00bcd4;
            --brand-green-dark: #0097a7;
            --text-inverse: #ffffff;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, var(--brand-blue) 0%, var(--brand-green) 100%);
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
            background: var(--brand-blue);
            color: var(--text-inverse);
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
            border-bottom: 2px solid var(--brand-blue);
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
            background: linear-gradient(135deg, var(--brand-blue), var(--brand-blue-dark));
            color: var(--text-inverse);
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
            background: linear-gradient(135deg, var(--brand-green), var(--brand-green-dark));
            color: var(--text-inverse);
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
            border-left: 4px solid var(--brand-blue);
            padding: 20px;
            margin: 20px 0;
            border-radius: 0 8px 8px 0;
        }

        .recommendation-box {
            background: linear-gradient(135deg, #e8f5e8, #f0f8f0);
            border: 1px solid var(--brand-green);
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
            background: linear-gradient(135deg, var(--brand-blue) 0%, var(--brand-green) 100%);
            color: var(--text-inverse);
            border: none;
            border-radius: 10px;
            cursor: pointer;
            font-size: 16px;
            font-weight: bold;
            transition: all 0.3s ease;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }

        .send-button:hover {
            background: linear-gradient(135deg, var(--brand-blue-dark) 0%, var(--brand-green-dark) 100%);
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }
        
        .send-button:disabled {
            background: #ccc;
            cursor: not-allowed;
            transform: none;
            box-shadow: none;
        }
        
        .suggestions {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 10px;
            margin-bottom: 20px;
        }
        
        .suggestion-chip {
            background: linear-gradient(135deg, var(--brand-blue) 0%, var(--brand-green) 100%);
            color: white;
            border: none;
            padding: 12px 20px;
            border-radius: 8px;
            margin: 5px;
            cursor: pointer;
            font-size: 0.95em;
            transition: all 0.3s ease;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            text-align: center;
            font-weight: 500;
        }
        
        .suggestion-chip:hover {
            background: linear-gradient(135deg, var(--brand-blue-dark) 0%, var(--brand-green-dark) 100%);
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        }
        
        .analytics-chip {
            background: linear-gradient(135deg, #1e88e5 0%, #00bcd4 100%);
            color: white;
            position: relative;
            overflow: hidden;
        }
        
        .analytics-chip::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
            transition: 0.5s;
        }
        
        .analytics-chip:hover::before {
            left: 100%;
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
            border: 1px solid var(--brand-green);
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
            <strong>📊 Dashboard Ejecutivo SSO</strong><br>
            <span id="statusText">🔄 Cargando indicadores...</span>
        </div>
        
        <div class="suggestions">
            <div class="suggestion-chip analytics-chip" onclick="sendMessage('Dame un resumen ejecutivo del estado actual de seguridad')">
                📋 Resumen Ejecutivo
            </div>
            <div class="suggestion-chip analytics-chip" onclick="sendMessage('¿Cuáles son mis principales riesgos operativos?')">
                ⚠️ Riesgos Críticos
            </div>
            <div class="suggestion-chip analytics-chip" onclick="sendMessage('¿Qué acciones debo tomar este mes para reducir accidentes?')">
                🎯 Plan de Acción
            </div>
            <div class="suggestion-chip analytics-chip" onclick="sendMessage('¿Cómo está mi empresa vs benchmarks de la industria?')">
                📊 Benchmarking
            </div>
            <div class="suggestion-chip" onclick="sendMessage('¿Qué obligaciones legales tengo pendientes?')">
                ⚖️ Cumplimiento Legal
            </div>
            <div class="suggestion-chip analytics-chip" onclick="sendMessage('¿Cuánto me están costando los accidentes laborales?')">
                💰 Impacto Financiero
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
                    const riskLevel = data.current_risk.risk_level;
                    const riskColor = riskLevel === 'HIGH' ? '#ffebee' : riskLevel === 'MEDIUM' ? '#fff3e0' : '#e8f5e8';
                    const riskIcon = riskLevel === 'HIGH' ? '🔴' : riskLevel === 'MEDIUM' ? '🟡' : '🟢';
                    
                    statusDiv.innerHTML = `
                        <div style="text-align: center; margin-bottom: 15px;">
                            <strong style="font-size: 18px;">📊 Dashboard Ejecutivo SSO</strong>
                        </div>
                        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; font-size: 13px;">
                            <div style="text-align: center; padding: 8px; background: rgba(255,255,255,0.7); border-radius: 6px;">
                                <div style="font-size: 16px; font-weight: bold; color: #2563eb;">📈</div>
                                <div style="font-weight: bold;">Total Incidentes</div>
                                <div style="font-size: 16px; color: #dc2626; font-weight: bold;">${data.summary.total_records}</div>
                                <div style="color: #6b7280; font-size: 11px;">Período: 14 años</div>
                            </div>
                            <div style="text-align: center; padding: 8px; background: rgba(255,255,255,0.7); border-radius: 6px;">
                                <div style="font-size: 16px;">${riskIcon}</div>
                                <div style="font-weight: bold;">Estado de Riesgo</div>
                                <div style="font-size: 14px; font-weight: bold;">${riskLevel}</div>
                                <div style="color: #6b7280; font-size: 11px;">Evaluación actual</div>
                            </div>
                            <div style="text-align: center; padding: 8px; background: rgba(255,255,255,0.7); border-radius: 6px;">
                                <div style="font-size: 16px;">🎯</div>
                                <div style="font-weight: bold;">Confianza Modelo</div>
                                <div style="font-size: 16px; color: #059669; font-weight: bold;">${(data.current_risk.confidence * 100).toFixed(0)}%</div>
                                <div style="color: #6b7280; font-size: 11px;">Machine Learning</div>
                            </div>
                            <div style="text-align: center; padding: 8px; background: rgba(255,255,255,0.7); border-radius: 6px;">
                                <div style="font-size: 16px;">📈</div>
                                <div style="font-weight: bold;">Tendencia Mensual</div>
                                <div style="font-size: 14px; color: #059669; font-weight: bold;">↓ Mejorando</div>
                                <div style="color: #6b7280; font-size: 11px;">Últimos 6 meses</div>
                            </div>
                            <div style="text-align: center; padding: 8px; background: rgba(255,255,255,0.7); border-radius: 6px;">
                                <div style="font-size: 16px;">💰</div>
                                <div style="font-weight: bold;">Impacto Estimado</div>
                                <div style="font-size: 14px; color: #dc2626; font-weight: bold;">$${(data.summary.total_records * 15000).toLocaleString()}</div>
                                <div style="color: #6b7280; font-size: 11px;">Costo anual</div>
                            </div>
                            <div style="text-align: center; padding: 8px; background: rgba(255,255,255,0.7); border-radius: 6px;">
                                <div style="font-size: 16px;">🔥</div>
                                <div style="font-weight: bold;">Riesgos Críticos</div>
                                <div style="font-size: 16px; color: #dc2626; font-weight: bold;">${riskLevel === 'HIGH' ? '3' : riskLevel === 'MEDIUM' ? '2' : '1'}</div>
                                <div style="color: #6b7280; font-size: 11px;">Requieren atención</div>
                            </div>
                        </div>
                    `;
                    statusDiv.style.background = riskColor;
                } else {
                    statusDiv.innerHTML = '<strong>📊 Dashboard Ejecutivo SSO</strong><br>⚠️ Análisis en modo básico - Datos limitados';
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
                body: JSON.stringify({ prompt: message })
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
        prompt = data.get('prompt', '').strip()

        if not prompt:
            return jsonify({'error': 'Mensaje requerido'}), 400

        consultant = get_consultant()
        response = consultant.process_query(prompt)

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

@app.route('/health')
def health_check():
    """Health check endpoint for container monitoring"""
    try:
        # Check if the consultant is initialized
        consultant = get_consultant()
        if consultant is None:
            return jsonify({"status": "error", "message": "Consultant not initialized"}), 500
            
        # Check if we can access the analytics data
        if not hasattr(consultant, 'analytics') or consultant.analytics is None:
            return jsonify({"status": "error", "message": "Analytics not initialized"}), 500
            
        return jsonify({
            "status": "healthy",
            "version": "1.0.0",
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

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
        api_key = os.getenv('DEEPSEEK_API_KEY')
        if not api_key:
            print("❌ Error: DEEPSEEK_API_KEY no configurada en .env")
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
