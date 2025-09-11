#!/usr/bin/env python3
"""
Debug específico para el error 'columns' en métodos contextuales
"""

import sys
import os
import traceback
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sso_enhanced import SSOConsultantEnhanced

def test_specific_methods():
    """Test específico de métodos que fallan"""
    print("🔍 DEBUG ESPECÍFICO DEL ERROR 'COLUMNS'")
    print("=" * 50)
    
    try:
        # Inicializar consultor
        api_key = os.getenv('DEEPSEEK_API_KEY', 'sk-test')
        consultant = SSOConsultantEnhanced(api_key)
        
        # Acceder directamente al ResponseBuilder
        rb = consultant.response_builder
        
        print(f"ResponseBuilder: {rb}")
        print(f"IndicatorsEngine: {rb.indicators}")
        print(f"DataFrame shape: {rb.indicators.df.shape if hasattr(rb.indicators.df, 'shape') else 'NO SHAPE'}")
        print(f"DataFrame columns available: {hasattr(rb.indicators.df, 'columns')}")
        
        if hasattr(rb.indicators.df, 'columns'):
            print(f"Columns: {list(rb.indicators.df.columns)[:5]}...")  # Solo primeras 5
        
        # Test específico de métodos que fallan
        test_methods = [
            ("_build_benchmark_response", "benchmark test"),
            ("_build_cost_response", "cost test"),
            ("_build_action_plan_response", "action test"),
            ("_build_risk_response", "risk test")  # Este funciona
        ]
        
        for method_name, test_query in test_methods:
            print(f"\n🧪 TESTING {method_name}")
            print("-" * 30)
            
            try:
                method = getattr(rb, method_name)
                response = method(test_query)
                print(f"✅ {method_name} - SUCCESS")
                print(f"   Keys: {list(response.keys())}")
                
            except Exception as e:
                print(f"❌ {method_name} - ERROR: {str(e)}")
                traceback.print_exc()
                
    except Exception as e:
        print(f"❌ SETUP ERROR: {str(e)}")
        traceback.print_exc()

if __name__ == "__main__":
    test_specific_methods()
