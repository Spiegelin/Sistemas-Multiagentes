import ComputationalVision

def get_certainty(position):
    """
    Procesa los resultados del modelo YOLO y devuelve una lista de predicciones con certeza y peligro.
    """
    model = ComputationalVision.get_model()
    results = ComputationalVision.detect_objects()

    predictions = []
    for result in results:
        for detection in result.boxes:
            certainty = detection.conf.item()  # Nivel de certeza
            class_name = model.names[int(detection.cls.item())]  # Tipo de clase

            # Definir si hay peligro según la clase detectada
            danger = class_name == "bad"

            # Añadir a la lista de predicciones
            predictions.append({
                'certainty': certainty,
                'danger': danger,
                'class_name': class_name,
                'position': position
            })
    
    return predictions
