import asyncio
import websockets
import json

async def get_camera_position():
    """Función para solicitar la posición de la cámara a Unity."""
    uri = "ws://localhost:8765/camara"  # Endpoint de Unity para la cámara
    message = "Dame la posicion de la camara"
    try:
        async with websockets.connect(uri) as websocket:
            # Enviar mensaje a Unity
            await websocket.send(message)
            print(f"Mensaje enviado: {message}")

            # Esperar respuesta de Unity
            response = await websocket.recv()
            position_data = json.loads(response)
            print(f"Posición de la cámara recibida: {position_data['pos']}")

            # Retornar la posición de la cámara
            return position_data['pos']

    except Exception as e:
        print(f"Error al solicitar la posición de la cámara: {e}")
        return None
