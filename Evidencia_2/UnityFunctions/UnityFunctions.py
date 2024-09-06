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
    """
    Unity regresa la posición actual del dron (x,y,z)
    """
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
    """
    Unity que regresa la posición actual de la camara con id en (x,y,z)
    """
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
    """
    Se indica a Unity que el dron debe empezar a volar, se regresa una confirmación de que ya está volando
    return flighting = True
    """
    print("Dron Take Off!!!!")


async def next_position():
    """
    Se indica a Unity que sigue la siguiente posición de la ruta, 
    Unity regresa la posición del dron en (x,y,z) después de moverse
    """
    position = (randint(0,10), randint(0,10), randint(0,10))
    print("NEXT POSITION:", position)
    return position


async def move_to(position):
    """
    Unity recibe la posición a la que el dron se debe de mover
    Regresa:
    "move" : True
    Si no se espera el programa
    """
    print("MOVE TO", position)

async def move_forward():
    """
    Unity recibe move_forward : True
    Unity mueve el dron un poco adelante en x o z
    Unity regresa que ya se terminó de mover el dron
    """
    print("MOVE FORWARD!!!!")


async def trigger_alarm():
    """
    Unity recibe que trigger_alarm : True
    Unity regresa que ya se triggereo la alarma
    """
    print("TRIGGER ALARM!!!!")


async def false_alarm():
    """
    Unity recibe que false_alarm : True
    Unity regresa que ya sucedió el evento de falsa alarma
    """
    print("FALSE ALARM!!!!")


async def get_start_position():
    """
    Unity recibe get_start_position : True
    Unity regresa la posición inicial de la ruta
    """
    position = (0, 0, 0)
    print("START POSITION:", position)
    return position

async def get_second_to_last_position():
    """
    Unity recibe get_second_to_last : True
    Unity regresa la penúltima posición de la ruta
    1 antes de que termine la ruta o que inicia la ruta en ese caso
    """
    position = (-1, -1, -1)
    return position

async def end_route():
    """
    Unity recibe que se terminó la ruta
    Unity regresa 
    return flighting = False
    """
    print("END ROUTE!!!!")
