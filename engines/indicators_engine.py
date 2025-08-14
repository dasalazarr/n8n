#!/usr/bin/env python3
"""
SSO Indicators Engine - Motor de Indicadores Estandarizados
Calcula todos los indicadores definidos en el análisis del usuario
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import json

class IndicatorsEngine:
    """Motor de cálculo de indicadores SSO estandarizados"""
    
    def __init__(self, df: pd.DataFrame, denominators_table: Optional[pd.DataFrame] = None):
        self.df = df
        self.denominators = denominators_table
        self.indicators = {}
        
    def calculate_all_indicators(self) -> Dict[str, Any]:
        """Calcula todos los indicadores disponibles"""
        return {
            "volumen_tendencia": self._calculate_volume_trends(),
            "perfil_siniestralidad": self._calculate_accident_profile(),
            "impacto_operativo": self._calculate_operational_impact(),
            "factores_humanos": self._calculate_human_factors(),
            "efectividad_medidas": self._calculate_measures_effectiveness(),
            "kpis_normativos": self._calculate_regulatory_kpis(),
            "indicadores_avanzados": self._calculate_advanced_indicators(),
            "calidad_datos": self._assess_data_quality()
        }
    
    def _calculate_volume_trends(self) -> Dict[str, Any]:
        """1.1 Volumen y tendencia"""
        fecha_col = self._find_date_column()
        if fecha_col:
            self.df['fecha_parsed'] = pd.to_datetime(self.df[fecha_col], errors='coerce')
            self.df['año'] = self.df['fecha_parsed'].dt.year
            self.df['mes'] = self.df['fecha_parsed'].dt.month
        
        return {
            "accidentes_por_año": self.df.groupby('año').size().to_dict() if 'año' in self.df.columns else {},
            "accidentes_por_mes": self.df.groupby('mes').size().to_dict() if 'mes' in self.df.columns else {},
            "temporada_picos": self._identify_seasonal_peaks(),
            "distribucion_turno": self._calculate_shift_distribution(),
            "tasa_cambio_interanual": self._calculate_year_over_year_change()
        }
    
    def _calculate_accident_profile(self) -> Dict[str, Any]:
        """1.2 Perfil de siniestralidad"""
        return {
            "top_formas_accidente": self._get_top_n('Forma de Accidente', 5),
            "top_agentes_causantes": self._get_top_n('Agente Causante', 5),
            "top_partes_cuerpo": self._get_top_n('Parte del cuerpo afectada', 5),
            "distribucion_severidad": self._calculate_severity_distribution(),
            "dias_perdidos_severidad": self._calculate_lost_days_by_severity()
        }
    
    def _calculate_operational_impact(self) -> Dict[str, Any]:
        """1.3 Impacto operativo y económico"""
        dias_col = 'Días de Descnaso Médico'
        
        return {
            "dias_descanso_total": int(self.df[dias_col].sum()) if dias_col in self.df.columns else 0,
            "dias_promedio_accidente": float(self.df[dias_col].mean()) if dias_col in self.df.columns else 0,
            "dias_por_año": self.df.groupby('año')[dias_col].sum().to_dict() if all(col in self.df.columns for col in ['año', dias_col]) else {},
            "costo_total": self._calculate_total_costs(),
            "costo_medio_severidad": self._calculate_cost_by_severity()
        }
    
    def _calculate_regulatory_kpis(self) -> Dict[str, Any]:
        """2.1 KPIs normativos (RM 050-2013)"""
        if self.denominators is not None:
            return self._calculate_if_ig_ia()
        else:
            return {
                "IF": {
                    "nombre": "Índice de Frecuencia",
                    "valor": None,
                    "estado": "needs_input",
                    "formula": "Accidentes incapacitantes × 1,000,000 / Horas-hombre",
                    "requerimiento": "Tabla de horas-hombre por año/área"
                },
                "IG": {
                    "nombre": "Índice de Gravedad", 
                    "valor": None,
                    "estado": "needs_input",
                    "formula": "Días perdidos × 1,000,000 / Horas-hombre",
                    "requerimiento": "Tabla de horas-hombre por año/área"
                },
                "IA": {
                    "nombre": "Índice de Accidentabilidad",
                    "valor": None,
                    "estado": "needs_input", 
                    "formula": "(IF × IG) / 1,000",
                    "requerimiento": "Cálculo de IF e IG previo"
                }
            }
    
    # Métodos auxiliares principales
    def _find_date_column(self) -> Optional[str]:
        """Encuentra la columna de fecha principal"""
        date_candidates = ['Fecha', 'FECHA', 'fecha']
        for col in self.df.columns:
            if any(candidate in col for candidate in date_candidates):
                return col
        return None
    
    def _get_top_n(self, column: str, n: int = 5) -> List[Dict[str, Any]]:
        """Obtiene top N de una columna"""
        if column not in self.df.columns:
            return []
        
        top_values = self.df[column].value_counts().head(n)
        return [
            {"categoria": str(idx), "cantidad": int(val), "porcentaje": round(val/len(self.df)*100, 1)}
            for idx, val in top_values.items()
        ]
    
    def _calculate_shift_distribution(self) -> Dict[str, Any]:
        """Calcula distribución por turno"""
        turno_col = 'Turno'
        if turno_col not in self.df.columns:
            return {}
        
        distribution = self.df[turno_col].value_counts()
        total = len(self.df)
        
        return {
            "distribucion": [
                {"turno": str(turno), "cantidad": int(count), "porcentaje": round(count/total*100, 1)}
                for turno, count in distribution.items()
            ]
        }
    
    def _identify_seasonal_peaks(self):
        """Identifica picos estacionales en los accidentes"""
        if self.df is None or self.df.empty:
            return {}
        
        fecha_col = self._find_date_column()
        if not fecha_col:
            return {}
        
        try:
            # Agrupar por mes
            monthly_counts = self.df.groupby(self.df[fecha_col].dt.month).size()
            peak_month = monthly_counts.idxmax()
            peak_count = monthly_counts.max()
            
            months = {1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril", 5: "Mayo", 6: "Junio",
                     7: "Julio", 8: "Agosto", 9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"}
            
            return {
                "mes_pico": months.get(peak_month, "Desconocido"),
                "cantidad_pico": int(peak_count),
                "distribucion_mensual": monthly_counts.to_dict()
            }
        except:
            return {}
    
    def _calculate_shift_distribution(self):
        """Calcula distribución por turno"""
        if self.df is None or self.df.empty:
            return {}
        
        turno_cols = ['Turno', 'turno', 'TURNO', 'Hora']
        turno_col = None
        
        for col in turno_cols:
            if col in self.df.columns:
                turno_col = col
                break
        
        if turno_col:
            return self.df[turno_col].value_counts().to_dict()
        return {}
    
    def _calculate_year_over_year_change(self):
        """Calcula cambio interanual"""
        if self.df is None or self.df.empty:
            return {}
        
        fecha_col = self._find_date_column()
        if not fecha_col:
            return {}
        
        try:
            yearly_counts = self.df.groupby(self.df[fecha_col].dt.year).size()
            if len(yearly_counts) < 2:
                return {"cambio_porcentual": 0, "tendencia": "Datos insuficientes"}
            
            current_year = yearly_counts.index[-1]
            previous_year = yearly_counts.index[-2]
            
            change = ((yearly_counts[current_year] - yearly_counts[previous_year]) / yearly_counts[previous_year]) * 100
            
            return {
                "cambio_porcentual": round(change, 2),
                "tendencia": "Aumento" if change > 0 else "Disminución",
                "año_actual": int(current_year),
                "año_anterior": int(previous_year)
            }
        except:
            return {}
    
    def _calculate_severity_distribution(self):
        """Calcula distribución por severidad"""
        if self.df is None or self.df.empty:
            return {}
        
        severity_cols = ['Severidad', 'severidad', 'SEVERIDAD', 'Tipo de Lesión', 'Grado de Lesión']
        severity_col = None
        
        for col in severity_cols:
            if col in self.df.columns:
                severity_col = col
                break
        
        if severity_col:
            return self.df[severity_col].value_counts().to_dict()
        return {}
    
    def _calculate_lost_days_by_severity(self):
        """Calcula días perdidos por severidad"""
        if self.df is None or self.df.empty:
            return {}
        
        severity_cols = ['Severidad', 'severidad', 'SEVERIDAD', 'Tipo de Lesión']
        days_cols = ['Días de Descanso Médico', 'dias_perdidos', 'DIAS_PERDIDOS', 'Días Perdidos']
        
        severity_col = None
        days_col = None
        
        for col in severity_cols:
            if col in self.df.columns:
                severity_col = col
                break
        
        for col in days_cols:
            if col in self.df.columns:
                days_col = col
                break
        
        if severity_col and days_col:
            try:
                return self.df.groupby(severity_col)[days_col].sum().to_dict()
            except:
                return {}
        return {}
    
    def _calculate_total_costs(self):
        """Calcula costos totales estimados"""
        if self.df is None or self.df.empty:
            return 0
        
        # Estimación básica basada en días perdidos
        days_cols = ['Días de Descanso Médico', 'dias_perdidos', 'DIAS_PERDIDOS', 'Días Perdidos']
        days_col = None
        
        for col in days_cols:
            if col in self.df.columns:
                days_col = col
                break
        
        if days_col:
            try:
                total_days = self.df[days_col].sum()
                # Estimación: $100 USD por día perdido (ajustable)
                return total_days * 100
            except:
                return 0
        return 0
    
    def _calculate_cost_by_severity(self):
        """Calcula costo medio por severidad"""
        if self.df is None or self.df.empty:
            return {}
        
        severity_cols = ['Severidad', 'severidad', 'SEVERIDAD', 'Tipo de Lesión']
        days_cols = ['Días de Descanso Médico', 'dias_perdidos', 'DIAS_PERDIDOS', 'Días Perdidos']
        
        severity_col = None
        days_col = None
        
        for col in severity_cols:
            if col in self.df.columns:
                severity_col = col
                break
        
        for col in days_cols:
            if col in self.df.columns:
                days_col = col
                break
        
        if severity_col and days_col:
            try:
                avg_days = self.df.groupby(severity_col)[days_col].mean()
                return (avg_days * 100).to_dict()  # $100 por día
            except:
                return {}
        return {}
    
    def _calculate_human_factors(self):
        """Calcula factores humanos relacionados con accidentes"""
        if self.df is None or self.df.empty:
            return {}
        
        # Buscar columnas relacionadas con factores humanos
        age_cols = ['Edad', 'edad', 'EDAD', 'Age']
        experience_cols = ['Experiencia', 'experiencia', 'EXPERIENCIA', 'Antigüedad', 'antiguedad']
        time_cols = ['Hora', 'hora', 'HORA', 'Tiempo en el puesto']
        
        result = {}
        
        # Análisis por edad
        for col in age_cols:
            if col in self.df.columns:
                try:
                    age_stats = self.df[col].describe()
                    result['edad_promedio'] = round(age_stats['mean'], 1)
                    result['edad_mediana'] = round(age_stats['50%'], 1)
                    break
                except:
                    pass
        
        # Análisis por experiencia
        for col in experience_cols:
            if col in self.df.columns:
                try:
                    exp_stats = self.df[col].describe()
                    result['experiencia_promedio'] = round(exp_stats['mean'], 1)
                    result['experiencia_mediana'] = round(exp_stats['50%'], 1)
                    break
                except:
                    pass
        
        # Análisis por hora del día
        for col in time_cols:
            if col in self.df.columns:
                try:
                    time_dist = self.df[col].value_counts().head(5)
                    result['horas_criticas'] = time_dist.to_dict()
                    break
                except:
                    pass
        
        return result
    
    def _calculate_measures_effectiveness(self):
        """Calcula efectividad de medidas preventivas"""
        if self.df is None or self.df.empty:
            return {}
        
        # Buscar columnas relacionadas con medidas
        measures_cols = ['Medidas Adoptadas', 'medidas', 'MEDIDAS', 'Acción Correctiva', 'Prevención']
        status_cols = ['Estado', 'estado', 'ESTADO', 'Status', 'Cumplimiento']
        
        result = {}
        
        # Análisis de medidas adoptadas
        for col in measures_cols:
            if col in self.df.columns:
                try:
                    measures_count = self.df[col].value_counts()
                    result['medidas_frecuentes'] = measures_count.head(5).to_dict()
                    result['total_medidas'] = len(measures_count)
                    break
                except:
                    pass
        
        # Análisis de cumplimiento
        for col in status_cols:
            if col in self.df.columns:
                try:
                    status_dist = self.df[col].value_counts()
                    result['distribucion_cumplimiento'] = status_dist.to_dict()
                    break
                except:
                    pass
        
        return result
    
    def _calculate_advanced_indicators(self):
        """Calcula indicadores avanzados"""
        if self.df is None or self.df.empty:
            return {}
        
        result = {}
        
        # Análisis de recurrencia
        area_cols = ['Área', 'area', 'AREA', 'Departamento', 'Sección']
        for col in area_cols:
            if col in self.df.columns:
                try:
                    area_counts = self.df[col].value_counts()
                    result['areas_recurrentes'] = area_counts.head(3).to_dict()
                    break
                except:
                    pass
        
        # Análisis de gravedad esperada
        severity_cols = ['Severidad', 'severidad', 'SEVERIDAD', 'Tipo de Lesión']
        for col in severity_cols:
            if col in self.df.columns:
                try:
                    severity_counts = self.df[col].value_counts()
                    total = len(self.df)
                    result['indice_gravedad'] = {
                        sev: round(count/total*100, 2) 
                        for sev, count in severity_counts.items()
                    }
                    break
                except:
                    pass
        
        # Hotspots de riesgo
        if 'areas_recurrentes' in result:
            result['hotspots'] = list(result['areas_recurrentes'].keys())[:3]
        
        return result
    
    def _calculate_if_ig_ia(self):
        """Calcula índices normativos IF, IG, IA"""
        # Estos requieren datos de horas-hombre y trabajadores expuestos
        # que no están disponibles en el Excel actual
        return {
            "IF": {"valor": None, "estado": "needs_input", "descripcion": "Requiere horas-hombre trabajadas"},
            "IG": {"valor": None, "estado": "needs_input", "descripcion": "Requiere días perdidos y horas-hombre"},
            "IA": {"valor": None, "estado": "needs_input", "descripcion": "Requiere días perdidos y trabajadores expuestos"},
            "nota": "Para calcular estos KPIs normativos se necesita agregar datos de horas-hombre y número de trabajadores expuestos"
        }
    
    def _assess_data_quality(self):
        """Evalúa la calidad de los datos - versión mínima"""
        if self.df is None or self.df.empty:
            return {"completitud": 0, "total_registros": 0}
        
        missing_ratio = self.df.isnull().sum().sum() / (len(self.df) * len(self.df.columns))
        return {
            "completitud": round((1 - missing_ratio) * 100, 2),
            "total_registros": len(self.df),
            "campos_principales": len(self.df.columns)
        }
