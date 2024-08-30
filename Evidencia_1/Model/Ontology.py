from owlready2 import *

# Cargar ontología (desde Vaccum Cleaner)
onto = get_ontology("file://onto.owl")
with onto:
    class Entity(Thing):
        pass

    class Robot(Entity):
        pass

    class Caja(Entity):
        pass

    class Base(Entity):
        pass

    class has_place(ObjectProperty):
        domain = [Entity]
        range = [Base]

    class has_position(DataProperty):
        domain = [Entity]
        range = [str]
