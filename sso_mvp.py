#!/usr/bin/env python3
"""
SSO Consultant MVP - Sistema Funcional Mínimo
MVP funcional para consultoría SSO con OpenAI
"""

import os
from flask import Flask, render_template_string, request, jsonify
from openai import OpenAI
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)

class SSOConsultantMVP:
    """MVP del Consultor SSO"""
    
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
        print("✅ MVP SSO Consultant inicializado")
    
    def process_query(self, message: str) -> str:
        """Procesa consulta del usuario"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": """
                        Eres un consultor experto en Seguridad y Salud Ocupacional especializado en normativa peruana.
                        
                        CONOCIMIENTO BASE:
                        - LEY 29783: Ley de Seguridad y Salud en el Trabajo
                        - DS 005-2012-TR: Reglamento de la Ley de SST
                        - RM 050-2013-TR: Formatos de registros obligatorios
                        
                        OBLIGACIONES POR TAMAÑO DE EMPRESA:
                        - Menos de 20 trabajadores: Supervisor SST
                        - 20 o más trabajadores: Comité SST + Supervisor SST
                        - Más de 100 trabajadores: Comité SST + Supervisor SST + Médico ocupacional
                        
                        MULTAS (UIT 2024: S/ 5,150):
                        - Leves: 0.27-5 UIT (S/ 1,391-25,750)
                        - Graves: 5.01-10 UIT (S/ 25,802-51,500)
                        - Muy Graves: 10.01-100 UIT (S/ 51,552-515,000)
                        
                        RESPONDE EN HTML ESTRUCTURADO:
                        - Usa <h3> para títulos
                        - Usa <table> para datos organizados
                        - Usa <ul><li> para listas
                        - Usa <strong> para resaltar información importante
                        """
                    },
                    {
                        "role": "user",
                        "content": message
                    }
                ],
                temperature=0.7,
                max_tokens=1500
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"""
            <div style="color: red; border: 1px solid red; padding: 10px; border-radius: 5px;">
            <h3>Error en el Sistema</h3>
            <p>No se pudo procesar su consulta.</p>
            <p><small>Error: {str(e)}</small></p>
            </div>
            """

# Instancia global del consultor
consultant = None

def get_consultant():
    """Obtiene instancia del consultor"""
    global consultant
    if consultant is None:
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY no configurada")
        consultant = SSOConsultantMVP(api_key)
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
    <title>SSO Consultant MVP</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .container {
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            width: 90%;
            max-width: 800px;
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
        
        .header p {
            color: #666;
            font-size: 1.1em;
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
            background: #667eea;
            color: white;
            margin-left: 20%;
        }
        
        .assistant-message {
            background: white;
            border: 1px solid #e0e0e0;
            margin-right: 20%;
        }
        
        .input-container {
            display: flex;
            gap: 10px;
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
            background: #667eea;
            color: white;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            font-size: 16px;
            font-weight: bold;
        }
        
        .send-button:hover {
            background: #5a6fd8;
        }
        
        .send-button:disabled {
            background: #ccc;
            cursor: not-allowed;
        }
        
        .suggestions {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin-bottom: 20px;
        }
        
        .suggestion-chip {
            background: #f0f0f0;
            border: 1px solid #ddd;
            border-radius: 20px;
            padding: 8px 15px;
            cursor: pointer;
            font-size: 14px;
            transition: all 0.3s ease;
        }
        
        .suggestion-chip:hover {
            background: #667eea;
            color: white;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 10px 0;
        }
        
        th, td {
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }
        
        th {
            background-color: #f2f2f2;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🛡️ SSO Consultant MVP</h1>
            <p>Consultor especializado en Seguridad y Salud Ocupacional - Normativa Peruana</p>
        </div>
        
        <div class="suggestions">
            <div class="suggestion-chip" onclick="sendMessage('Mi empresa tiene 50 trabajadores, ¿qué obligaciones SST tenemos?')">
                🏢 Obligaciones por tamaño
            </div>
            <div class="suggestion-chip" onclick="sendMessage('¿Qué multas aplican por no tener comité de SST?')">
                💰 Multas y sanciones
            </div>
            <div class="suggestion-chip" onclick="sendMessage('¿Cómo implementar un sistema de gestión SST?')">
                🛠️ Implementación SST
            </div>
            <div class="suggestion-chip" onclick="sendMessage('¿Qué registros son obligatorios según RM 050-2013?')">
                📝 Registros obligatorios
            </div>
        </div>
        
        <div class="chat-container" id="chatContainer">
            <div class="message assistant-message">
                <strong>🛡️ SSO Consultant MVP</strong><br>
                ¡Hola! Soy tu consultor especializado en Seguridad y Salud Ocupacional para normativa peruana.<br><br>
                Puedo ayudarte con:
                <ul>
                    <li>Obligaciones SST según tamaño de empresa</li>
                    <li>Multas y sanciones por incumplimiento</li>
                    <li>Implementación de sistemas de gestión SST</li>
                    <li>Registros obligatorios y formatos</li>
                </ul>
                ¿En qué puedo ayudarte hoy?
            </div>
        </div>
        
        <div class="input-container">
            <input type="text" id="messageInput" class="input-field" placeholder="Escribe tu consulta sobre SSO..." onkeypress="handleKeyPress(event)">
            <button onclick="sendMessage()" class="send-button" id="sendButton">Enviar</button>
        </div>
    </div>

    <script>
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
            sendButton.textContent = 'Enviando...';
            
            // Enviar a servidor
            fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: message })
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
    </script>
</body>
</html>
    """)

@app.route('/chat', methods=['POST'])
def chat():
    """Endpoint para consultas"""
    try:
        data = request.get_json()
        message = data.get('message', '').strip()

        if not message:
            return jsonify({'error': 'Mensaje requerido'}), 400

        consultant = get_consultant()
        response = consultant.process_query(message)

        return jsonify({'response': response})

    except Exception as e:
        print(f"Error en endpoint /chat: {e}")
        return jsonify({
            'error': f'Error procesando consulta: {str(e)}'
        }), 500

if __name__ == '__main__':
    try:
        # Verificar API key
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            print("❌ Error: OPENAI_API_KEY no configurada en .env")
            exit(1)
        
        print("🚀 Iniciando SSO Consultant MVP...")
        print(f"🔑 API Key: {api_key[:15]}...{api_key[-10:]}")
        
        # Probar conexión
        test_consultant = SSOConsultantMVP(api_key)
        
        print("✅ MVP listo en http://localhost:8083")
        app.run(host='0.0.0.0', port=8083, debug=True)
        
    except Exception as e:
        print(f"❌ Error iniciando MVP: {e}")
        exit(1)
