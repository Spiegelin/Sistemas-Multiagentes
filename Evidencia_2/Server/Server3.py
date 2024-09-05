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
    if path == "/camara":
        try:
            # Ejecutar la función para obtener la posición de la cámara
            position = await UnityFunctions.get_camera_position()
            # Enviar la posición de la cámara al cliente
            response_message = json.dumps({"pos": position})
            await websocket.send(response_message)

        except Exception as e:
            print(f"Error en /camara: {e}")


    elif path == "/dron":
        print("Conexión establecida en la ruta /dron")
        try:
            async for message in websocket:
                print(f"Mensaje recibido en /dron: {message}")

                try:
                    data = json.loads(message)
                    action = data.get('action')
                    position = data.get('position')

                    if action == "move_to" and position:
                        # Enviar comando de movimiento al dron
                        move_message = f"muevete a {position}"
                        await websocket.send(move_message)
                        print(f"Comando de movimiento enviado: {move_message}")

                    elif action is None:
                        # Por defecto, solicita la posición del dron
                        request_message = "Dame la posicion del dron"
                        await websocket.send(request_message)
                        print(f"Mensaje enviado para solicitar posición del dron: {request_message}")

                except json.JSONDecodeError as e:
                    print(f"Error de decodificación de JSON: {e}")
                except Exception as e:
                    print(f"Error al procesar el mensaje: {e}")

        except websockets.ConnectionClosed:
            print("Conexión cerrada en /dron")

    else:  # Manejar la ruta raíz
        print("Conexión establecida en la ruta raíz /")
        try:
            while True:
                message = await websocket.recv()
                print(f"Mensaje recibido en /: {message}")

                response = {"status": "connected to /"}
                await websocket.send(json.dumps(response))

        except websockets.ConnectionClosed:
            print("Conexión cerrada en /")
        except Exception as e:
            print(f"Error en la ruta raíz: {e}")

async def main():
    start_server = websockets.serve(handler, 'localhost', 8765)
    await start_server

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
loop.run_forever()