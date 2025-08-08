#!/usr/bin/env python3
"""
Test API Key - Verificar que la API key funciona correctamente
"""

import os
from dotenv import load_dotenv

def test_api_key():
    print("🔍 Verificando API key...")
    
    # Cargar variables de entorno
    load_dotenv()
    api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key:
        print("❌ No se encontró API key en .env")
        return False
    
    print(f"✅ API Key encontrada: {api_key[:15]}...{api_key[-10:]}")
    print(f"📏 Longitud: {len(api_key)} caracteres")
    
    # Verificar que es la correcta
    if api_key.endswith('wJaGjwQFQA'):
        print("✅ API Key CORRECTA detectada")
    else:
        print("❌ API Key INCORRECTA")
        print(f"Termina en: {api_key[-10:]}")
        return False
    
    # Probar conexión con OpenAI
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        
        print("🔄 Probando conexión con OpenAI...")
        response = client.chat.completions.create(
            model='gpt-3.5-turbo',
            messages=[{'role': 'user', 'content': 'Responde solo: CONEXION_EXITOSA'}],
            max_tokens=10,
            temperature=0
        )
        
        result = response.choices[0].message.content.strip()
        print(f"✅ Conexión OpenAI exitosa!")
        print(f"📝 Respuesta: '{result}'")
        return True
        
    except Exception as e:
        print(f"❌ Error conectando con OpenAI: {e}")
        return False

if __name__ == "__main__":
    success = test_api_key()
    if success:
        print("\n🎉 API Key funcionando correctamente!")
        print("✅ Sistema listo para iniciar")
    else:
        print("\n❌ Problema con API Key")
        print("🔧 Verifica tu configuración en .env")
    
    exit(0 if success else 1)
