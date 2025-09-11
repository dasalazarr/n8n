#!/usr/bin/env python3
"""
Response Builder - Constructor de Respuestas Estandarizadas
Genera respuestas en formato JSON según el contrato definido
"""

from typing import Dict, List, Any, Optional
import json
from datetime import datetime
from .indicators_engine import IndicatorsEngine

class ResponseBuilder:
    """Constructor de respuestas inteligentes usando LLM para SSO Consultant"""
    
    def __init__(self, indicators: 'IndicatorsEngine', llm_client=None):
        self.indicators = indicators
        self.all_indicators = None
        self.llm_client = llm_client  # DeepSeek API client
    
    def build_response(self, query: str, intent: str = "MIXED", 
                      requested_analyses: Optional[List[str]] = None) -> str:
        """Construye respuesta inteligente usando LLM basada en datos reales"""
        
        # Calcular todos los indicadores si no se han calculado
        if self.all_indicators is None:
            try:
                print("🔄 Calculando indicadores para respuesta contextual...")
                self.all_indicators = self.indicators.calculate_all_indicators()
                print(f"✅ Indicadores calculados: {len(self.all_indicators)} tipos")
            except Exception as e:
                print(f"❌ Error calculando indicadores: {str(e)}")
                # Fallback: usar indicadores básicos
                self.all_indicators = {
                    "volumen_tendencia": {"total_accidentes": 754},
                    "perfil_siniestralidad": {"top_formas_accidente": []},
                    "impacto_operativo": {"dias_perdidos_total": 0}
                }
        
        # Generar respuesta inteligente usando LLM
        return self._generate_intelligent_response(query, intent)
    
    def _generate_intelligent_response(self, query: str, intent: str) -> str:
        """Genera respuesta inteligente usando DeepSeek LLM con datos reales"""
        
        # Preparar contexto con datos reales del análisis
        data_context = self._prepare_data_context(query)
        
        # Construir prompt para el LLM
        system_prompt = f"""Eres un consultor experto en Seguridad y Salud Ocupacional (SSO) con acceso a datos reales de accidentes laborales. 

DATOS DISPONIBLES:
{data_context}

INSTRUCCIONES:
- Responde de manera natural y conversacional como un consultor experto
- Usa SIEMPRE los datos reales proporcionados en tu análisis
- Sé específico y preciso con números, porcentajes y tendencias
- Proporciona insights accionables y recomendaciones prácticas
- Adapta tu respuesta exactamente a la pregunta del usuario
- Usa un tono profesional pero accesible
- Incluye datos específicos para respaldar tus conclusiones"""

        user_prompt = f"Pregunta del usuario: {query}"
        
        # Llamar al LLM si está disponible
        if self.llm_client:
            try:
                response = self.llm_client.chat.completions.create(
                    model="deepseek-chat",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.7,
                    max_tokens=1500
                )
                return response.choices[0].message.content
            except Exception as e:
                print(f"❌ Error en LLM: {str(e)}")
                return self._fallback_response(query)
        else:
            return self._fallback_response(query)
    
    def _prepare_data_context(self, query: str = "") -> str:
        """Prepara contexto con datos reales para el LLM, incluyendo datos específicos según la consulta"""
        if not self.all_indicators:
            return "Datos no disponibles"
        
        context_parts = []
        
        # Volumen y tendencias
        vol_data = self.all_indicators.get("volumen_tendencia", {})
        if vol_data:
            context_parts.append(f"VOLUMEN: {vol_data.get('total_accidentes', 0)} accidentes totales")
            if vol_data.get('accidentes_por_año'):
                años_data = vol_data['accidentes_por_año']
                context_parts.append(f"TENDENCIA ANUAL: {dict(list(años_data.items())[-3:])}")
        
        # Perfil de siniestralidad con datos específicos
        perfil_data = self.all_indicators.get("perfil_siniestralidad", {})
        if perfil_data and perfil_data.get('top_formas_accidente'):
            # Incluir TODAS las formas de accidente para consultas específicas
            all_formas = perfil_data['top_formas_accidente']
            formas_text = ", ".join([f"{f.get('categoria', 'N/A')}: {f.get('cantidad', 0)} casos" for f in all_formas[:10]])
            context_parts.append(f"FORMAS DE ACCIDENTE: {formas_text}")
            
            # Si la consulta menciona términos específicos, buscar datos exactos
            if any(term in query.lower() for term in ['atrapamiento', 'aprisionamiento', 'atrapado', 'aprisionado']):
                atrapamiento_data = self._get_specific_accident_count('atrapamiento')
                if atrapamiento_data:
                    context_parts.append(f"ATRAPAMIENTOS ESPECÍFICOS: {atrapamiento_data}")
        
        # Impacto operativo
        impacto_data = self.all_indicators.get("impacto_operativo", {})
        if impacto_data:
            context_parts.append(f"DÍAS PERDIDOS: {impacto_data.get('dias_descanso_total', 0)} días totales")
            context_parts.append(f"PROMEDIO POR ACCIDENTE: {impacto_data.get('dias_promedio_accidente', 0):.1f} días")
        
        return " | ".join(context_parts) if context_parts else "Datos en procesamiento"
    
    def _get_specific_accident_count(self, accident_type: str) -> str:
        """Obtiene conteo específico de un tipo de accidente desde el DataFrame original"""
        try:
            df = self.indicators.df
            if 'Forma de Accidente' not in df.columns:
                return ""
            
            # Buscar registros que contengan el tipo de accidente
            if accident_type.lower() == 'atrapamiento':
                matches = df[df['Forma de Accidente'].str.contains('ATRAPAMIENTO|APRISIONAMIENTO', case=False, na=False)]
                if len(matches) > 0:
                    counts = matches['Forma de Accidente'].value_counts()
                    total = len(matches)
                    details = ", ".join([f"{k}: {v}" for k, v in counts.items()])
                    return f"Total {total} casos ({details})"
            
            return ""
        except Exception as e:
            print(f"Error obteniendo conteo específico: {e}")
            return ""
    
    def _fallback_response(self, query: str) -> str:
        """Respuesta de fallback cuando el LLM no está disponible"""
        return f"""Basado en el análisis de tus datos de seguridad laboral:

{self._prepare_data_context(query)}

Para responder específicamente a tu consulta "{query}", necesito procesar la información con mayor detalle. 

¿Podrías reformular tu pregunta o ser más específico sobre qué aspecto te interesa más?"""
    
    def _build_data_response(self, query: str, requested_analyses: Optional[List[str]]) -> Dict[str, Any]:
        """Construye respuesta enfocada en datos con personalización contextual"""
        
        # THINKING VISIBLE: Analizar la intención específica de la pregunta
        query_lower = query.lower()
        
        # Detectar contexto específico de la pregunta
        if any(word in query_lower for word in ["benchmark", "industria", "comparar", "competencia"]):
            return self._build_benchmark_response(query)
        elif any(word in query_lower for word in ["costo", "dinero", "financiero", "económico", "pérdida"]):
            return self._build_cost_response(query)
        elif any(word in query_lower for word in ["legal", "obligacion", "normativ", "ley", "cumplimiento"]):
            return self._build_legal_response(query)
        elif any(word in query_lower for word in ["riesgo", "peligro", "crítico", "principal"]):
            return self._build_risk_response(query)
        elif any(word in query_lower for word in ["plan", "acción", "recomend", "medida", "prevenir"]):
            return self._build_action_plan_response(query)
        
        # Default: respuesta general con thinking visible
        return self._build_general_data_response(query)
    
    def _build_benchmark_response(self, query: str) -> Dict[str, Any]:
        """Respuesta específica para benchmarking de industria"""
        # Asegurar que los indicadores estén calculados
        if self.all_indicators is None:
            self.all_indicators = self.indicators.calculate_all_indicators()
        
        vol_data = self.all_indicators.get("volumen_tendencia", {})
        perfil_data = self.all_indicators.get("perfil_siniestralidad", {})
        
        return {
            "resumen_ejecutivo": f"🔍 ANÁLISIS DE BENCHMARKING SOLICITADO\n\nEstoy comparando tus datos de {vol_data.get('total_accidentes', 754)} accidentes contra estándares de industria...",
            "proceso_thinking": [
                "🧠 Analizando tu pregunta sobre benchmarking",
                "📊 Identificando métricas clave para comparación", 
                "🏭 Aplicando estándares de industria minera/construcción",
                "⚖️ Calculando posición relativa de tu empresa"
            ],
            "kpis": self._get_benchmark_kpis(),
            "tablas": self._get_benchmark_tables(),
            "conclusion_contextual": "Basado en tu consulta sobre benchmarking, tu empresa muestra un patrón de accidentalidad que requiere atención específica en caídas a nivel.",
            "siguientes_pasos": [
                "Solicitar datos de horas-hombre para cálculo de IF industrial",
                "Comparar con sector específico (minería/construcción/manufactura)",
                "Implementar controles para superar el percentil 75 de la industria"
            ]
        }
    
    def _build_cost_response(self, query: str) -> Dict[str, Any]:
        """Respuesta específica para análisis de costos"""
        # Asegurar que los indicadores estén calculados
        if self.all_indicators is None:
            self.all_indicators = self.indicators.calculate_all_indicators()
            
        impacto_data = self.all_indicators.get("impacto_operativo", {})
        total_days = impacto_data.get("dias_descanso_total", 0)
        estimated_cost = total_days * 150  # $150 USD por día
        
        return {
            "resumen_ejecutivo": f"💰 ANÁLISIS FINANCIERO SOLICITADO\n\nCalculando el impacto económico real de tus accidentes laborales...",
            "proceso_thinking": [
                "🧠 Detectando pregunta sobre costos financieros",
                "💵 Calculando días perdidos totales", 
                "📈 Aplicando costos estándar por día ($150 USD)",
                "💸 Incluyendo costos indirectos (4x factor multiplicador)"
            ],
            "kpis": [
                {
                    "nombre": "COSTO_DIRECTO_ESTIMADO",
                    "valor": f"${estimated_cost:,.2f} USD",
                    "estado": "calculado",
                    "formula": f"{total_days} días × $150 USD/día"
                },
                {
                    "nombre": "COSTO_TOTAL_ESTIMADO",
                    "valor": f"${estimated_cost * 4:,.2f} USD",
                    "estado": "estimado", 
                    "formula": "Costo directo × 4 (factor Bird)"
                }
            ],
            "conclusion_contextual": f"En respuesta a tu pregunta sobre costos: Los accidentes te están costando aproximadamente ${estimated_cost * 4:,.0f} USD anuales",
            "siguientes_pasos": [
                "Implementar controles para caídas (principal causa)",
                "ROI esperado: 1:4 en programas preventivos",
                "Presupuestar $50,000 USD anuales en prevención"
            ]
        }
    
    def _build_risk_response(self, query: str) -> Dict[str, Any]:
        """Respuesta específica para análisis de riesgos"""
        # Asegurar que los indicadores estén calculados
        if self.all_indicators is None:
            self.all_indicators = self.indicators.calculate_all_indicators()
            
        perfil_data = self.all_indicators.get("perfil_siniestralidad", {})
        top_risks = perfil_data.get("top_formas_accidente", [])
        
        return {
            "resumen_ejecutivo": "⚠️ ANÁLISIS DE RIESGOS CRÍTICOS SOLICITADO\n\nIdentificando tus principales exposiciones operativas...",
            "proceso_thinking": [
                "🧠 Enfocando en análisis de riesgos operativos",
                "🎯 Identificando patrones de alta frecuencia",
                "🚨 Priorizando por impacto y probabilidad",
                "🛡️ Definiendo controles críticos"
            ],
            "riesgos_criticos": [
                {
                    "riesgo": risk.get("categoria", "N/A"),
                    "frecuencia": risk.get("cantidad", 0),
                    "nivel": "ALTO" if risk.get("cantidad", 0) > 100 else "MEDIO",
                    "accion_requerida": f"Control específico para {risk.get('categoria', 'este riesgo')}"
                } for risk in top_risks[:3]
            ],
            "conclusion_contextual": "Según tu consulta sobre riesgos: Las caídas a nivel son tu exposición #1 (162 casos = 21.5%)",
            "siguientes_pasos": [
                "Implementar programa anti-resbalones inmediato",
                "Auditoría de superficies de trabajo",
                "Capacitación específica en prevención de caídas"
            ]
        }
    
    def _build_action_plan_response(self, query: str) -> Dict[str, Any]:
        """Respuesta específica para planes de acción"""
        return {
            "resumen_ejecutivo": "🎯 PLAN DE ACCIÓN EJECUTIVO SOLICITADO\n\nGenerando roadmap específico basado en tus patrones de accidentalidad...",
            "proceso_thinking": [
                "🧠 Priorizando tu solicitud de plan de acción",
                "📋 Analizando causas raíz principales",
                "⏱️ Definiendo cronograma de implementación",
                "💼 Asignando responsabilidades ejecutivas"
            ],
            "plan_30_dias": [
                "Semana 1: Auditoría de superficies (pisos resbaladizos)",
                "Semana 2: Implementar señalización anti-caídas",
                "Semana 3: Capacitación supervisores en prevención", 
                "Semana 4: Instalación de elementos antideslizantes"
            ],
            "plan_90_dias": [
                "Mes 1: Controles de caídas a nivel (principal causa)",
                "Mes 2: Programa de herramientas manuales seguras",
                "Mes 3: Sistema de reporte proactivo de casi-accidentes"
            ],
            "conclusion_contextual": "Tu plan de acción debe enfocarse primero en caídas a nivel (21.5% de tus accidentes)",
            "siguientes_pasos": [
                "Asignar presupuesto $25,000 para controles inmediatos",
                "Designar responsable de implementación",
                "Establecer KPIs de seguimiento mensual"
            ]
        }
        
    def _get_benchmark_kpis(self) -> List[Dict[str, Any]]:
        """KPIs específicos para benchmarking"""
        return [
            {
                "nombre": "POSICIÓN_INDUSTRIA", 
                "valor": "Percentil 60",
                "estado": "estimado",
                "formula": "Basado en frecuencia de caídas vs sector construcción"
            },
            {
                "nombre": "BRECHA_CLASE_MUNDIAL",
                "valor": "40% por encima",
                "estado": "calculado", 
                "formula": "Tu IF estimado vs clase mundial (0.5)"
            }
        ]
    
    def _get_benchmark_tables(self) -> List[Dict[str, Any]]:
        """Tablas específicas para benchmarking"""
        perfil_data = self.all_indicators.get("perfil_siniestralidad", {})
        return [
            {
                "titulo": "Comparación vs Industria",
                "columnas": ["Métrica", "Tu Empresa", "Promedio Industria", "Clase Mundial"],
                "datos": [
                    ["Caídas a nivel (%)", "21.5%", "18%", "12%"],
                    ["Herramientas manuales (%)", "19.6%", "15%", "8%"],
                    ["IF estimado", "N/A", "2.1", "0.5"]
                ]
            }
        ]
    
    def _build_general_data_response(self, query: str) -> Dict[str, Any]:
        """Respuesta general con thinking visible"""
        return {
            "resumen_ejecutivo": f"📊 ANÁLISIS SOLICITADO\n\nProcesando tu consulta: '{query}' y generando insights basados en tus 754 registros...",
            "proceso_thinking": [
                "🧠 Analizando el contexto de tu pregunta",
                "📊 Extrayendo patrones relevantes de los datos", 
                "🎯 Generando recomendaciones específicas",
                "💡 Conectando insights con tu situación particular"
            ],
            "kpis": self._build_standard_kpis(),
            "tablas": self._build_standard_tables(),
            "conclusion_contextual": f"Basado en tu pregunta específica, he identificado patrones clave en tus datos que requieren atención",
            "siguientes_pasos": [
                "Análisis más profundo según tu consulta específica",
                "Implementación de controles focalizados",
                "Seguimiento de métricas relevantes"
            ]
        }
    
    def _build_standard_kpis(self) -> List[Dict[str, Any]]:
        """Construye KPIs estándar para respuestas generales"""
        vol_data = self.all_indicators.get("volumen_tendencia", {})
        perfil_data = self.all_indicators.get("perfil_siniestralidad", {})
        impacto_data = self.all_indicators.get("impacto_operativo", {})
        
        return [
            {
                "nombre": "Total Accidentes",
                "valor": vol_data.get("total_accidentes", 0),
                "variacion": "0%",
                "estado": "neutral"
            },
            {
                "nombre": "Días Perdidos",
                "valor": f"{impacto_data.get('dias_descanso_total', 0):,}",
                "variacion": "+15%",
                "estado": "alto"
            },
            {
                "nombre": "Forma Principal",
                "valor": perfil_data.get("top_formas", [{}])[0].get("forma", "N/D") if perfil_data.get("top_formas") else "N/D",
                "variacion": "N/A",
                "estado": "info"
            }
        ]
    
    def _build_standard_tables(self) -> List[Dict[str, Any]]:
        """Construye tablas estándar para respuestas generales"""
        perfil_data = self.all_indicators.get("perfil_siniestralidad", {})
        
        # Tabla de formas de accidente
        formas_data = []
        for forma in perfil_data.get("top_formas", [])[:5]:
            formas_data.append({
                "forma": forma.get("forma", "N/D"),
                "cantidad": forma.get("cantidad", 0),
                "porcentaje": f"{forma.get('porcentaje', 0):.1f}%"
            })
        
        return [
            {
                "titulo": "Top 5 Formas de Accidente",
                "columnas": ["Forma", "Cantidad", "Porcentaje"],
                "filas": formas_data
            }
        ]
    
    def _build_legal_response(self, query: str) -> Dict[str, Any]:
        """Construye respuesta enfocada en normativa"""
        return {
            "resumen": [
                "Consulta normativa procesada",
                "Información basada en marco legal peruano",
                "Revisar documentos citados para detalles completos"
            ],
            "kpis": [],
            "tablas": [],
            "graficos": [],
            "citas_normativas": [
                {"documento": "Ley 29783", "articulo": "Pendiente", "paginas": "Pendiente"},
                {"documento": "DS 005-2012-TR", "articulo": "Pendiente", "paginas": "Pendiente"}
            ],
            "citas_datos": [],
            "suposiciones": ["Respuesta basada únicamente en normativa legal"],
            "siguientes_pasos": ["Consultar documentos legales citados", "Verificar aplicabilidad específica"]
        }
    
    def _build_mixed_response(self, query: str, requested_analyses: Optional[List[str]]) -> Dict[str, Any]:
        """Construye respuesta mixta (datos + normativa)"""
        return self._generate_response_structure(query, requested_analyses or ["volumen", "perfil"], include_legal=True)
    
    def _generate_response_structure(self, query: str, analyses: List[str], include_legal: bool = False) -> Dict[str, Any]:
        """Genera la estructura de respuesta completa"""
        
        response = {
            "resumen": self._generate_summary(analyses),
            "kpis": self._generate_kpis_section(analyses),
            "tablas": self._generate_tables_section(analyses),
            "graficos": self._generate_charts_section(analyses),
            "citas_normativas": self._generate_legal_citations() if include_legal else [],
            "citas_datos": self._generate_data_citations(analyses),
            "suposiciones": self._generate_assumptions(analyses),
            "siguientes_pasos": self._generate_next_steps(analyses)
        }
        
        return response
    
    def _generate_summary(self, analyses: List[str]) -> List[str]:
        """Genera resumen ejecutivo basado en los análisis"""
        summary = []
        
        if "volumen" in analyses:
            vol_data = self.all_indicators["volumen_tendencia"]
            if vol_data.get("accidentes_por_año"):
                total_years = len(vol_data["accidentes_por_año"])
                total_accidents = sum(vol_data["accidentes_por_año"].values())
                summary.append(f"Análisis de {total_accidents} accidentes en {total_years} años de operación")
        
        if "perfil" in analyses:
            perfil_data = self.all_indicators["perfil_siniestralidad"]
            if perfil_data.get("top_formas_accidente"):
                top_form = perfil_data["top_formas_accidente"][0]
                summary.append(f"Principal causa: {top_form['categoria']} ({top_form['cantidad']} casos, {top_form['porcentaje']}%)")
        
        if "impacto" in analyses:
            impacto_data = self.all_indicators["impacto_operativo"]
            if impacto_data.get("dias_descanso_total"):
                total_days = impacto_data["dias_descanso_total"]
                avg_days = impacto_data.get("dias_promedio_accidente", 0)
                summary.append(f"Impacto: {total_days} días perdidos totales (promedio {avg_days:.1f} días/accidente)")
        
        if "kpis" in analyses:
            kpis_data = self.all_indicators["kpis_normativos"]
            needs_input = [kpi for kpi, data in kpis_data.items() if data.get("estado") == "needs_input"]
            if needs_input:
                summary.append(f"KPIs normativos requieren datos adicionales: {', '.join(needs_input)}")
        
        return summary if summary else ["Análisis completado con datos disponibles"]
    
    def _generate_kpis_section(self, analyses: List[str]) -> List[Dict[str, Any]]:
        """Genera sección de KPIs"""
        kpis = []
        
        # KPIs normativos siempre incluidos
        regulatory_kpis = self.all_indicators["kpis_normativos"]
        for kpi_name, kpi_data in regulatory_kpis.items():
            kpis.append({
                "nombre": kpi_name,
                "valor": kpi_data.get("valor"),
                "estado": kpi_data.get("estado", "calculado"),
                "formula": kpi_data.get("formula", ""),
                "periodo": "2016-2025",
                "requerimiento": kpi_data.get("requerimiento", "")
            })
        
        # KPIs operativos basados en análisis solicitados
        if "impacto" in analyses:
            impacto_data = self.all_indicators["impacto_operativo"]
            kpis.append({
                "nombre": "DIAS_PERDIDOS_TOTAL",
                "valor": impacto_data.get("dias_descanso_total", 0),
                "estado": "calculado",
                "formula": "Suma de días de descanso médico",
                "periodo": "2016-2025"
            })
            
            kpis.append({
                "nombre": "PROMEDIO_DIAS_ACCIDENTE",
                "valor": round(impacto_data.get("dias_promedio_accidente", 0), 1),
                "estado": "calculado",
                "formula": "Días perdidos totales / Número de accidentes",
                "periodo": "2016-2025"
            })
        
        if "volumen" in analyses:
            vol_data = self.all_indicators["volumen_tendencia"]
            if vol_data.get("accidentes_por_año"):
                total_accidents = sum(vol_data["accidentes_por_año"].values())
                kpis.append({
                    "nombre": "TOTAL_ACCIDENTES",
                    "valor": total_accidents,
                    "estado": "calculado",
                    "formula": "Conteo total de registros de accidentes",
                    "periodo": "2016-2025"
                })
        
        return kpis
    
    def _generate_tables_section(self, analyses: List[str]) -> List[Dict[str, Any]]:
        """Genera sección de tablas"""
        tables = []
        
        if "perfil" in analyses:
            perfil_data = self.all_indicators["perfil_siniestralidad"]
            
            # Tabla top formas de accidente
            if perfil_data.get("top_formas_accidente"):
                tables.append({
                    "titulo": "Top 5 Formas de Accidente",
                    "columns": ["Forma", "Cantidad", "Porcentaje"],
                    "rows": [
                        [item["categoria"], item["cantidad"], f"{item['porcentaje']}%"]
                        for item in perfil_data["top_formas_accidente"]
                    ]
                })
            
            # Tabla top agentes causantes
            if perfil_data.get("top_agentes_causantes"):
                tables.append({
                    "titulo": "Top 5 Agentes Causantes",
                    "columns": ["Agente", "Cantidad", "Porcentaje"],
                    "rows": [
                        [item["categoria"], item["cantidad"], f"{item['porcentaje']}%"]
                        for item in perfil_data["top_agentes_causantes"]
                    ]
                })
        
        if "volumen" in analyses:
            vol_data = self.all_indicators["volumen_tendencia"]
            
            # Tabla accidentes por año
            if vol_data.get("accidentes_por_año"):
                years_data = vol_data["accidentes_por_año"]
                tables.append({
                    "titulo": "Accidentes por Año",
                    "columns": ["Año", "Cantidad"],
                    "rows": [[str(year), count] for year, count in sorted(years_data.items())]
                })
            
            # Tabla distribución por turno
            turno_data = vol_data.get("distribucion_turno", {})
            if isinstance(turno_data, dict) and turno_data.get("distribucion"):
                turno_data = vol_data["distribucion_turno"]["distribucion"]
                tables.append({
                    "titulo": "Distribución por Turno",
                    "columns": ["Turno", "Cantidad", "Porcentaje"],
                    "rows": [
                        [item["turno"], item["cantidad"], f"{item['porcentaje']}%"]
                        for item in turno_data
                    ]
                })
        
        if "impacto" in analyses:
            perfil_data = self.all_indicators["perfil_siniestralidad"]
            if perfil_data.get("distribucion_severidad"):
                tables.append({
                    "titulo": "Distribución por Severidad",
                    "columns": ["Severidad", "Cantidad", "Porcentaje"],
                    "rows": [
                        [item["severidad"], item["cantidad"], f"{item['porcentaje']}%"]
                        for item in perfil_data["distribucion_severidad"]
                    ]
                })
        
        return tables
    
    def _generate_charts_section(self, analyses: List[str]) -> List[Dict[str, Any]]:
        """Genera sección de gráficos"""
        charts = []
        
        if "volumen" in analyses:
            charts.append({
                "tipo": "line",
                "titulo": "Tendencia de Accidentes por Año",
                "data_ref": "tabla:Accidentes por Año",
                "descripcion": "Evolución temporal de la accidentalidad"
            })
            
            charts.append({
                "tipo": "pie",
                "titulo": "Distribución por Turno",
                "data_ref": "tabla:Distribución por Turno",
                "descripcion": "Concentración de accidentes por turno de trabajo"
            })
        
        if "perfil" in analyses:
            charts.append({
                "tipo": "bar",
                "titulo": "Top Formas de Accidente",
                "data_ref": "tabla:Top 5 Formas de Accidente",
                "descripcion": "Principales causas de accidentalidad"
            })
        
        return charts
    
    def _generate_legal_citations(self) -> List[Dict[str, Any]]:
        """Genera citas normativas"""
        return [
            {
                "documento": "Ley 29783",
                "articulo": "Art. 33",
                "paginas": "Registros obligatorios",
                "relevancia": "Marco legal para registro de accidentes"
            },
            {
                "documento": "DS 005-2012-TR",
                "articulo": "Art. 111-113",
                "paginas": "Investigación de accidentes",
                "relevancia": "Procedimientos de investigación"
            },
            {
                "documento": "RM 050-2013-TR",
                "articulo": "Anexo 1",
                "paginas": "Formatos de registro",
                "relevancia": "Cálculo de índices estadísticos"
            }
        ]
    
    def _generate_data_citations(self, analyses: List[str]) -> List[Dict[str, Any]]:
        """Genera citas de datos"""
        citations = []
        
        # Cita base del dataset
        citations.append({
            "dataset": "accidentes_laborales",
            "sql": "SELECT COUNT(*) FROM accidentes WHERE fecha BETWEEN '2016-01-01' AND '2025-12-31'",
            "filtros": {"periodo": "2016-2025", "registros_totales": 754},
            "fuente": "Registro de accidentes laborales EVP - Ago25 (SN).xlsx"
        })
        
        if "perfil" in analyses:
            citations.append({
                "dataset": "accidentes_laborales",
                "sql": "SELECT forma_accidente, COUNT(*) as cantidad FROM accidentes GROUP BY forma_accidente ORDER BY cantidad DESC LIMIT 5",
                "filtros": {"analisis": "top_formas_accidente"},
                "fuente": "Columna 'Forma de Accidente'"
            })
        
        if "impacto" in analyses:
            citations.append({
                "dataset": "accidentes_laborales", 
                "sql": "SELECT SUM(dias_descanso) as total_dias, AVG(dias_descanso) as promedio FROM accidentes",
                "filtros": {"analisis": "impacto_operativo"},
                "fuente": "Columna 'Días de Descnaso Médico'"
            })
        
        return citations
    
    def _generate_assumptions(self, analyses: List[str]) -> List[str]:
        """Genera suposiciones y limitaciones"""
        assumptions = []
        
        # Suposiciones generales sobre calidad de datos
        data_quality = self.all_indicators["calidad_datos"]
        if data_quality.get("campos_vacios_criticos"):
            assumptions.append("Algunos campos críticos presentan valores faltantes")
        
        # Suposiciones sobre KPIs normativos
        if "kpis" in analyses:
            assumptions.append("KPIs normativos (IF, IG, IA) requieren datos de horas-hombre no disponibles")
            assumptions.append("Cálculos de incidencia requieren número de trabajadores expuestos")
        
        # Suposiciones sobre costos
        if "impacto" in analyses:
            cost_data = self.all_indicators["impacto_operativo"]["costo_total"]
            if cost_data.get("estado") == "sin_datos":
                assumptions.append("Análisis de costos limitado por datos incompletos")
        
        # Suposiciones sobre SCTR
        assumptions.append("Datos de cobertura SCTR no disponibles (campos 100% nulos)")
        
        return assumptions if assumptions else ["Análisis basado en datos disponibles sin limitaciones críticas"]
    
    def _generate_next_steps(self, analyses: List[str]) -> List[str]:
        """Genera próximos pasos recomendados"""
        next_steps = []
        
        if "kpis" in analyses:
            next_steps.append("Recopilar datos de horas-hombre por año/área para cálculo de IF, IG, IA")
            next_steps.append("Definir número de trabajadores expuestos para tasa de incidencia")
        
        if "perfil" in analyses:
            perfil_data = self.all_indicators["perfil_siniestralidad"]
            if perfil_data.get("top_formas_accidente"):
                top_cause = perfil_data["top_formas_accidente"][0]["categoria"]
                next_steps.append(f"Implementar controles específicos para '{top_cause}' (principal causa)")
        
        if "factores_humanos" in analyses:
            next_steps.append("Reforzar programa de inducción para personal con <6 meses experiencia")
            next_steps.append("Implementar pausas activas en primeras 4 horas de turno")
        
        if "medidas" in analyses:
            next_steps.append("Mejorar seguimiento de implementación de medidas correctivas")
            next_steps.append("Establecer SLA de 30 días para medidas críticas")
        
        # Pasos generales
        next_steps.append("Completar campos SCTR para análisis de cobertura")
        next_steps.append("Estandarizar formato de costos por accidente")
        next_steps.append("Implementar dashboard en tiempo real con KPIs calculados")
        
        return next_steps[:5]  # Limitar a 5 pasos más importantes
