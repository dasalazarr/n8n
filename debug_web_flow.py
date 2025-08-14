#!/usr/bin/env python3
"""
Diagnóstico del flujo web para identificar por qué las respuestas siguen siendo genéricas
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sso_enhanced import SSOConsultantEnhanced
import json

def test_web_flow():
    """Test del flujo completo como lo haría la web"""
    print("🔍 DIAGNÓSTICO DEL FLUJO WEB")
    print("=" * 50)
    
    # Inicializar el consultor (como en la web)
    import os
    api_key = os.getenv('DEEPSEEK_API_KEY', 'sk-test')
    consultant = SSOConsultantEnhanced(api_key)
    
    # Test queries que fallan en la web
    test_queries = [
        "¿Cómo está mi empresa vs benchmarks de la industria?",
        "¿Cuánto me están costando los accidentes laborales?",
        "¿Qué acciones debo tomar este mes para reducir accidentes?",
        "¿Cuáles son mis principales riesgos operativos?"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n🧪 TEST {i}: {query}")
        print("-" * 40)
        
        try:
            # Llamar al método exacto que usa la web
            response = consultant.process_query(query)
            
            print(f"✅ Respuesta generada (primeros 200 chars):")
            print(f"   {response[:200]}...")
            
            # Verificar si es genérica o contextual
            if "Error generando respuesta estandarizada" in response:
                print("❌ ERROR DETECTADO en respuesta estandarizada")
            elif "754 registros" in response and "CAÍDA DE PERSONAS A NIVEL" in response:
                print("✅ Respuesta parece contextual (contiene datos reales)")
            else:
                print("⚠️  Respuesta posiblemente genérica")
                
        except Exception as e:
            print(f"❌ EXCEPCIÓN: {str(e)}")
            import traceback
            traceback.print_exc()
    
    # Verificar estado del response_builder
    print(f"\n🔧 ESTADO DEL SISTEMA:")
    print(f"   response_builder: {consultant.response_builder}")
    print(f"   analytics_data: {consultant.analytics_data is not None}")
    if consultant.analytics_data is not None:
        print(f"   registros: {len(consultant.analytics_data)}")

if __name__ == "__main__":
    test_web_flow()
