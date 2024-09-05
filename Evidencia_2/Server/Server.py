import sys
import os
import asyncio
import websockets
import json

# Añadir el directorio raíz al PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Model import DronModel as model
import UnityFunctions

async def handler(websocket, path):
    if path == "/dron":
        print("Conexión establecida en la ruta /dron")
        try:
            # Enviar el mensaje de solicitud de la posición del dron
            message = "Dame la posicion"
            await websocket.send(message)
            print(f"Mensaje enviado a Unity: {message}")

            # Esperar la respuesta de Unity
            response = await websocket.recv()
            position_data = json.loads(response)
            print(f"Posición del dron recibida: {position_data['pos']}")

        except websockets.ConnectionClosed:
            print("Conexión cerrada en /dron")

    elif path == "/camara":
        print("Conexión establecida en la ruta /camara")
        try:
            # Enviar el mensaje de solicitud de la posición de la cámara
            message = "Dame la posicion de la camara"
            await websocket.send(message)
            print(f"Mensaje enviado a Unity: {message}")

            # Esperar la respuesta de Unity
            response = await websocket.recv()
            position_data = json.loads(response)
            print(f"Posición de la cámara recibida: {position_data['pos']}")

        except websockets.ConnectionClosed:
            print("Conexión cerrada en /camara")

    else:
        while True:
            try:
                data = await websocket.recv()
                print("DATA: ", data)
                data = json.loads(data)
                print("DATA JSON: ", data)

                # Procesar la información de las cámaras o el dron
                if "camera_alert" in data:
                    certainty = data['certainty']
                    position = data['position']
                    drone = model.drone
                    drone.receive_alert(certainty, position)

                elif "drone_position" in data:
                    drone = model.drone
                    drone.current_pos = data['position']

                if "take_off_command" in data:
                    await UnityFunctions.take_off()

                response = {
                    'Hola': '2'
                }
                await websocket.send(json.dumps(response))

            except websockets.ConnectionClosed:
                print("Conexión cerrada")
                break

async def main():
    # Iniciar el servidor WebSocket
    start_server = websockets.serve(handler, 'localhost', 8765)
    await start_server

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
loop.run_forever()