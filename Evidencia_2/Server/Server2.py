import sys
import os
import asyncio
import websockets
import json

# Añadir el directorio raíz al PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Model import DronModel as model
import UnityFunctions
import ComputationalVision

async def handler(websocket, path):
    print(f"Conexión establecida en la ruta {path}")

    try:
        while True:
            # Recibir datos del cliente
            data = await websocket.recv()
            print("DATA: ", data)
            data = json.loads(data)
            print("DATA JSON: ", data)

            # Manejar la lógica basada en el contenido del mensaje
            if "path" in data:
                if data["path"] == "/test":
                    # Lógica para la ruta /test
                    response = {"status": "Mandame la pos"}
                    await websocket.send(json.dumps(response))
                    message = await websocket.recv()
                    print(f"Mensaje recibido en /test: {message}")
                else:
                    # Lógica para otros caminos especificados
                    response = {"status": "Ruta desconocida"}
                    await websocket.send(json.dumps(response))
            else:
                # Manejo de datos no especificados por ruta
                if "camera_alert" in data:
                    certainty = data['certainty']
                    position = data['position']
                    drone = model.drone
                    drone.receive_alert(certainty, position)

                elif "drone_position" in data:
                    # Actualizar la posición del dron
                    drone = model.drone
                    drone.current_pos = data['position']

                # Ejemplo de llamada a take_off
                if "take_off_command" in data:
                    # Llama a la función take_off cuando se recibe el comando adecuado
                    await UnityFunctions.take_off()

                # Enviar información de vuelta a Unity
                response = {
                    'Hola': '2'
                }
                await websocket.send(json.dumps(response))

    except websockets.ConnectionClosed:
        print("Conexión cerrada")

async def main():
    # Iniciar el servidor WebSocket
    start_server = websockets.serve(handler, 'localhost', 8765)
    await start_server

# Ejecutar el bucle de eventos existente
loop = asyncio.get_event_loop()
loop.run_until_complete(main())
loop.run_forever()
