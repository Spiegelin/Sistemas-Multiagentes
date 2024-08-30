import asyncio
import websockets
import json
from Model import DronModel as model
import UnityFunctions
import ComputationalVision

async def handler(websocket, path):
    while True:
        try:
            # Recibir datos de Unity
            data = await websocket.recv()
            data = json.loads(data)

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

            # Enviar información de vuelta a Unity
            response = {
                'drone_position': drone.current_pos,
                'certainty': drone.certainty,
                'danger': drone.is_dangerous
            }
            await websocket.send(json.dumps(response))

        except websockets.ConnectionClosed:
            print("Conexión cerrada")
            break

# Iniciar servidor
start_server = websockets.serve(handler, 'localhost', 8765)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
