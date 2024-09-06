import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import asyncio
import websockets
import json
import agentpy as ap
import time
from UnityFunctions.UnityFunctions import *
from ComputationalVision.get import get_certainty, get_dron_certainty
from owlready2 import *

#
#
#        ONTOLOGÍA
#
#
onto = get_ontology("file://security_onto.owl")

with onto:
    class Entity(Thing):
        pass

    class Drone(Entity):
        pass

    class Camera(Entity):
        pass

    class Guard(Entity):
        pass

    class has_position(DataProperty):
        domain = [Entity]
        range = [str]

    class has_certainty(DataProperty):
        domain = [Entity]
        range = [float]

    class has_danger(DataProperty):
        domain = [Entity]
        range = [bool]


#
#
#        AGENTES:
# DRON - CAMERA - GUARD
#
#

# Mensajes de simulación (usando un diccionario)
mensajes = {}

# Función para enviar un mensaje a un agente específico
def enviar_mensaje(destinatario, contenido):
    if destinatario not in mensajes:
        mensajes[destinatario] = []
    
    # Solo agregar el mensaje si la lista está vacía
    if not mensajes[destinatario] and not len(mensajes[destinatario]) > 0:
        mensajes[destinatario].append(contenido)
    else:
        print(f"$ Mensaje ignorado: ya se tiene una alerta pendiente.")


# Función para procesar los mensajes de un agente específico
def recibir_mensajes(agente_id):
    if agente_id in mensajes:
        mensajes_recibidos = mensajes[agente_id]
        del mensajes[agente_id]  # Limpiar mensajes una vez procesados
        return mensajes_recibidos
    return []

class DroneAgent(ap.Agent):
    def setup(self):
        self.owl_entity = Drone()
        self.patrolling = False
        self.current_pos = None
        self.previous_pos = None
        self.certainty = None
        self.is_dangerous = False
        self.target_pos = None
        self.flighting = False
        self.finish_route = False
        self.in_control = False
        self.before_alert_pos = None
        self.investigating = False

    async def initialize(self):
        self.current_pos = await get_dron_position()
        print(f"CURRENT POS: {self.current_pos}")
        self.certainty = get_dron_certainty()  # 0 .. 1
        print(f"CERTAINTY: ", self.certainty)

    async def start_patrol(self):
        if self.current_pos == self.model.start_position and not self.flighting:
            print(f"$ Dron despega en {self.current_pos}")
            self.patrolling = True
            self.flighting = True
            await take_off()
        elif self.current_pos == self.model.start_position and self.previous_pos == self.model.route[-2] and self.flighting and not self.is_dangerous and self.finish_route: 
            await self.end_route()
        await self.move_along_route()

    async def move_along_route(self):
        # Movimiento en ruta predefinida
        self.previous_pos = self.current_pos
        self.current_pos = await next_position()
        print(f"$ Dron se mueve a {self.current_pos}")
        
        # Si la posición actual es la de inicio, se termina la ruta
        if self.current_pos == self.model.start_position:
            await self.end_route()
        pass

    async def end_route(self):
        print(f"$ Dron terminó su ruta")
        print(f"$ Dron desciende en {self.current_pos}")
        print(f"$ Dron se espera por 10 segundos")
        self.flighting = False
        self.finish_route = False   
        await end_route()
        #time.sleep(10)

    async def receive_alert(self, certainty, position):
        if not self.investigating:
            self.certainty = certainty
            self.target_pos = position

            # Si la certeza es mayor a 0.5 y no está investigando ya, se inicia una investigación
            if self.certainty > 0.5:
                self.before_alert_pos = self.current_pos
                self.investigating = True
                print(f"$ Posición del dron antes de investigar: {self.before_alert_pos}")
                await self.investigate()

    async def investigate(self):
        # Se mueve a la posición objetivo y señala al guardia si es peligroso
        if self.current_pos != self.target_pos:
            await self.move_to(self.target_pos)

        # Ya que llegó a la posición objetivo, se verifica si es peligroso
        self.certainty = get_dron_certainty()
        #self.is_dangerous = ComputationalVision.detect_danger()
        self.is_dangerous = True
        if self.certainty > 0.6:
            print(f"$ Dron en posición {self.current_pos} señala peligro al guardia por mensaje")
            enviar_mensaje("guardia", {"take_control": {"certainty": self.certainty, "is_dangerous": self.is_dangerous}})
            print("Mensajes Guardia: ", mensajes["guardia"], end="\n\n")
        else:
            print(f"$ Dron en posición {self.current_pos} no detectó peligro.")
            await self.move_to(self.before_alert_pos)

    async def move_to(self, position):
        # Lógica de movimiento hacia una posición específica
        # Solo se regresaría a Unity que se mueva a la siguiente posición
        print(f"$ Dron se mueve de {self.current_pos} a {position}")
        self.previous_pos = self.current_pos
        self.current_pos = position
        await move_to(position)

    async def revisar_mensajes(self):
        if not self.investigating:
            mensajes_drone = recibir_mensajes("dron")
            for mensaje in mensajes_drone:
                if "receive_alert" in mensaje:
                    alerta = mensaje["receive_alert"]
                    await self.receive_alert(alerta["certainty"], alerta["position"])
                
                if "return_to_route" in mensaje:
                    print(f"$ Dron regresa a su ruta en posición {self.before_alert_pos}")
                    self.investigating = False
                    await self.move_to(self.before_alert_pos)


class CameraAgent(ap.Agent):
    def setup(self):
        self.owl_entity = Camera()
        self.id = str(self)[17:-1]
        
    async def detect_movement(self):
        # Simular detección de maldad? y llamar al dron si es necesario
        #position = await get_camera_position(self.id)
        position = await get_camera_position()
        certainty = get_certainty(self.id)
        #danger = ComputationalVision.detect_danger()
        if certainty > 0.5:
            enviar_mensaje("dron", {"receive_alert": {"certainty": certainty, "position": position}})
            print(f"- {self}: Aviso al dron sobre una posible amenaza en {position} con certeza {certainty}.")
            print("Mensajes Dron: ", mensajes["dron"], end="\n\n")

class GuardAgent(ap.Agent):
    def setup(self):
        self.owl_entity = Guard()

    async def take_control(self, certainty, danger):
        print(f"* Guardia toma control del dron con certeza {certainty} y peligro {danger}")
        # Se tomaría control del dron y se verifica si es peligroso
        certainty = get_dron_certainty() # Obtener certeza de la visión computacional después de tomar control
        #danger = ComputationalVision.detect_danger() # Detectar peligro por visión computacional
        if certainty > 0.7 and danger:
            await self.trigger_alarm()
        else:
            await move_forward()
            new_certainty = get_dron_certainty() # Obtener certeza de la visión computacional después de tomar control
            #new_danger = ComputationalVision.detect_danger() # Detectar peligro por visión computacional
            new_danger = True
            if certainty > 0.7 and danger:
                if new_certainty > certainty and new_danger:
                    await self.trigger_alarm()
                else:
                    await self.false_alarm()
            else:
                await self.false_alarm()
        
    async def trigger_alarm(self):
        # Se regresa a Unity que se active la alarma
        print("* ¡Alarma general! Peligro detectado.")
        enviar_mensaje("dron", {"return_to_route": True})
        print("Mensajes Dron: ", mensajes["dron"], end="\n\n")
        await trigger_alarm()
        #time.sleep(10)


    async def false_alarm(self):
        # Se regresa a Unity que fue falsa alarma y vuelva a la ruta
        print("* Falsa alarma. El dron vuelve a su ruta.")
        enviar_mensaje("dron", {"return_to_route": True})
        print("Mensajes Dron: ", mensajes["dron"], end="\n\n")
        await false_alarm()
        #time.sleep(5)


    async def revisar_mensajes(self):
        mensajes_guardia = recibir_mensajes("guardia")
        for mensaje in mensajes_guardia:
            if "take_control" in mensaje:
                control = mensaje["take_control"]
                await self.take_control(control["certainty"], control["is_dangerous"])


#
#
#        MODELO
#
#
class SecurityModel(ap.Model):
    async def setup(self):
        self.drone = DroneAgent(self)
        self.cameras = ap.AgentList(self, 3, CameraAgent)
        self.guard = GuardAgent(self)

        # Ruta predefinida para el dron, la manda unity
        self.start_position = await get_start_position() # (x,y,z)
        self.steps = 0

        await self.drone.initialize()

    async def step(self):
        self.steps += 1
        await self.drone.start_patrol()
        await self.drone.revisar_mensajes()
        await self.guard.revisar_mensajes()
        for camera in self.cameras:
            await camera.detect_movement()

        print(f"---------------Step {self.steps}----------------")




async def handler(websocket, path):
    if path == "/camera":
        print("Conexión establecida en la ruta /camera")
        try:
            await set_websocket_camara(websocket)

        except websockets.ConnectionClosed:
            print("Conexión cerrada en /camara")
        except Exception as e:
            print(f"Error en /camara: {e}")

    elif path == "/dron":
        print("Conexión establecida en la ruta /dron")
        try:
            await set_websocket_dron(websocket)

        except websockets.ConnectionClosed:
            print("Conexión cerrada en /dron")
        except Exception as e:
            print(f"Error en /dron: {e}")
    
    else:
        print("Conexión establecida en la ruta raíz /")
        # Parámetros de la simulación
        parameters = {
            'steps': 500,
        }

        # Ejecutar la simulación
        model = SecurityModel(parameters)
        await model.setup()

        # Registrar el tiempo de inicio
        start_time = time.time()
        try:
            steps = 0
            while True:
                message = await websocket.recv()
                print(f"Mensaje recibido en /: {message}")

                response = {"status": "connected to /"}
                await websocket.send(json.dumps(response))

                print("A punto de iniciar el Agentpy")
                await model.step()
                steps += 1
                
                # Esperar la respuesta de dron y cámara si es necesario
                # Puedes usar get_dron_position() y get_camera_position(id) aquí si es necesario

                # Verificar si se han agotado los pasos
                if steps >= parameters['steps']:
                    print("Se han agotado los steps")
                    
                    final_data = {
                        'type': 'final',
                        'duration': time.time() - start_time,
                        'steps': model.t,
                    }
                    await websocket.send(json.dumps(final_data))
                    break

        except websockets.ConnectionClosed:
            print("Conexión cerrada en /")
        except Exception as e:
            print(f"Error en la ruta raíz: {e}")

async def main():
    start_server = websockets.serve(handler, 'localhost', 8765)
    await start_server

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.run_forever()