import asyncio
import sys, os
import websockets
import json
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


# Importar las funciones necesarias desde UnityFunctions
from UnityFunctions.UnityFunctions import set_websocket_dron, set_websocket_camara, get_dron_position, get_camara_position

async def handler(websocket, path):
    if path == "/camara":
        print("Conexión establecida en la ruta /camara")
        try:
            await set_websocket_camara(websocket)
            async for message in websocket:
                print(f"Mensaje recibido de la cámara: {message}")

        except websockets.ConnectionClosed:
            print("Conexión cerrada en /camara")
        except Exception as e:
            print(f"Error en /camara: {e}")

    elif path == "/dron":
        print("Conexión establecida en la ruta /dron")
        try:
            await set_websocket_dron(websocket)
            async for message in websocket:
                print(f"Mensaje recibido del dron: {message}")

        except websockets.ConnectionClosed:
            print("Conexión cerrada en /dron")
        except Exception as e:
            print(f"Error en /dron: {e}")
    
    else:
        print("Conexión establecida en la ruta raíz /")
        try:
            while True:
                message = await websocket.recv()
                print(f"Mensaje recibido en /: {message}")

                response = {"status": "connected to /"}
                await websocket.send(json.dumps(response))

                print("A punto de llamar al main")
                await get_dron_position()
                await get_camara_position()

        except websockets.ConnectionClosed:
            print("Conexión cerrada en /")
        #except Exception as e:
         #   print(f"Error en la ruta raíz: {e}")

async def main():
    start_server = websockets.serve(handler, 'localhost', 8765)
    await start_server

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
loop.run_forever()
