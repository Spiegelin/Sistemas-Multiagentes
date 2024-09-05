# UnityFunctions.py
import json
import asyncio

# Almacenar los websockets globalmente
websocket_dron = None
websocket_camara = None

# Función para asignar el websocket del dron
async def set_websocket_dron(ws):
    global websocket_dron
    websocket_dron = ws
    print("WebSocket del dron asignado.")

# Función para asignar el websocket de la cámara
async def set_websocket_camara(ws):
    global websocket_camara
    websocket_camara = ws
    print("WebSocket de la cámara asignado.")

# Función para solicitar la posición del dron
async def get_dron_position():
    global websocket_dron
    if websocket_dron is not None:
        request_message = "Dame la posicion del dron"
        await websocket_dron.send(request_message)
        print(f"Solicitud enviada: {request_message}")
    else:
        print("El WebSocket del dron no está conectado.")

# Función para solicitar la posición de la cámara
async def get_camara_position():
    global websocket_camara
    if websocket_camara is not None:
        request_message = "Dame la posicion de la camara"
        await websocket_camara.send(request_message)
        print(f"Solicitud enviada: {request_message}")
    else:
        print("El WebSocket de la cámara no está conectado.")
