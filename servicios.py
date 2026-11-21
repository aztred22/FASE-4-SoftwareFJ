"""Servicios de Software FJ: clase abstracta Servicio y tres servicios especializados.

Conceptos aplicados:
- Abstracción: Servicio es abstracta y obliga a las hijas a implementar métodos.
- Herencia: ReservaSala, AlquilerEquipo y Asesoria heredan de Servicio (y esta de Entidad).
- Polimorfismo: cada hija sobrescribe _costo_base(), describir() y validar_parametros().
- Encapsulación: atributos privados/protegidos con propiedades validadas.
- Sobrecarga: calcular_costo() y desglose() aceptan distintas combinaciones de
  parámetros (solo horas; horas + impuesto; horas + impuesto + descuento).
"""
import logging
from abc import abstractmethod

from entidad import Entidad
from excepciones import (
    CalculoInconsistenteError,
    ServicioInvalidoError,
)

logger = logging.getLogger("SoftwareFJ")


class Servicio(Entidad):
    """Clase abstracta que representa un servicio ofrecido por Software FJ."""

    _contador_id = 0
    HORAS_MAX = 24  # Límite por defecto; las hijas lo sobrescriben

    def __init__(self, nombre, tarifa_hora, disponible=True):
        try:
            self._nombre = self._validar_texto(nombre, "nombre")
            self._tarifa_hora = self._validar_numero_positivo(tarifa_hora, "tarifa por hora")
            if not isinstance(disponible, bool):
                raise ServicioInvalidoError("La disponibilidad debe ser True o False")
            self._disponible = disponible
            self._validar_atributos_especificos()  # Gancho sobrescrito por cada hija
        except ServicioInvalidoError as error:
            logger.error("No se pudo crear el servicio: %s", error)
            raise ServicioInvalidoError(f"Servicio rechazado: {error}") from error  # Encadenamiento

        Servicio._contador_id += 1
        super().__init__(Servicio._contador_id)
        logger.info("Servicio creado: ID %s - %s (%s)", self.id, self._nombre, type(self).__name__)

    # ---------- Validaciones reutilizables ----------
    @staticmethod
    def _validar_texto(valor, campo):
        if valor is None or not isinstance(valor, str):
            raise ServicioInvalidoError(f"El campo '{campo}' es obligatorio y debe ser texto")
        valor = valor.strip()
        if len(valor) < 3:
            raise ServicioInvalidoError(f"El campo '{campo}' debe tener al menos 3 caracteres")
        return valor

    @staticmethod
    def _validar_numero_positivo(valor, campo):
        if valor is None or isinstance(valor, bool) or not isinstance(valor, (int, float)):
            raise ServicioInvalidoError(f"El campo '{campo}' es obligatorio y debe ser numérico")
        if valor <= 0:
            raise ServicioInvalidoError(f"El campo '{campo}' debe ser mayor a 0")
        return valor

    @staticmethod
    def _validar_entero_en_rango(valor, campo, minimo, maximo):
        if valor is None or isinstance(valor, bool) or not isinstance(valor, int):
            raise ServicioInvalidoError(f"El campo '{campo}' es obligatorio y debe ser un entero")
        if not (minimo <= valor <= maximo):
            raise ServicioInvalidoError(f"El campo '{campo}' debe estar entre {minimo} y {maximo}")
        return valor

    # ---------- Propiedades (encapsulación) ----------
    @property
    def nombre(self):
        return self._nombre

    @property
    def tarifa_hora(self):
        return self._tarifa_hora

    @property
    def disponible(self):
        return self._disponible

    def marcar_disponible(self, estado):
        """Cambia la disponibilidad del servicio (True/False)."""
        if not isinstance(estado, bool):
            raise ServicioInvalidoError("La disponibilidad debe ser True o False")
        self._disponible = estado
        logger.info("Servicio %s ahora %s", self._nombre, "disponible" if estado else "NO disponible")

    # ---------- Métodos abstractos (polimorfismo) ----------
    @abstractmethod
    def _validar_atributos_especificos(self):
        """Valida los atributos propios de cada servicio especializado."""

    @abstractmethod
    def _costo_base(self, horas):
        """Costo sin impuestos ni descuentos para la cantidad de horas dada."""

    @abstractmethod
    def describir(self):
        """Descripción del servicio. Cada hija la sobrescribe."""

    # ---------- Validación de parámetros de la reserva ----------
    def validar_parametros(self, horas):
        """Valida la duración solicitada. Las hijas la extienden con sus propios límites."""
        if horas is None or isinstance(horas, bool) or not isinstance(horas, (int, float)):
            raise ServicioInvalidoError("La duración debe ser un número de horas")
        if horas <= 0:
            raise ServicioInvalidoError("La duración debe ser mayor a 0 horas")
        if horas > self.HORAS_MAX:
            raise ServicioInvalidoError(
                f"La duración máxima para {type(self).__name__} es {self.HORAS_MAX} horas"
            )
        return True

    # ---------- Cálculo de costos (métodos sobrecargados) ----------
    def calcular_costo(self, horas, impuesto=0.0, descuento=0.0):
        """Calcula el costo final. Variantes de uso (sobrecarga mediante parámetros opcionales):

            calcular_costo(horas)                        -> costo base
            calcular_costo(horas, impuesto)              -> costo base + impuesto
            calcular_costo(horas, impuesto, descuento)   -> costo con descuento e impuesto

        impuesto y descuento son fracciones entre 0 y 1 (0.19 = 19 %).
        """
        self.validar_parametros(horas)
        for nombre, valor in (("impuesto", impuesto), ("descuento", descuento)):
            if isinstance(valor, bool) or not isinstance(valor, (int, float)) or not (0 <= valor <= 1):
                raise CalculoInconsistenteError(
                    f"El {nombre} debe ser un valor entre 0 y 1 (recibido: {valor!r})"
                )
        base = self._costo_base(horas)
        if base <= 0:
            raise CalculoInconsistenteError("El costo base calculado no es válido")
        total = base * (1 - descuento) * (1 + impuesto)
        return round(total, 2)

    def desglose(self, horas, impuesto=0.0, descuento=0.0):
        """Devuelve un diccionario con el detalle del cálculo del costo."""
        total = self.calcular_costo(horas, impuesto, descuento)
        base = self._costo_base(horas)
        return {
            "base": round(base, 2),
            "descuento": round(base * descuento, 2),
            "impuesto": round(base * (1 - descuento) * impuesto, 2),
            "total": total,
        }

    # ---------- Creación segura (try/except/else/finally) ----------
    @classmethod
    def crear_seguro(cls, *args, **kwargs):
        """Crea un servicio sin detener el programa si los parámetros son inválidos."""
        servicio = None
        try:
            servicio = cls(*args, **kwargs)
        except ServicioInvalidoError as error:
            logger.error("Fallo en crear_seguro (%s): %s | Causa: %s", cls.__name__, error, error.__cause__)
            print(f"[ERROR] {error} -> Causa: {error.__cause__}")
        except TypeError as error:  # Parámetros faltantes o sobrantes
            logger.error("Parámetros incorrectos al crear %s: %s", cls.__name__, error)
            print(f"[ERROR] Parámetros incorrectos para {cls.__name__}: {error}")
        else:
            print(f"[OK] Servicio creado: {servicio}")
        finally:
            logger.info("Intento de creación de %s finalizado", cls.__name__)
        return servicio

    def __repr__(self):
        return f"{type(self).__name__}(id={self.id}, nombre='{self._nombre}')"


class ReservaSala(Servicio):
    """Reserva de salas de reuniones o capacitación."""

    HORAS_MAX = 12
    CARGO_PROYECTOR_HORA = 20000

    def __init__(self, nombre, tarifa_hora, capacidad, con_proyector=False, disponible=True):
        self._capacidad = capacidad
        self._con_proyector = con_proyector
        super().__init__(nombre, tarifa_hora, disponible)

    def _validar_atributos_especificos(self):
        self._capacidad = self._validar_entero_en_rango(self._capacidad, "capacidad", 1, 200)
        if not isinstance(self._con_proyector, bool):
            raise ServicioInvalidoError("'con_proyector' debe ser True o False")

    def _costo_base(self, horas):
        costo = self._tarifa_hora * horas
        if self._con_proyector:
            costo += self.CARGO_PROYECTOR_HORA * horas
        return costo

    def describir(self):
        extra = "con proyector" if self._con_proyector else "sin proyector"
        return (f"Sala #{self.id} | {self._nombre} | Capacidad: {self._capacidad} personas | "
                f"{extra} | ${self._tarifa_hora:,.0f}/hora")


class AlquilerEquipo(Servicio):
    """Alquiler de equipos tecnológicos."""

    HORAS_MAX = 72
    RECARGO_SEGURO = 0.05  # 5 % de seguro sobre el alquiler

    def __init__(self, nombre, tarifa_hora, tipo_equipo, cantidad=1, disponible=True):
        self._tipo_equipo = tipo_equipo
        self._cantidad = cantidad
        super().__init__(nombre, tarifa_hora, disponible)

    def _validar_atributos_especificos(self):
        self._tipo_equipo = self._validar_texto(self._tipo_equipo, "tipo de equipo")
        self._cantidad = self._validar_entero_en_rango(self._cantidad, "cantidad", 1, 50)

    def _costo_base(self, horas):
        return self._tarifa_hora * horas * self._cantidad * (1 + self.RECARGO_SEGURO)

    def describir(self):
        return (f"Equipo #{self.id} | {self._nombre} | Tipo: {self._tipo_equipo} | "
                f"Cantidad: {self._cantidad} | ${self._tarifa_hora:,.0f}/hora c/u (incluye seguro 5%)")


class Asesoria(Servicio):
    """Asesoría especializada con un profesional junior o senior."""

    HORAS_MAX = 8
    MULTIPLICADORES = {"junior": 1.0, "senior": 1.5}

    def __init__(self, nombre, tarifa_hora, especialidad, nivel="junior", disponible=True):
        self._especialidad = especialidad
        self._nivel = nivel
        super().__init__(nombre, tarifa_hora, disponible)

    def _validar_atributos_especificos(self):
        self._especialidad = self._validar_texto(self._especialidad, "especialidad")
        if not isinstance(self._nivel, str) or self._nivel.lower() not in self.MULTIPLICADORES:
            raise ServicioInvalidoError("El nivel debe ser 'junior' o 'senior'")
        self._nivel = self._nivel.lower()

    def _costo_base(self, horas):
        return self._tarifa_hora * horas * self.MULTIPLICADORES[self._nivel]

    def validar_parametros(self, horas):
        super().validar_parametros(horas)  # Reutiliza la validación general
        if horas < 0.5:
            raise ServicioInvalidoError("La asesoría mínima es de 0.5 horas")
        return True

    def describir(self):
        return (f"Asesoría #{self.id} | {self._nombre} | Especialidad: {self._especialidad} | "
                f"Nivel: {self._nivel} | ${self._tarifa_hora:,.0f}/hora")
