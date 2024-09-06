# UnityFunctions.py
from random import randint
import json
import asyncio
import websockets

# Almacenar los websockets globalmente
websocket_dron = None
websocket_camara = None

# Colas para recibir respuestas
response_queue_dron = asyncio.Queue()
response_queue_camara = asyncio.Queue()

# Función para asignar el websocket del dron
async def set_websocket_dron(ws):
    global websocket_dron
    websocket_dron = ws
    print("WebSocket del dron asignado.")
    async for message in ws:
        await response_queue_dron.put(message)

# Función para asignar el websocket de la cámara
async def set_websocket_camara(ws):
    global websocket_camara
    websocket_camara = ws
    print("WebSocket de la cámara asignado.")
    async for message in ws:
        await response_queue_camara.put(message)

# Función para solicitar la posición del dron y esperar la respuesta
async def get_dron_position():
    global websocket_dron
    if websocket_dron is not None:
        request_message = "Dame la posicion del dron"
        await websocket_dron.send(request_message)
        print(f"Solicitud enviada: {request_message}")

        # Esperar la respuesta
        response = await response_queue_dron.get()
        response = json.loads(response)
        print(f"Respuesta del dron: {response}")
        response = response['pos']
        response = tuple(map(int, response.strip("()").split(",")))
        return response

    else:
        print("El WebSocket del dron no está conectado.")
        return None

# Función para solicitar la posición de la cámara y esperar la respuesta
async def get_camera_position(id):
    global websocket_camara
    if websocket_camara is not None:
        request_message = "Dame la posicion de la camara"
        await websocket_camara.send(request_message)
        print(f"Solicitud enviada: {request_message}")

        # Esperar la respuesta
        response = await response_queue_camara.get()
        print(f"Respuesta de la cámara: {response}")
        return response

    else:
        print("El WebSocket de la cámara no está conectado.")
        return None
    
async def take_off():
    print("Dron Take Off!!!!")


async def next_position():
    position = (randint(0,10), randint(0,10), randint(0,10))
    print("NEXT POSITION:", position)
    return position


async def move_to(position):
    print("MOVE TO", position)

async def move_forward():
    print("MOVE FORWARD!!!!")


async def trigger_alarm():
    print("TRIGGER ALARM!!!!")


async def false_alarm():
    print("FALSE ALARM!!!!")


async def get_start_position():
    position = (0, 0, 0)
    print("START POSITION:", position)
    return position


async def end_route():
    print("END ROUTE!!!!")
