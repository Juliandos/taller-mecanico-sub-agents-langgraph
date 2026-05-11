"""Servidor simple para exponer chat de LangGraph"""
import http.server
import socketserver
import json
from pathlib import Path
from urllib.parse import urlparse
import requests
import uuid
from langchain_core.messages import HumanMessage

PORT = 8080
LANGGRAPH_URL = "http://127.0.0.1:2024"
HTML_FILE = Path(__file__).parent / "chat.html"


class ChatHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        """Servir el archivo HTML"""
        if self.path in ["/", "/chat.html"]:
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            with open(HTML_FILE, "r", encoding="utf-8") as f:
                self.wfile.write(f.read().encode())
            return

        self.send_error(404)

    def do_POST(self):
        """Manejar POST /api/chat"""
        if self.path == "/api/chat":
            self._handle_chat()
            return

        self.send_error(404)

    def _handle_chat(self):
        """Procesar mensaje de chat y obtener respuesta de LangGraph"""
        try:
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length)
            request_data = json.loads(body.decode())

            thread_id = request_data.get("thread_id")
            message = request_data.get("message", "").strip()

            if not message:
                self._send_error("Mensaje vacío", 400)
                return

            print(f"\n[CHAT] Mensaje recibido: {message[:100]}")

            # Crear thread si no existe
            if not thread_id:
                print("[CHAT] Creando nuevo thread en LangGraph...")
                try:
                    thread_response = requests.post(
                        f"{LANGGRAPH_URL}/threads",
                        json={},
                        headers={"Content-Type": "application/json"},
                        timeout=10
                    )

                    if thread_response.status_code in [200, 201]:
                        thread_data = thread_response.json()
                        thread_id = thread_data.get("thread_id") or thread_data.get("id")
                        print(f"[CHAT] Thread creado en LangGraph: {thread_id}")
                    else:
                        print(f"[CHAT] Advertencia: No se pudo crear thread en LangGraph, usando UUID")
                        thread_id = str(uuid.uuid4())
                        print(f"[CHAT] Thread UUID: {thread_id}")
                except Exception as e:
                    print(f"[CHAT] Error creando thread: {e}, usando UUID")
                    thread_id = str(uuid.uuid4())

            # Ejecutar el grafo
            print(f"[CHAT] Invocando grafo para thread: {thread_id}")

            try:
                # Usar el assistant "taller" definido en langgraph.json
                assistant_id = "taller"
                print(f"[CHAT] Usando assistant: {assistant_id}")

                # Crear el run con streaming
                print(f"[CHAT] Creando run en thread {thread_id[:8]}...")

                # Crear mensaje de usuario en formato de LangChain
                user_msg = HumanMessage(content=message)

                response = requests.post(
                    f"{LANGGRAPH_URL}/threads/{thread_id}/runs/stream",
                    json={
                        "assistant_id": assistant_id,
                        "input": {
                            "messages": [user_msg.model_dump()]
                        }
                    },
                    headers={"Content-Type": "application/json"},
                    timeout=60,
                    stream=True
                )

                print(f"[CHAT] Response status: {response.status_code}")

                if response.status_code not in [200, 201]:
                    error_text = response.text[:500]
                    print(f"[CHAT] Error: {error_text}")
                    self._send_error(f"Error {response.status_code}: {error_text}", response.status_code)
                    return

                # Procesar eventos del stream
                result = self._process_stream(response)
                print(f"[CHAT] Stream procesado, resultado: {bool(result)}")

                # Extraer el último mensaje del asistente
                assistant_response = self._extract_response(result)

                if not assistant_response:
                    print("[CHAT] ⚠️ No se encontró respuesta, usando fallback")
                    assistant_response = "Entiendo tu problema. ¿Puedes dar más detalles?"

                # Retornar respuesta
                self._send_json({
                    "thread_id": thread_id,
                    "response": assistant_response
                })

            except requests.exceptions.Timeout:
                self._send_error("Timeout esperando respuesta de LangGraph", 504)
            except requests.exceptions.ConnectionError:
                self._send_error("No se puede conectar a LangGraph en " + LANGGRAPH_URL, 503)

        except json.JSONDecodeError:
            self._send_error("JSON inválido", 400)
        except Exception as e:
            print(f"[CHAT] Error: {e}")
            self._send_error(str(e), 500)

    def _process_stream(self, response):
        """Procesa eventos del stream SSE de LangGraph"""
        result = None

        try:
            for line in response.iter_lines():
                if not line:
                    continue

                line_str = line.decode() if isinstance(line, bytes) else line

                if line_str.startswith("data: "):
                    try:
                        event_data = json.loads(line_str[6:])
                        result = event_data
                        print(f"[CHAT] Stream event, keys: {list(event_data.keys())[:5]}")
                    except json.JSONDecodeError:
                        pass
        except Exception as e:
            print(f"[CHAT] Error procesando stream: {e}")

        return result or {}

    def _extract_response(self, result):
        """Extrae la respuesta del asistente del resultado de LangGraph"""
        messages = result.get("messages", [])
        print(f"[CHAT] Total mensajes: {len(messages)}")

        # Filtrar solo los últimos mensajes (últimos 10) para evitar mensajes antiguos acumulados
        recent_messages = messages[-10:] if len(messages) > 10 else messages

        # Buscar el ÚLTIMO mensaje del asistente (tipo 'ai') en los mensajes recientes
        ai_messages = []
        for msg in recent_messages:
            msg_type = msg.get("type", "").lower() if isinstance(msg, dict) else getattr(msg, "type", "").lower()
            content = msg.get("content", "") if isinstance(msg, dict) else getattr(msg, "content", "")

            if msg_type == "ai" and content and isinstance(content, str) and len(content) > 10:
                ai_messages.append((msg_type, content))

        print(f"[CHAT] Mensajes AI encontrados (últimos): {len(ai_messages)}")

        if ai_messages:
            # Tomar el ÚLTIMO mensaje de AI (más reciente)
            msg_type, content = ai_messages[-1]
            print(f"[CHAT] ✅ Usando último mensaje de tipo '{msg_type}', len={len(content)}")
            return content

        return None

    def _send_json(self, data, status=200):
        """Enviar respuesta JSON"""
        self.send_response(status)
        self.send_header("Content-type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def _send_error(self, message, status=500):
        """Enviar error JSON"""
        self._send_json({"error": message}, status)

    def do_OPTIONS(self):
        """Manejar CORS preflight"""
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()


if __name__ == "__main__":
    with socketserver.TCPServer(("", PORT), ChatHandler) as httpd:
        print(f"\n{'='*60}")
        print(f"✅ Servidor corriendo en http://127.0.0.1:{PORT}")
        print(f"📍 Abre en tu navegador: http://127.0.0.1:{PORT}")
        print(f"🔗 Conectando a LangGraph: {LANGGRAPH_URL}")
        print(f"{'='*60}\n")
        print("Presiona Ctrl+C para detener\n")
        httpd.serve_forever()
