#!/usr/bin/env python3
"""
SSO Accident Analytics Engine
Sistema de análisis predictivo para accidentes laborales
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, mean_squared_error
import joblib
import os
import warnings
warnings.filterwarnings('ignore')

class AccidentAnalytics:
    """Motor de análisis predictivo para accidentes laborales"""
    
    def __init__(self, excel_path='docs/Registro de accidentes laborales EVP - Ago25 (SN).xlsx'):
        self.excel_path = excel_path
        self.df = None
        self.risk_model = None
        self.severity_model = None
        self.label_encoders = {}
        self.scaler = StandardScaler()
        self.risk_factors = {}

    def get_data_dictionary(self):
        """Genera un diccionario de datos del archivo Excel."""
        if self.df is None:
            if not self.load_and_process_data():
                return {"error": "No se pudo cargar el archivo de datos."}

        data_dictionary = {}
        for col in self.df.columns:
            data_dictionary[col] = {
                'dtype': str(self.df[col].dtype),
                'unique_values': self.df[col].nunique(),
                'missing_values': int(self.df[col].isnull().sum()),
                'missing_percentage': f"{self.df[col].isnull().sum() / len(self.df) * 100:.2f}%",
                'sample': [str(x) for x in self.df[col].dropna().head(3).tolist()]
            }
        return data_dictionary
        
    def load_and_process_data(self):
        """Cargar y procesar datos de accidentes"""
        try:
            if not os.path.exists(self.excel_path):
                print(f"❌ Archivo no encontrado: {self.excel_path}")
                return False
                
            # Leer archivo Excel
            self.df = pd.read_excel(self.excel_path)
            print(f"✅ Datos cargados: {len(self.df)} registros")
            
            # Procesar datos
            self._clean_and_prepare_data()
            self._extract_features()
            
            return True
            
        except Exception as e:
            print(f"❌ Error cargando datos: {e}")
            return False
    
    def _clean_and_prepare_data(self):
        """Limpiar y preparar datos"""
        # Convertir fechas
        date_columns = [col for col in self.df.columns if 'fecha' in col.lower() or 'date' in col.lower()]
        for col in date_columns:
            try:
                self.df[col] = pd.to_datetime(self.df[col], errors='coerce')
            except:
                pass
        
        # Limpiar valores nulos
        self.df = self.df.dropna(subset=self.df.select_dtypes(include=[np.number]).columns, how='all')
        
        # Normalizar texto
        text_columns = self.df.select_dtypes(include=['object']).columns
        for col in text_columns:
            if self.df[col].dtype == 'object':
                self.df[col] = self.df[col].astype(str).str.upper()
                self.df[col] = self.df[col].str.replace(r'[^\w\s]', '', regex=True)
                self.df[col] = self.df[col].str.replace(r'\s+', ' ', regex=True).str.strip()
    
    def _extract_features(self):
        """Extraer características para el modelo"""
        # Crear características temporales
        if 'FECHA' in self.df.columns or any('fecha' in col.lower() for col in self.df.columns):
            date_col = next((col for col in self.df.columns if 'fecha' in col.lower()), None)
            if date_col and pd.api.types.is_datetime64_any_dtype(self.df[date_col]):
                self.df['mes'] = self.df[date_col].dt.month
                self.df['dia_semana'] = self.df[date_col].dt.dayofweek
                self.df['trimestre'] = self.df[date_col].dt.quarter
        
        # Extracción de palabras clave de la descripción
        description_col = next((col for col in self.df.columns if 'descripción' in col.lower() or 'descripcion' in col.lower()), None)
        if description_col:
            keywords = [
                'CAIDA', 'GOLPE', 'CORTE', 'QUEMADURA', 'ATRAPAMIENTO', 
                'CONTACTO ELECTRICO', 'EXPOSICION', 'SOBREESFUERZO', 'INHALACION',
                'PROYECCION', 'DERRUMBE', 'ATROPELLO'
            ]
            for keyword in keywords:
                self.df[f'keyword_{keyword.replace(" ", "_").lower()}'] = self.df[description_col].str.contains(keyword, case=False, na=False).astype(int)

        # Codificar variables categóricas
        categorical_columns = self.df.select_dtypes(include=['object']).columns
        for col in categorical_columns:
            if col not in self.label_encoders:
                self.label_encoders[col] = LabelEncoder()
                self.df[f'{col}_encoded'] = self.label_encoders[col].fit_transform(self.df[col].fillna('UNKNOWN'))
    
    def analyze_risk_patterns(self):
        """Analizar patrones de riesgo de forma dinámica."""
        if self.df is None:
            return {}

        analysis = {
            'total_accidents': len(self.df),
            'risk_by_time': {},
            'trends': {}
        }

        # Dimensiones a analizar y sus posibles nombres de columna
        analysis_dimensions = {
            'risk_by_area': ['area'],
            'risk_by_sector': ['sector'],
            'risk_by_position': ['puesto', 'cargo'],
            'risk_by_shift': ['turno'],
            'risk_by_cause': ['causa'],
            'risk_by_body_part': ['parte del cuerpo', 'parte afectada'],
            'risk_by_injury_nature': ['naturaleza de lesion', 'tipo de lesion'],
            'risk_by_agent': ['agente causante'],
            'risk_by_activity': ['actividad', 'tarea'],
            'severity_distribution': ['gravedad', 'severity', 'consecuencia']
        }

        for key, potential_cols in analysis_dimensions.items():
            col_to_analyze = next((col for col in self.df.columns if any(p_col in col.lower() for p_col in potential_cols)), None)
            if col_to_analyze:
                counts = self.df[col_to_analyze].value_counts()
                analysis[key] = counts.to_dict()

        # Análisis temporal
        if 'mes' in self.df.columns:
            month_counts = self.df['mes'].value_counts().sort_index()
            analysis['risk_by_time']['monthly'] = {str(k): v for k, v in month_counts.items()}
        
        if 'dia_semana' in self.df.columns:
            day_counts = self.df['dia_semana'].value_counts().sort_index()
            days = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
            analysis['risk_by_time']['weekly'] = {days[k]: v for k, v in day_counts.items() if k < 7}
        
        return analysis

    def get_key_indicators(self, analysis_results):
        """Extrae y formatea los indicadores clave para el LLM."""
        indicators = {}

        # 1. Meses de mayor incidencia
        if 'risk_by_time' in analysis_results and 'monthly' in analysis_results['risk_by_time']:
            top_months = sorted(analysis_results['risk_by_time']['monthly'].items(), key=lambda x: x[1], reverse=True)[:3]
            indicators['top_months'] = {m: c for m, c in top_months}

        # 2. Áreas críticas
        if 'risk_by_area' in analysis_results:
            top_areas = sorted(analysis_results['risk_by_area'].items(), key=lambda x: x[1], reverse=True)[:3]
            indicators['critical_areas'] = {a: c for a, c in top_areas}

        # 3. Causas frecuentes
        if 'risk_by_cause' in analysis_results:
            top_causes = sorted(analysis_results['risk_by_cause'].items(), key=lambda x: x[1], reverse=True)[:3]
            indicators['frequent_causes'] = {ca: co for ca, co in top_causes}

        # 4. Severidad
        if 'severity_distribution' in analysis_results:
            indicators['severity_distribution'] = analysis_results['severity_distribution']

        return indicators
    
    def train_predictive_models(self):
        """Entrenar modelos predictivos"""
        if self.df is None or len(self.df) < 10:
            print("❌ Datos insuficientes para entrenar modelos")
            return False
        
        try:
            # Preparar características
            feature_columns = [col for col in self.df.columns if col.endswith('_encoded') or col in ['mes', 'dia_semana', 'trimestre']]
            
            if len(feature_columns) < 2:
                print("❌ Características insuficientes para el modelo")
                return False
            
            X = self.df[feature_columns].fillna(0)
            
            # Modelo de predicción de riesgo (clasificación binaria)
            # Crear variable objetivo basada en frecuencia de accidentes
            if 'mes' in self.df.columns:
                monthly_accidents = self.df.groupby('mes').size()
                high_risk_months = monthly_accidents[monthly_accidents > monthly_accidents.median()].index
                y_risk = self.df['mes'].isin(high_risk_months).astype(int)
                
                if len(np.unique(y_risk)) > 1:
                    X_train, X_test, y_train, y_test = train_test_split(X, y_risk, test_size=0.3, random_state=42)
                    
                    self.risk_model = RandomForestClassifier(n_estimators=100, random_state=42)
                    self.risk_model.fit(X_train, y_train)
                    
                    # Evaluar modelo
                    y_pred = self.risk_model.predict(X_test)
                    print("✅ Modelo de riesgo entrenado")
            
            return True
            
        except Exception as e:
            print(f"❌ Error entrenando modelos: {e}")
            return False
    
    def predict_risk_level(self, area=None, month=None, day_of_week=None):
        """Predecir nivel de riesgo"""
        if self.risk_model is None:
            return {"risk_level": "MEDIUM", "confidence": 0.5, "message": "Modelo no disponible"}
        
        try:
            # Crear vector de características
            features = np.zeros(len(self.risk_model.feature_names_in_))
            
            # Mapear características si están disponibles
            if month is not None and 'mes' in self.risk_model.feature_names_in_:
                idx = list(self.risk_model.feature_names_in_).index('mes')
                features[idx] = month
            
            if day_of_week is not None and 'dia_semana' in self.risk_model.feature_names_in_:
                idx = list(self.risk_model.feature_names_in_).index('dia_semana')
                features[idx] = day_of_week
            
            # Predecir
            risk_prob = self.risk_model.predict_proba([features])[0]
            risk_level = "HIGH" if risk_prob[1] > 0.6 else "MEDIUM" if risk_prob[1] > 0.3 else "LOW"
            
            return {
                "risk_level": risk_level,
                "confidence": float(max(risk_prob)),
                "probability_high_risk": float(risk_prob[1]),
                "message": f"Nivel de riesgo {risk_level.lower()} con {max(risk_prob)*100:.1f}% de confianza"
            }
            
        except Exception as e:
            return {"risk_level": "MEDIUM", "confidence": 0.5, "message": f"Error en predicción: {e}"}
    
    def generate_recommendations(self, analysis_results, risk_prediction=None):
        """Generar recomendaciones basadas en datos"""
        recommendations = {
            "immediate_actions": [],
            "preventive_measures": [],
            "monitoring_priorities": [],
            "training_needs": []
        }
        
        # Recomendaciones basadas en áreas de alto riesgo
        if 'risk_by_area' in analysis_results and analysis_results['risk_by_area']:
            high_risk_areas = sorted(analysis_results['risk_by_area'].items(), key=lambda x: x[1], reverse=True)[:3]
            
            for area, count in high_risk_areas:
                recommendations["immediate_actions"].append(
                    f"Inspección prioritaria en {area} ({count} incidentes registrados)"
                )
                recommendations["preventive_measures"].append(
                    f"Implementar controles adicionales de seguridad en {area}"
                )
        
        # Recomendaciones temporales
        if 'risk_by_time' in analysis_results:
            if 'monthly' in analysis_results['risk_by_time']:
                monthly_data = analysis_results['risk_by_time']['monthly']
                high_risk_months = [month for month, count in monthly_data.items() if count > np.mean(list(monthly_data.values()))]
                
                if high_risk_months:
                    recommendations["monitoring_priorities"].append(
                        f"Reforzar vigilancia durante los meses: {', '.join(map(str, high_risk_months))}"
                    )
            
            if 'weekly' in analysis_results['risk_by_time']:
                weekly_data = analysis_results['risk_by_time']['weekly']
                high_risk_days = [day for day, count in weekly_data.items() if count > np.mean(list(weekly_data.values()))]
                
                if high_risk_days:
                    recommendations["preventive_measures"].append(
                        f"Implementar briefings de seguridad adicionales los días: {', '.join(high_risk_days)}"
                    )
        
        # Recomendaciones de capacitación
        recommendations["training_needs"].extend([
            "Capacitación en identificación de peligros y evaluación de riesgos",
            "Entrenamiento en uso correcto de EPP",
            "Simulacros de emergencia y respuesta a incidentes",
            "Programa de liderazgo en seguridad para supervisores"
        ])
        
        return recommendations
    
    def get_comprehensive_analysis(self):
        """Obtener análisis completo del sistema"""
        if not self.load_and_process_data():
            return None
        
        # Análisis de patrones
        patterns = self.analyze_risk_patterns()
        
        # Entrenar modelos
        self.train_predictive_models()
        
        # Predicción actual
        current_month = datetime.now().month
        current_day = datetime.now().weekday()
        risk_prediction = self.predict_risk_level(month=current_month, day_of_week=current_day)
        
        # Generar recomendaciones
        recommendations = self.generate_recommendations(patterns, risk_prediction)

        # Obtener indicadores clave
        key_indicators = self.get_key_indicators(patterns)
        
        return {
            "data_summary": {
                "total_records": len(self.df),
                "date_range": self._get_date_range(),
                "data_quality": self._assess_data_quality()
            },
            "key_indicators": key_indicators,
            "risk_analysis": patterns,
            "current_prediction": risk_prediction,
            "recommendations": recommendations,
            "model_status": {
                "risk_model_trained": self.risk_model is not None,
                "features_available": len([col for col in self.df.columns if col.endswith('_encoded')]) if self.df is not None else 0
            }
        }
    
    def _get_date_range(self):
        """Obtener rango de fechas de los datos"""
        date_columns = [col for col in self.df.columns if pd.api.types.is_datetime64_any_dtype(self.df[col])]
        if date_columns:
            date_col = date_columns[0]
            return {
                "start": str(self.df[date_col].min().date()) if pd.notna(self.df[date_col].min()) else "N/A",
                "end": str(self.df[date_col].max().date()) if pd.notna(self.df[date_col].max()) else "N/A"
            }
        return {"start": "N/A", "end": "N/A"}
    
    def _assess_data_quality(self):
        """Evaluar calidad de los datos"""
        if self.df is None:
            return "Poor"

        completeness = (1 - self.df.isnull().sum().sum() / (len(self.df) * len(self.df.columns))) * 100

        if completeness > 80:
            return "Excellent"
        elif completeness > 60:
            return "Good"
        elif completeness > 40:
            return "Fair"
        else:
            return "Poor"

    def predict_future_incidents(self, days_ahead=30):
        """Predecir incidentes futuros"""
        if self.df is None or len(self.df) < 10:
            return {"prediction": "Datos insuficientes", "confidence": 0}

        try:
            # Análisis de tendencias temporales
            if 'mes' in self.df.columns:
                monthly_counts = self.df.groupby('mes').size()
                current_month = datetime.now().month

                # Predicción simple basada en promedio histórico
                avg_monthly = monthly_counts.mean()
                current_month_data = monthly_counts.get(current_month, avg_monthly)

                # Factor de estacionalidad
                seasonality_factor = current_month_data / avg_monthly if avg_monthly > 0 else 1

                # Predicción para los próximos días
                daily_rate = avg_monthly / 30  # Aproximación diaria
                predicted_incidents = daily_rate * days_ahead * seasonality_factor

                return {
                    "predicted_incidents": round(predicted_incidents, 1),
                    "confidence": min(0.8, len(self.df) / 100),  # Confianza basada en cantidad de datos
                    "daily_rate": round(daily_rate, 2),
                    "seasonality_factor": round(seasonality_factor, 2)
                }
        except Exception as e:
            return {"prediction": f"Error en predicción: {e}", "confidence": 0}

    def get_risk_factors_ranking(self):
        """Obtener ranking de factores de riesgo"""
        if self.df is None:
            return {}

        risk_factors = {}

        # Analizar factores categóricos
        categorical_columns = self.df.select_dtypes(include=['object']).columns
        for col in categorical_columns:
            if col.lower() in ['area', 'departamento', 'tipo', 'causa', 'actividad']:
                value_counts = self.df[col].value_counts()
                risk_factors[col] = {
                    "top_risks": value_counts.head(5).to_dict(),
                    "total_categories": len(value_counts)
                }

        return risk_factors

    def generate_executive_summary(self):
        """Generar resumen ejecutivo"""
        if not self.analytics_data:
            return "No hay datos disponibles para generar resumen ejecutivo"

        summary = f"""
        <h3>📊 Resumen Ejecutivo - Análisis de Seguridad</h3>

        <h4>🔍 Estado Actual</h4>
        <ul>
            <li><strong>Total de incidentes registrados:</strong> {self.analytics_data['data_summary']['total_records']}</li>
            <li><strong>Calidad de datos:</strong> {self.analytics_data['data_summary']['data_quality']}</li>
            <li><strong>Nivel de riesgo actual:</strong> {self.analytics_data['current_prediction']['risk_level']}</li>
            <li><strong>Confianza del modelo:</strong> {self.analytics_data['current_prediction']['confidence']:.1%}</li>
        </ul>

        <h4>⚠️ Áreas Críticas</h4>
        <ul>
        """

        # Agregar áreas de riesgo
        if 'risk_by_area' in self.analytics_data['risk_analysis']:
            top_areas = sorted(self.analytics_data['risk_analysis']['risk_by_area'].items(),
                             key=lambda x: x[1], reverse=True)[:3]
            for area, count in top_areas:
                summary += f"<li><strong>{area}:</strong> {count} incidentes</li>"

        summary += """
        </ul>

        <h4>🎯 Acciones Prioritarias</h4>
        <ol>
        """

        # Agregar recomendaciones
        for action in self.analytics_data['recommendations']['immediate_actions'][:3]:
            summary += f"<li>{action}</li>"

        summary += """
        </ol>

        <h4>📈 Indicadores Clave</h4>
        <table>
            <tr><th>Métrica</th><th>Valor</th><th>Estado</th></tr>
        """

        # Agregar métricas
        total_incidents = self.analytics_data['data_summary']['total_records']
        risk_level = self.analytics_data['current_prediction']['risk_level']

        summary += f"""
            <tr><td>Total de Incidentes</td><td>{total_incidents}</td><td>{'🔴 Alto' if total_incidents > 50 else '🟡 Medio' if total_incidents > 20 else '🟢 Bajo'}</td></tr>
            <tr><td>Riesgo Actual</td><td>{risk_level}</td><td>{'🔴' if risk_level == 'HIGH' else '🟡' if risk_level == 'MEDIUM' else '🟢'}</td></tr>
            <tr><td>Modelo Predictivo</td><td>{'Activo' if self.analytics_data['model_status']['risk_model_trained'] else 'Inactivo'}</td><td>{'🟢' if self.analytics_data['model_status']['risk_model_trained'] else '🔴'}</td></tr>
        </table>
        """

        return summary

    def generate_dynamic_executive_summary(self, analysis_results):
        """Genera un resumen ejecutivo dinámico y detallado."""
        summary = "<h3>📊 Resumen Ejecutivo Dinámico</h3>"

        # Dimensiones clave y sus títulos para el resumen
        key_dimensions = {
            'risk_by_area': 'Áreas de Mayor Riesgo',
            'risk_by_position': 'Puestos con Mayor Incidencia',
            'risk_by_cause': 'Causas Principales de Accidentes',
            'risk_by_shift': 'Turnos Críticos',
            'risk_by_body_part': 'Partes del Cuerpo Más Afectadas',
            'severity_distribution': 'Distribución de Severidad'
        }

        for key, title in key_dimensions.items():
            if key in analysis_results and analysis_results[key]:
                summary += f"<h4>{title}</h4><ul>"
                top_items = sorted(analysis_results[key].items(), key=lambda x: x[1], reverse=True)[:3]
                for item, count in top_items:
                    summary += f"<li><strong>{item}:</strong> {count} incidentes</li>"
                summary += "</ul>"
        
        return summary
