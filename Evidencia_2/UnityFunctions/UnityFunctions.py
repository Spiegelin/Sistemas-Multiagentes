# UnityFunctions.py
from random import randint
import json
import asyncio
import websockets

# Almacenar los websockets globalmente
websocket_dron = None
websocket_camera = None

# Colas para recibir respuestas
response_queue_dron = asyncio.Queue()
response_queue_camera = asyncio.Queue()

# Función para asignar el websocket del dron
async def set_websocket_dron(ws):
    global websocket_dron
    websocket_dron = ws
    print("WebSocket del dron asignado.")
    async for message in ws:
        await response_queue_dron.put(message)

# Función para asignar el websocket de la cámara
async def set_websocket_camera(ws):
    global websocket_camera
    websocket_camera = ws
    print("WebSocket de la cámara asignado.")
    async for message in ws:
        await response_queue_camera.put(message)

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
    Unity regresa la posición actual de la cámara con el ID dado (x,y,z).
    """
    global websocket_camera
    if websocket_camera is not None:
        request_message = f"Dame la posicion de la camara {id}"
        await websocket_camera.send(request_message)
        print(f"Solicitud enviada: {request_message}")

        # Esperar la respuesta
        response = await response_queue_camera.get()
        response = json.loads(response)
        print(f"Respuesta de la cámara {id}: {response}")
        response = response['pos']
        response = tuple(map(int, response.strip("()").split(",")))
        return response

    else:
        print("El WebSocket de la cámara no está conectado.")
        return None
    
async def take_off():
    """
    Se indica a Unity que el dron debe empezar a volar.
    Unity regresa una confirmación si el dron está volando ("flying": "true" or "false").
    return flighting = True o False
    """
    global websocket_dron
    if websocket_dron is not None:
        request_message = "Despega"
        await websocket_dron.send(request_message)
        print(f"Solicitud enviada: {request_message}")

        # Esperar la respuesta
        response = await response_queue_dron.get()
        response = json.loads(response)
        print(f"Respuesta de vuelo del dron: {response}")

        # Retornar el estado de vuelo
        flighting = response['flying'] == "true"
        return flighting

    else:
        print("El WebSocket del dron no está conectado.")
        return False



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
    Envía una solicitud a Unity para mover el dron a la posición especificada.
    position: tupla con las coordenadas (x, y, z)
    """
    global websocket_dron
    if websocket_dron is not None:
        request_message = json.dumps({"pos": str(position)})
        await websocket_dron.send(request_message)
        print(f"Solicitud enviada: {request_message}")

        # Esperar la respuesta de confirmación si es necesario
        response = await response_queue_dron.get()  # Si esperas confirmación
        response = json.loads(response)
        print(f"Respuesta de movimiento del dron: {response}")

    else:
        print("El WebSocket del dron no está conectado.")



async def move_forward():
    """
    Unity recibe move_forward : True
    Unity mueve el dron un poco adelante en x o z
    Unity regresa que ya se terminó de mover el dron
    """
    global websocket_dron
    if websocket_dron is not None:
        request_message = "Avanza"
        await websocket_dron.send(request_message)
        print(f"Solicitud enviada: {request_message}")

        # Esperar la respuesta
        response = await response_queue_dron.get()
        response = json.loads(response)
        print(f"Respuesta de avanzar dron: {response}")

        # Retornar el estado de vuelo
        mvFoward = response['Forward'] == "true"
        return mvFoward

    else:
        print("El WebSocket del dron no está conectado.")
        return False


async def trigger_alarm():
    """
    Unity recibe que trigger_alarm : True
    Unity regresa que ya se triggereo la alarma
    """
    global websocket_dron
    if websocket_dron is not None:
        request_message = "Prende la alarma"
        await websocket_dron.send(request_message)
        print(f"Solicitud enviada: {request_message}")

        # Esperar la respuesta
        response = await response_queue_dron.get()
        response = json.loads(response)
        print(f"Respuesta de la alarma: {response}")

        # Retornar el estado de vuelo
        alarm = response['alarm'] == "true"
        return alarm

    else:
        print("El WebSocket del dron no está conectado.")
        return False



async def false_alarm():
    """
    Unity recibe que false_alarm : True
    Unity regresa que ya sucedió el evento de falsa alarma
    """
    global websocket_dron
    if websocket_dron is not None:
        request_message = "Falsa alarma"
        await websocket_dron.send(request_message)
        print(f"Solicitud enviada: {request_message}")

        # Esperar la respuesta
        response = await response_queue_dron.get()
        response = json.loads(response)
        print(f"Respuesta de vuelo del dron: {response}")

        # Retornar el estado de vuelo
        falseAlarm = response['falseAlarm'] == "true"
        return falseAlarm

    else:
        print("El WebSocket del dron no está conectado.")
        return False


async def get_start_position():
    """
    Unity recibe get_start_position : True
    Unity regresa la posición inicial de la ruta
    """
    global websocket_dron
    if websocket_dron is not None:
        request_message = "Primer punto de ruta"
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

async def get_second_to_last_position():
    """
    Unity recibe get_second_to_last : True
    Unity regresa la penúltima posición de la ruta
    1 antes de que termine la ruta o que inicia la ruta en ese caso
    """
    global websocket_dron
    if websocket_dron is not None:
        request_message = "Penultimo punto de ruta"
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

async def end_route():
    """
    Unity recibe que se terminó la ruta
    Unity regresa 
    return flighting = False
    """
    global websocket_dron
    if websocket_dron is not None:
        request_message = "Termina la ruta"
        await websocket_dron.send(request_message)
        print(f"Solicitud enviada: {request_message}")

        # Esperar la respuesta
        response = await response_queue_dron.get()
        response = json.loads(response)
        print(f"Respuesta de vuelo del dron: {response}")

        # Retornar el estado de vuelo
        endRoute = response['endRoute'] == "true"
        return endRoute

    else:
        print("El WebSocket del dron no está conectado.")
        return False
