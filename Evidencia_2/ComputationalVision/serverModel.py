from dotenv import load_dotenv
import os
import logging
import websockets
import asyncio
import cv2
import numpy as np
from ultralytics import YOLO
import random

# Load the environment variables
load_dotenv()

#import json
#from get_dron_certainty import process_predictions

# Cargar el modelo YOLO
model = YOLO(os.getenv("LOCAL_PATH"))

# Configuración de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_certainty2(id=1):
    return 0.8

def get_numeric_data(buffer):
    """
    Extract numeric data (e.g., data length) from the buffer and separate it from the rest of the data.
    """
    numeric_buffer = b''
    left_bytes = b''

    for b in buffer:
        if 48 <= b <= 57:  
            numeric_buffer += bytes([b])
        else:
            left_bytes += bytes([b])

    return numeric_buffer, left_bytes

'''
async def send_predictions_to_server(predictions):
    uri = "ws://localhost:8765"  # Your WebSocket server address
    try:
        async with websockets.connect(uri) as websocket:
            logging.info(f"Sending predictions: {json.dumps(predictions)}")
            # Send predictions to the server
            await websocket.send(json.dumps(predictions))
            # Optionally, wait for the server's response (if necessary)
    except Exception as e:
        logging.error(f"Failed to send predictions to the server: {e}")
'''

def get_certainty(cam_id="10"):
    certainty = 0

    try:
        # Cargar la imagen de depuración de la cámara
        img = cv2.imread(f'debug_frame_{cam_id}.jpg')

        if img is None:
            logging.error(f"No se pudo cargar la imagen para la cámara: {cam_id}")
            return None

        # Ejecutar el modelo YOLO en la imagen
        results = model.predict(img)

        # Acceder a las cajas de detección (boxes) para obtener el valor de certeza
        if results and len(results) > 0:
            if results[0].boxes is not None:
                boxes = results[0].boxes  # Obtener las cajas de detección
                confidences = boxes.conf  # Acceder a la confianza de cada detección
                class_ids = boxes.cls  # IDs de las clases detectadas

                # Obtener los nombres de las clases del modelo
                class_names = model.names

                # Filtrar por la clase 'bad' y obtener la certeza más alta
                for i, class_id in enumerate(class_ids):
                    class_name = class_names[int(class_id)]  # Obtener el nombre de la clase
                    if class_name == 'bad':  # Verificar si la clase es 'bad'
                        certainty = confidences[i]  # Tomar la certeza asociada
                        logging.info(f"Detección de 'bad' con certeza: {certainty}")
                        break  # Salir del bucle si encontramos una detección 'bad'

                if certainty is None:
                    logging.warning(f"No se encontraron detecciones de 'bad' para la cámara: {cam_id}")
                    
            else:
                logging.warning(f"No hay cajas de detección para la cámara: {cam_id}")
    
    except Exception as e:
        logging.error(f"Error al obtener la certeza para la cámara {cam_id}: {e}")
    
    return float(certainty)

async def handle_websocket_client(websocket, path):
    logger = logging.getLogger("handle_websocket_client")
    logger.info("Connected to client")

    try:
        while True:
            try:
                # Recepción de datos del cliente
                data = await websocket.recv()

                if not data:
                    break

                # Separar el ID de la cámara y la longitud de los datos
                data = data.decode('utf-8')
                camera_id, numeric_data = data.split(":")
                data_len = int(numeric_data)

                logger.info(f"Camera ID: {camera_id}, Data length: {data_len}")

                buffer = b""
                bytes_left = data_len

                # Recibimos los datos de la imagen
                while bytes_left > 0:
                    fragment = await websocket.recv()
                    buffer += fragment
                    bytes_left = data_len - len(buffer)

                if len(buffer) != data_len:
                    logger.error("Received data length does not match the expected length")
                    break

                # Procesar la imagen
                nparr = np.frombuffer(buffer, np.uint8)
                img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

                if img is None:
                    logger.error("Failed to decode image from camera: {}".format(camera_id))
                    continue

                # Procesar la imagen con el modelo YOLO
                results = model.track(img, persist=True)

                # Guardar el frame para depuración
                cv2.imwrite(f'debug_frame_{camera_id}.jpg', results[0].plot())
                logger.info(f"Saved frame from camera {camera_id} as debug_frame_{camera_id}.jpg")

            except websockets.exceptions.ConnectionClosedError as e:
                logger.error(f"Connection closed unexpectedly: {e}")
                break
            except Exception as e:
                logger.error(f"Error in connection handler: {e}", exc_info=True)
                break

    except Exception as e:
        logger.error(f"Fatal error in websocket handler: {e}", exc_info=True)

    logger.info("Client disconnected")

async def websocket_server():
    logger = logging.getLogger("websocket_server")

    HOST = '127.0.0.1'
    PORT = 5000

    logger.info(f"WebSocket server listening on port: {HOST}:{PORT}")

    async with websockets.serve(handle_websocket_client, HOST, PORT):
        await asyncio.Future()  # Run forever

def getcertainty(id=1):
    return 0.82

if __name__ == "__main__":
    try:
        asyncio.run(websocket_server())
    finally:
        cv2.destroyAllWindows()