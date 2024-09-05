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
        print("Conexión establecida en la ruta /camara")
        try:
            # Enviar mensaje a Unity
            message = "Dame la posicion de la camara"
            await websocket.send(message)
            print(f"Mensaje enviado a Unity: {message}")

            # Esperar respuesta de Unity
            response = await websocket.recv()
            print(f"Respuesta de Unity: {response}")

            if response:
                position_data = json.loads(response)
                print(f"Posición de la cámara recibida: {position_data['pos']}")
            else:
                print("Respuesta vacía o no válida recibida de Unity")

        except json.JSONDecodeError as e:
            print(f"Error de decodificación de JSON: {e}")
        except websockets.ConnectionClosed:
            print("Conexión cerrada en /camara")

    elif path == "/dron":
        print("Conexión establecida en la ruta /dron")
        try:
            # Enviar mensaje a Unity
            message = "Dame la posicion del dron"
            await websocket.send(message)
            print(f"Mensaje enviado a Unity: {message}")

            # Esperar respuesta de Unity
            response = await websocket.recv()
            print(f"Respuesta de Unity: {response}")

            if response:
                position_data = json.loads(response)
                print(f"Posición del dron recibida: {position_data['pos']}")
            else:
                print("Respuesta vacía o no válida recibida de Unity")

        except json.JSONDecodeError as e:
            print(f"Error de decodificación de JSON: {e}")
        except websockets.ConnectionClosed:
            print("Conexión cerrada en /dron")

    else:  # Manejar la ruta raíz
        print("Conexión establecida en la ruta raíz /")
        try:
            while True:
                # Mantener la conexión abierta y escuchar mensajes
                message = await websocket.recv()
                print(f"Mensaje recibido en /: {message}")

                # Procesar mensaje recibido o responder
                response = {"status": "connected to /"}
                await websocket.send(json.dumps(response))

        except websockets.ConnectionClosed:
            print("Conexión cerrada en /")
        except Exception as e:
            print(f"Error en la ruta raíz: {e}")

async def main():
    # Iniciar el servidor WebSocket
    start_server = websockets.serve(handler, 'localhost', 8765)
    await start_server

# Ejecutar el bucle de eventos existente
loop = asyncio.get_event_loop()
loop.run_until_complete(main())
loop.run_forever()
