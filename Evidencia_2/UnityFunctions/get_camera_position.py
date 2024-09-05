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

            # Verificar que la respuesta no esté vacía antes de procesarla
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
            # Esperar el mensaje de solicitud de la posición
            message = await websocket.recv()
            print(f"Mensaje recibido en /dron: {message}")

            if message == "Dame la posicion":
                # Simula la obtención de la posición del dron
                dron_position = "(10, 20, 30)"  # Ejemplo de posición
                response = json.dumps({"pos": dron_position})
                await websocket.send(response)
                print(f"Posición del dron enviada: {response}")

        except websockets.ConnectionClosed:
            print("Conexión cerrada en /dron")

    else:
        while True:
            try:
                # Recibir datos de Unity
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
                break

async def main():
    # Iniciar el servidor WebSocket
    start_server = websockets.serve(handler, 'localhost', 8765)
    await start_server

# Ejecutar el bucle de eventos existente
loop = asyncio.get_event_loop()
loop.run_until_complete(main())
loop.run_forever()
