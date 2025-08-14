#!/usr/bin/env python3
"""
Test directo del ResponseBuilder para diagnosticar el bug crítico
"""

import pandas as pd
import sys
import os
sys.path.append('/Users/dasalazarr/Projects/n8n')

from engines.indicators_engine import IndicatorsEngine
from engines.response_builder import ResponseBuilder

def test_response_builder():
    """Test directo para identificar por qué no funcionan las respuestas contextuales"""
    
    print("🔍 DIAGNÓSTICO DIRECTO DEL RESPONSE BUILDER")
    print("=" * 60)
    
    # Cargar datos reales
    try:
        df = pd.read_excel('/Users/dasalazarr/Projects/n8n/docs/Registro de accidentes laborales EVP - Ago25 (SN).xlsx')
        print(f"✅ Cargado Excel: {len(df)} registros")
    except Exception as e:
        print(f"❌ Error cargando Excel: {e}")
        return
    
    # Inicializar motores
    try:
        indicators_engine = IndicatorsEngine(df)
        response_builder = ResponseBuilder(indicators_engine)
        print("✅ Motores inicializados")
    except Exception as e:
        print(f"❌ Error inicializando motores: {e}")
        return
    
    # Test 1: Query sobre benchmarking
    print("\n🧪 TEST 1: Query benchmarking")
    print("-" * 40)
    
    query_benchmark = "¿Cómo estamos comparados con la industria? Necesito benchmark"
    
    try:
        response = response_builder.build_response(query_benchmark, intent="DATA", requested_analyses=None)
        print(f"✅ Respuesta generada")
        print(f"📝 Resumen ejecutivo: {response.get('resumen_ejecutivo', 'NO ENCONTRADO')[:100]}...")
        print(f"🧠 Thinking visible: {len(response.get('proceso_thinking', []))} pasos")
        print(f"🎯 Conclusión contextual: {response.get('conclusion_contextual', 'NO ENCONTRADA')[:100]}...")
    except Exception as e:
        print(f"❌ ERROR en test benchmarking: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 2: Query sobre costos
    print("\n🧪 TEST 2: Query costos")
    print("-" * 40)
    
    query_cost = "¿Cuánto dinero hemos perdido por accidentes? Análisis financiero"
    
    try:
        response = response_builder.build_response(query_cost, intent="DATA", requested_analyses=None)
        print(f"✅ Respuesta generada")
        print(f"📝 Resumen ejecutivo: {response.get('resumen_ejecutivo', 'NO ENCONTRADO')[:100]}...")
        print(f"🧠 Thinking visible: {len(response.get('proceso_thinking', []))} pasos")
        print(f"🎯 Conclusión contextual: {response.get('conclusion_contextual', 'NO ENCONTRADA')[:100]}...")
    except Exception as e:
        print(f"❌ ERROR en test costos: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 3: Query general
    print("\n🧪 TEST 3: Query general")
    print("-" * 40)
    
    query_general = "Dame un resumen de los accidentes"
    
    try:
        response = response_builder.build_response(query_general, intent="DATA", requested_analyses=None)
        print(f"✅ Respuesta generada")
        print(f"📝 Resumen ejecutivo: {response.get('resumen_ejecutivo', 'NO ENCONTRADO')[:100]}...")
        print(f"🧠 Thinking visible: {len(response.get('proceso_thinking', []))} pasos")
        print(f"🎯 Conclusión contextual: {response.get('conclusion_contextual', 'NO ENCONTRADA')[:100]}...")
    except Exception as e:
        print(f"❌ ERROR en test general: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_response_builder()
