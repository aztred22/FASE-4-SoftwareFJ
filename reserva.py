"""Clase Reserva del sistema Software FJ.

Integra un cliente, un servicio, una duración y un estado, e implementa
confirmación, cancelación y procesamiento con manejo de excepciones.
"""
import logging

from cliente import Cliente
from entidad import Entidad
from excepciones import (
    CalculoInconsistenteError,
    OperacionNoPermitidaError,
    ReservaInvalidaError,
    ServicioInvalidoError,
    ServicioNoDisponibleError,
    SoftwareFJError,
)
from servicios import Servicio

logger = logging.getLogger("SoftwareFJ")


class Reserva(Entidad):
    """Reserva de un servicio por parte de un cliente."""

    PENDIENTE = "PENDIENTE"
    CONFIRMADA = "CONFIRMADA"
    CANCELADA = "CANCELADA"

    _contador_id = 0

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
            servicio.validar_parametros(horas)
        except ServicioInvalidoError as error:
            logger.error("Reserva rechazada por parámetros inválidos: %s", error)
            raise ReservaInvalidaError(f"Reserva rechazada: {error}") from error

        Reserva._contador_id += 1
        super().__init__(Reserva._contador_id)
        self.__cliente = cliente
        self.__servicio = servicio
        self.__horas = horas
        self.__estado = Reserva.PENDIENTE
        self.__costo_total = None

        cliente.agregar_reserva(self)
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
        if self.__estado != Reserva.PENDIENTE:
            raise OperacionNoPermitidaError(
                f"No se puede confirmar una reserva en estado {self.__estado}"
            )
        if not self.__servicio.disponible:
            raise ServicioNoDisponibleError(
                f"El servicio '{self.__servicio.nombre}' no está disponible"
            )
        self.__estado = Reserva.CONFIRMADA
        logger.info("Reserva #%s confirmada", self.id)

    def cancelar(self):
        """Cancela la reserva si no está ya cancelada."""
        if self.__estado == Reserva.CANCELADA:
            raise OperacionNoPermitidaError("La reserva ya estaba cancelada")
        self.__estado = Reserva.CANCELADA
        logger.info("Reserva #%s cancelada", self.id)

    def _calcular_total(self, impuesto, descuento):
        """Calcula el costo total; convierte errores inesperados en CalculoInconsistenteError."""
        try:
            return self.__servicio.calcular_costo(self.__horas, impuesto, descuento)
        except (TypeError, ValueError, ArithmeticError) as error:
            raise CalculoInconsistenteError("Error inesperado en el cálculo del costo") from error

    def procesar(self, impuesto=0.19, descuento=0.0):
        """Procesa la reserva: la confirma y calcula su costo total.

        Nunca detiene el programa: devuelve True si todo salió bien y False si hubo
        un error controlado (que queda registrado en el log).
        """
        exito = False
        try:
            self.confirmar()
            total = self._calcular_total(impuesto, descuento)
        except SoftwareFJError as error:
            logger.error("Fallo al procesar la reserva #%s: %s | Causa: %s",
                         self.id, error, error.__cause__)
            print(f"[ERROR] Reserva #{self.id}: {error}")
        else:
            self.__costo_total = total
            exito = True
            logger.info("Reserva #%s procesada. Total: $%s", self.id, f"{total:,.2f}")
            print(f"[OK] Reserva #{self.id} procesada. Total: ${total:,.2f}")
        finally:
            logger.info("Procesamiento de la reserva #%s finalizado (estado: %s)", self.id, self.__estado)
        return exito

    # ---------- Creación segura ----------
    @classmethod
    def crear_segura(cls, cliente, servicio, horas):
        """Intenta crear una reserva sin detener el programa si hay errores."""
        reserva = None
        try:
            reserva = cls(cliente, servicio, horas)
        except ReservaInvalidaError as error:
            logger.error("Fallo en crear_segura: %s | Causa: %s", error, error.__cause__)
            print(f"[ERROR] {error}")
        else:
            print(f"[OK] Reserva creada: {reserva}")
        finally:
            logger.info("Intento de creación de reserva finalizado")
        return reserva

    # ---------- Representaciones ----------
    def describir(self):
        total = f"${self.__costo_total:,.2f}" if self.__costo_total is not None else "sin calcular"
        return (f"Reserva #{self.id} | Cliente: {self.__cliente.nombre} | "
                f"Servicio: {self.__servicio.nombre} | {self.__horas} h | "
                f"Estado: {self.__estado} | Total: {total}")

    def __repr__(self):
        return f"Reserva(id={self.id}, estado='{self.__estado}')"
