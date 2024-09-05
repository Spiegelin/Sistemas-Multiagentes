import logging
import websockets
import asyncio
import cv2
import numpy as np
from ultralytics import YOLO
#import json
#from get_dron_certainty import process_predictions

# Cargar el modelo YOLO
model = YOLO('C:/Users/luisf/OneDrive/Documentos/Coding/Tec/Sistemas multiagentes con graficas computacionales/Espejin/Sistemas-Multiagentes/Evidencia_2/ComputationalVision/Model-training/runs/detect/train/weights/best.pt')

# Configuración de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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

def get_model():
    return model

def detect_objects(img):
    results = model.track(img, persist=True)
    return results

async def handle_websocket_client(websocket, path):
    logger = logging.getLogger("handle_websocket_client")
    logger.info("Connected to client")

    try:
        while True:
            try:
                # Recepción de datos del cliente (esperamos recibir datos binarios)
                data = await websocket.recv()

                if not data:
                    break

                numeric_data, initial_buffer = get_numeric_data(data)
                try:
                    data_len = int(numeric_data.decode('ascii'))
                except ValueError:
                    logger.error("Invalid data length received")
                    break

                logger.info("data_len: {}".format(data_len))

                buffer = initial_buffer
                bytes_left = data_len - len(buffer)

                # Recibimos los datos restantes
                while bytes_left > 0:
                    fragment = await websocket.recv()
                    if not fragment:
                        logger.error("Connection lost before receiving complete data")
                        return

                    buffer += fragment
                    bytes_left = data_len - len(buffer)

                if len(buffer) != data_len:
                    logger.error("Received data length does not match the expected length")
                    break

                # Decodificar la imagen de los bytes
                nparr = np.frombuffer(buffer, np.uint8)
                img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

                if img is None:
                    logger.error("Failed to decode image")
                    continue

                # Procesar la imagen con el modelo YOLO
                results = detect_objects(img)
                annotated_frame = results[0].plot()

                if img is None or annotated_frame is None:
                    logger.error("The image or annotated frame is None.")
                    continue

                # Usar la función para procesar las predicciones
                #predictions = process_predictions(results, model)

                # Enviar predicciones al servidor
                #await send_predictions_to_server(predictions)
                
                # Guardar el frame para depuración
                cv2.imwrite('debug_frame.jpg', annotated_frame)
                logger.info("Saved frame as debug_frame.jpg")

                # Configurar y mostrar el frame procesado
                cv2.imshow('YOLOv8 Tracking', annotated_frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

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

if __name__ == "__main__":
    try:
        asyncio.run(websocket_server())
    finally:
        cv2.destroyAllWindows()