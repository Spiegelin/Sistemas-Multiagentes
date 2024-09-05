# get_certainty_dron.py

def get_dron_certainty(results, model):
    """
    Procesa los resultados del modelo YOLO y devuelve una lista de predicciones
    con certeza y peligro (sin posición).
    """
    predictions = []
    
    for result in results:
        for detection in result.boxes:
            certainty = detection.conf.item()  # Nivel de certeza
            class_name = model.names[int(detection.cls.item())]  # Tipo de clase

            # Definir si hay peligro según la clase detectada
            danger = class_name == "bad"

            # Añadir a la lista de predicciones, sin la posición
            predictions.append({
                'certainty': certainty,
                'danger': danger,
                'class_name': class_name
            })
    
    return predictions
