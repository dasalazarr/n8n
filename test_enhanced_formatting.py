#!/usr/bin/env python3
"""
Test Enhanced HTML Formatting
Prueba el sistema mejorado de formato HTML para respuestas
"""

import requests
import json
import re

def test_enhanced_formatting():
    """Test the enhanced HTML formatting system"""
    
    print("🧪 TESTING ENHANCED HTML FORMATTING")
    print("=" * 60)
    
    # Test query that should trigger analytics and formatted response
    test_query = "Basándote en nuestros datos de 754 accidentes, ¿qué áreas presentan mayor riesgo?"
    
    try:
        response = requests.post('http://localhost:8085/chat', 
            json={'message': test_query},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            html_response = data.get('response', '')
            
            print("✅ QUERY SUCCESSFUL")
            print(f"📝 Query: {test_query}")
            print("=" * 60)
            
            # Check for enhanced HTML elements
            html_checks = {
                'Tables': '<table class="risk-table">' in html_response,
                'Headers': '<h3>' in html_response or '<h4>' in html_response,
                'Risk Badges': any(badge in html_response for badge in ['risk-high', 'risk-medium', 'risk-low']),
                'Structured Lists': '<ul>' in html_response or '<ol>' in html_response,
                'Strong Emphasis': '<strong>' in html_response,
                'Analysis Sections': 'analysis-section' in html_response or 'recommendation-box' in html_response
            }
            
            print("🔍 HTML FORMATTING ANALYSIS:")
            for feature, present in html_checks.items():
                status = "✅" if present else "❌"
                print(f"  {status} {feature}: {'Present' if present else 'Missing'}")
            
            print("\n📄 FORMATTED RESPONSE PREVIEW:")
            print("-" * 60)
            # Show first 800 characters of the response
            preview = html_response[:800] + "..." if len(html_response) > 800 else html_response
            print(preview)
            print("-" * 60)
            
            # Extract and show clean text version
            clean_text = re.sub('<[^<]+?>', '', html_response)
            print("\n📝 CLEAN TEXT VERSION (first 300 chars):")
            print("-" * 60)
            print(clean_text[:300] + "..." if len(clean_text) > 300 else clean_text)
            print("-" * 60)
            
            # Overall assessment
            passed_checks = sum(html_checks.values())
            total_checks = len(html_checks)
            
            print(f"\n📊 FORMATTING SCORE: {passed_checks}/{total_checks}")
            if passed_checks >= 4:
                print("🎉 EXCELLENT: Enhanced formatting is working well!")
            elif passed_checks >= 2:
                print("⚠️  GOOD: Some formatting features are working")
            else:
                print("❌ NEEDS IMPROVEMENT: Formatting enhancements not detected")
                
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Connection Error: {e}")

if __name__ == "__main__":
    test_enhanced_formatting()
