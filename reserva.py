"""Clase Reserva del sistema Software FJ.

Integra un cliente, un servicio, una duración y un estado, e implementa
confirmación, cancelación y procesamiento con manejo de excepciones.
"""
import logging  # Registro de eventos y errores en logs.txt

from cliente import Cliente  # Para verificar que el cliente recibido sea un Cliente real
from entidad import Entidad  # Clase abstracta de la que hereda Reserva
from excepciones import (
    CalculoInconsistenteError,  # Cálculo de costos inválido
    OperacionNoPermitidaError,  # Operación no válida para el estado actual
    ReservaInvalidaError,  # Datos de reserva inválidos
    ServicioInvalidoError,  # Error de parámetros del servicio (se convierte en ReservaInvalidaError)
    ServicioNoDisponibleError,  # Servicio marcado como no disponible
    SoftwareFJError,  # Excepción base: captura cualquier error propio del sistema
)
from servicios import Servicio  # Para verificar que el servicio recibido sea un Servicio real

logger = logging.getLogger("SoftwareFJ")  # Logger compartido por todo el sistema


class Reserva(Entidad):
    """Reserva de un servicio por parte de un cliente."""

    # Estados posibles de una reserva
    PENDIENTE = "PENDIENTE"
    CONFIRMADA = "CONFIRMADA"
    CANCELADA = "CANCELADA"

    _contador_id = 0  # Contador compartido para generar ids únicos de reserva

    def __init__(self, cliente, servicio, horas):
        # Validación de los objetos recibidos
        if not isinstance(cliente, Cliente):
            logger.error("Reserva rechazada: cliente inválido (%r)", cliente)
            raise ReservaInvalidaError("La reserva requiere un cliente válido")
        if not isinstance(servicio, Servicio):
            logger.error("Reserva rechazada: servicio inválido (%r)", servicio)
            raise ReservaInvalidaError("La reserva requiere un servicio válido")

        # Validación de la duración (encadenamiento de excepciones)
        try:
            servicio.validar_parametros(horas)  # Cada servicio valida con sus propias reglas
        except ServicioInvalidoError as error:
            logger.error("Reserva rechazada por parámetros inválidos: %s", error)
            # Se convierte en un error de reserva conservando la causa original
            raise ReservaInvalidaError(f"Reserva rechazada: {error}") from error

        # Si todo es válido: se asigna id y se guardan los datos (atributos privados)
        Reserva._contador_id += 1
        super().__init__(Reserva._contador_id)
        self.__cliente = cliente
        self.__servicio = servicio
        self.__horas = horas
        self.__estado = Reserva.PENDIENTE  # Toda reserva nueva inicia pendiente
        self.__costo_total = None  # Se calcula al procesar la reserva

        cliente.agregar_reserva(self)  # La reserva queda en la lista interna del cliente
        logger.info("Reserva #%s creada: %s -> %s (%s h)", self.id, cliente.nombre, servicio.nombre, horas)

    # ---------- Propiedades de solo lectura (encapsulación) ----------
    @property
    def cliente(self):
        return self.__cliente

    @property
    def servicio(self):
        return self.__servicio

    @property
    def horas(self):
        return self.__horas

    @property
    def estado(self):
        return self.__estado

    @property
    def costo_total(self):
        return self.__costo_total

    # ---------- Operaciones sobre la reserva ----------
    def confirmar(self):
        """Confirma la reserva si está pendiente y el servicio está disponible."""
        # Solo se puede confirmar una reserva pendiente
        if self.__estado != Reserva.PENDIENTE:
            raise OperacionNoPermitidaError(
                f"No se puede confirmar una reserva en estado {self.__estado}"
            )
        # El servicio debe estar disponible
        if not self.__servicio.disponible:
            raise ServicioNoDisponibleError(
                f"El servicio '{self.__servicio.nombre}' no está disponible"
            )
        self.__estado = Reserva.CONFIRMADA  # Cambia el estado
        logger.info("Reserva #%s confirmada", self.id)

    def cancelar(self):
        """Cancela la reserva si no está ya cancelada."""
        # No se puede cancelar dos veces
        if self.__estado == Reserva.CANCELADA:
            raise OperacionNoPermitidaError("La reserva ya estaba cancelada")
        self.__estado = Reserva.CANCELADA  # Cambia el estado
        logger.info("Reserva #%s cancelada", self.id)

    def _calcular_total(self, impuesto, descuento):
        """Calcula el costo total; convierte errores inesperados en CalculoInconsistenteError."""
        try:
            return self.__servicio.calcular_costo(self.__horas, impuesto, descuento)
        except (TypeError, ValueError, ArithmeticError) as error:
            # Errores de Python no previstos se convierten en un error propio, conservando la causa
            raise CalculoInconsistenteError("Error inesperado en el cálculo del costo") from error

    def procesar(self, impuesto=0.19, descuento=0.0):
        """Procesa la reserva: la confirma y calcula su costo total.

        Nunca detiene el programa: devuelve True si todo salió bien y False si hubo
        un error controlado (que queda registrado en el log).
        """
        exito = False  # Se asume fallo hasta que todo salga bien
        try:
            self.confirmar()  # Paso 1: confirmar la reserva
            total = self._calcular_total(impuesto, descuento)  # Paso 2: calcular el costo
        except SoftwareFJError as error:
            # Cualquier error propio del sistema se registra y se muestra, sin detener el programa
            logger.error("Fallo al procesar la reserva #%s: %s | Causa: %s",
                         self.id, error, error.__cause__)
            print(f"[ERROR] Reserva #{self.id}: {error}")
        else:
            # Solo si no hubo excepción: se guarda el total y se marca el éxito
            self.__costo_total = total
            exito = True
            logger.info("Reserva #%s procesada. Total: $%s", self.id, f"{total:,.2f}")
            print(f"[OK] Reserva #{self.id} procesada. Total: ${total:,.2f}")
        finally:
            # Se ejecuta siempre, haya o no error
            logger.info("Procesamiento de la reserva #%s finalizado (estado: %s)", self.id, self.__estado)
        return exito

    # ---------- Creación segura ----------
    @classmethod
    def crear_segura(cls, cliente, servicio, horas):
        """Intenta crear una reserva sin detener el programa si hay errores."""
        reserva = None  # Si algo falla, se devolverá None
        try:
            reserva = cls(cliente, servicio, horas)  # Intenta crear la reserva
        except ReservaInvalidaError as error:
            # Se registra y se muestra el error, pero el programa continúa
            logger.error("Fallo en crear_segura: %s | Causa: %s", error, error.__cause__)
            print(f"[ERROR] {error}")
        else:
            # Solo si no hubo excepción
            print(f"[OK] Reserva creada: {reserva}")
        finally:
            # Se ejecuta siempre
            logger.info("Intento de creación de reserva finalizado")
        return reserva

    # ---------- Representaciones ----------
    def describir(self):
        # Implementa el método abstracto de Entidad (polimorfismo)
        total = f"${self.__costo_total:,.2f}" if self.__costo_total is not None else "sin calcular"
        return (f"Reserva #{self.id} | Cliente: {self.__cliente.nombre} | "
                f"Servicio: {self.__servicio.nombre} | {self.__horas} h | "
                f"Estado: {self.__estado} | Total: {total}")

    def __repr__(self):
        # Representación técnica, útil al depurar
        return f"Reserva(id={self.id}, estado='{self.__estado}')"
