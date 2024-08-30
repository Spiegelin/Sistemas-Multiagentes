import logging
import websockets
import asyncio
import cv2
import numpy as np
from ultralytics import YOLO

# Cargar el modelo YOLO
model = YOLO('Sistemas-Multiagentes/weights/yolov8n.pt')

# Índices de las clases que te interesan
orange_index = 49  

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
                results = model.track(img, persist=True)
                annotated_frame = results[0].plot()

                if img is None or annotated_frame is None:
                    logger.error("The image or annotated frame is None.")
                    continue

                # Guardar el frame para depuración
                cv2.imwrite('debug_frame.jpg', annotated_frame)
                logger.info("Saved frame as debug_frame.jpg")

                # Si se detecta algo, verificar si es una clase de interés
                if results and results[0].boxes:
                    class_index = int(results[0].boxes[0].cls.item())  # Convertir el tensor en un índice de clase

                    # Verificar si el índice detectado corresponde a "orange"
                    if class_index == orange_index:
                        detected_class_name = "orange"
                        detection_message = f"Objeto detectado: {detected_class_name}"
                        await websocket.send(detection_message)
                        logger.info(f"Mensaje enviado al cliente: {detection_message}")
                    else:
                        logger.info(f"Clase no relevante detectada con índice {class_index}")
                        # No enviar nada si no es "orange"
                else:
                    logger.info("No se detectaron objetos de interés.")

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
