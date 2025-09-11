#!/usr/bin/env python3
"""Test script para verificar detección de atrapamientos"""

import pandas as pd
from engines.indicators_engine import IndicatorsEngine
from engines.response_builder import ResponseBuilder
import os

# Configurar API key
os.environ['DEEPSEEK_API_KEY'] = 'sk-test'

def test_atrapamiento_detection():
    print("🔍 TESTING ATRAPAMIENTO DETECTION")
    print("=" * 50)
    
    # Cargar datos
    df = pd.read_excel('docs/Registro de accidentes laborales EVP - Ago25 (SN).xlsx')
    print(f"✅ Datos cargados: {len(df)} registros")
    
    # Verificar atrapamientos en el Excel
    atrapamientos = df[df['Forma de Accidente'].str.contains('ATRAPAMIENTO|APRISIONAMIENTO', case=False, na=False)]
    print(f"📊 Atrapamientos en Excel: {len(atrapamientos)} casos")
    print("Desglose:", atrapamientos['Forma de Accidente'].value_counts().to_dict())
    
    # Inicializar motores
    indicators = IndicatorsEngine(df)
    response_builder = ResponseBuilder(indicators, None)  # Sin LLM para test
    
    # Calcular indicadores primero
    print("🔄 Calculando indicadores...")
    response_builder.all_indicators = indicators.calculate_all_indicators()
    print(f"✅ Indicadores calculados: {len(response_builder.all_indicators)} tipos")
    
    # Test del método específico
    query = "cuantos atrapamientos hubieron"
    specific_data = response_builder._get_specific_accident_count('atrapamiento')
    print(f"\n🎯 Detección específica: {specific_data}")
    
    # Test del contexto mejorado
    context = response_builder._prepare_data_context(query)
    print(f"\n📋 Contexto generado:")
    print(context[:500] + "..." if len(context) > 500 else context)
    
    # Verificar si el contexto incluye los datos de atrapamiento
    if "ATRAPAMIENTOS ESPECÍFICOS" in context:
        print("✅ SUCCESS: El contexto incluye datos específicos de atrapamiento")
    else:
        print("❌ FAIL: El contexto NO incluye datos específicos de atrapamiento")

if __name__ == "__main__":
    test_atrapamiento_detection()
