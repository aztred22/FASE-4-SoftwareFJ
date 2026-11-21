"""Clase abstracta base de las entidades generales del sistema."""
from abc import ABC, abstractmethod  # ABC y abstractmethod permiten definir clases abstractas

class Entidad(ABC):
    """Representa cualquier entidad general del sistema cliente, servicio, etc...."""

    def __init__(self, id_entidad):
        # Guarda el identificador único de la entidad (atributo protegido por convención)
        self._id = id_entidad

    @property
    def id(self):
        # Permite leer el id como atributo (entidad.id) sin poder modificarlo directamente
        return self._id

    @abstractmethod
    def describir(self):
        """Devuelve una descripción de la entidad. Cada subclase la implementa."""
        pass  # Sin cuerpo: las clases hijas están obligadas a sobrescribirlo (polimorfismo)

    def __str__(self):
        # Al imprimir cualquier entidad con print(), se muestra su descripción
        return self.describir()
