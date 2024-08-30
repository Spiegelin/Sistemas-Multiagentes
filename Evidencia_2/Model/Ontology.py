from owlready2 import *

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

# Guardar la ontología
#onto.save()