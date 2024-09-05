import asyncio
import websockets
import json
from Model import DronModel as model  # Modelo del dron

async def get_dron_position():
    """Función para solicitar la posición del dron a Unity."""
    uri = "ws://localhost:8765/dron"  # Endpoint de Unity para el dron
    message = "Dame la posicion"
    try:
        async with websockets.connect(uri) as websocket:
            # Enviar mensaje a Unity
            await websocket.send(message)
            print(f"Mensaje enviado: {message}")

            # Esperar respuesta de Unity
            response = await websocket.recv()
            position_data = json.loads(response)
            print(f"Posición del dron recibida: {position_data['pos']}")

            # Actualizar el modelo del dron con la posición recibida
            drone = model.drone
            drone.current_pos = position_data['pos']

            # Retornar la posición del dron
            return position_data['pos']

    except Exception as e:
        print(f"Error al solicitar la posición del dron: {e}")
        return None
