"""Servicios de Software FJ: clase abstracta Servicio y tres servicios especializados.

Conceptos aplicados:
- Abstracción: Servicio es abstracta y obliga a las hijas a implementar métodos.
- Herencia: ReservaSala, AlquilerEquipo y Asesoria heredan de Servicio (y esta de Entidad).
- Polimorfismo: cada hija sobrescribe _costo_base(), describir() y validar_parametros().
- Encapsulación: atributos privados/protegidos con propiedades validadas.
- Sobrecarga: calcular_costo() y desglose() aceptan distintas combinaciones de
  parámetros (solo horas; horas + impuesto; horas + impuesto + descuento).
"""
import logging  # Registro de eventos y errores en logs.txt
from abc import abstractmethod  # Decorador para declarar métodos abstractos

from entidad import Entidad  # Clase abstracta raíz de la herencia
from excepciones import (
    CalculoInconsistenteError,  # Errores en impuestos, descuentos o costos
    ServicioInvalidoError,  # Errores en los parámetros del servicio
)

logger = logging.getLogger("SoftwareFJ")  # Logger compartido por todo el sistema


class Servicio(Entidad):
    """Clase abstracta que representa un servicio ofrecido por Software FJ."""

    _contador_id = 0  # Contador compartido para generar ids únicos de servicio
    HORAS_MAX = 24  # Límite por defecto; las hijas lo sobrescriben

    def __init__(self, nombre, tarifa_hora, disponible=True):
        try:
            # Valida y guarda los datos comunes a todos los servicios
            self._nombre = self._validar_texto(nombre, "nombre")
            self._tarifa_hora = self._validar_numero_positivo(tarifa_hora, "tarifa por hora")
            # La disponibilidad debe ser un booleano real (True/False)
            if not isinstance(disponible, bool):
                raise ServicioInvalidoError("La disponibilidad debe ser True o False")
            self._disponible = disponible
            self._validar_atributos_especificos()  # Gancho sobrescrito por cada hija
        except ServicioInvalidoError as error:
            # Se registra el error y se relanza conservando la causa original
            logger.error("No se pudo crear el servicio: %s", error)
            raise ServicioInvalidoError(f"Servicio rechazado: {error}") from error  # Encadenamiento

        # Solo si todo fue válido se asigna el id y se llama al constructor de Entidad
        Servicio._contador_id += 1
        super().__init__(Servicio._contador_id)
        logger.info("Servicio creado: ID %s - %s (%s)", self.id, self._nombre, type(self).__name__)

    # ---------- Validaciones reutilizables ----------
    @staticmethod
    def _validar_texto(valor, campo):
        # Debe existir y ser texto
        if valor is None or not isinstance(valor, str):
            raise ServicioInvalidoError(f"El campo '{campo}' es obligatorio y debe ser texto")
        valor = valor.strip()  # Quita espacios sobrantes
        # Mínimo 3 caracteres
        if len(valor) < 3:
            raise ServicioInvalidoError(f"El campo '{campo}' debe tener al menos 3 caracteres")
        return valor

    @staticmethod
    def _validar_numero_positivo(valor, campo):
        # Debe ser int o float (los booleanos se rechazan aunque Python los trate como int)
        if valor is None or isinstance(valor, bool) or not isinstance(valor, (int, float)):
            raise ServicioInvalidoError(f"El campo '{campo}' es obligatorio y debe ser numérico")
        # Debe ser estrictamente mayor que cero
        if valor <= 0:
            raise ServicioInvalidoError(f"El campo '{campo}' debe ser mayor a 0")
        return valor

    @staticmethod
    def _validar_entero_en_rango(valor, campo, minimo, maximo):
        # Debe ser un número entero (no bool, no decimal)
        if valor is None or isinstance(valor, bool) or not isinstance(valor, int):
            raise ServicioInvalidoError(f"El campo '{campo}' es obligatorio y debe ser un entero")
        # Debe estar dentro del rango permitido
        if not (minimo <= valor <= maximo):
            raise ServicioInvalidoError(f"El campo '{campo}' debe estar entre {minimo} y {maximo}")
        return valor

    # ---------- Propiedades (encapsulación) ----------
    @property
    def nombre(self):
        return self._nombre  # Solo lectura

    @property
    def tarifa_hora(self):
        return self._tarifa_hora  # Solo lectura

    @property
    def disponible(self):
        return self._disponible  # Solo lectura; se cambia con marcar_disponible()

    def marcar_disponible(self, estado):
        """Cambia la disponibilidad del servicio (True/False)."""
        # Valida que el nuevo estado sea booleano
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
        # Debe ser un número (no texto, no None, no bool)
        if horas is None or isinstance(horas, bool) or not isinstance(horas, (int, float)):
            raise ServicioInvalidoError("La duración debe ser un número de horas")
        # Debe ser positiva
        if horas <= 0:
            raise ServicioInvalidoError("La duración debe ser mayor a 0 horas")
        # No puede superar el máximo del tipo de servicio (HORAS_MAX de cada clase)
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
        self.validar_parametros(horas)  # Primero se valida la duración (polimórfico)
        # Se valida que impuesto y descuento sean números entre 0 y 1
        for nombre, valor in (("impuesto", impuesto), ("descuento", descuento)):
            if isinstance(valor, bool) or not isinstance(valor, (int, float)) or not (0 <= valor <= 1):
                raise CalculoInconsistenteError(
                    f"El {nombre} debe ser un valor entre 0 y 1 (recibido: {valor!r})"
                )
        base = self._costo_base(horas)  # Cada hija calcula su costo base a su manera
        # Un costo base no positivo indica un cálculo inconsistente
        if base <= 0:
            raise CalculoInconsistenteError("El costo base calculado no es válido")
        # Se aplica primero el descuento y luego el impuesto
        total = base * (1 - descuento) * (1 + impuesto)
        return round(total, 2)  # Se redondea a 2 decimales

    def desglose(self, horas, impuesto=0.0, descuento=0.0):
        """Devuelve un diccionario con el detalle del cálculo del costo."""
        total = self.calcular_costo(horas, impuesto, descuento)  # Valida y calcula el total
        base = self._costo_base(horas)
        return {
            "base": round(base, 2),  # Costo antes de descuento e impuesto
            "descuento": round(base * descuento, 2),  # Valor descontado
            "impuesto": round(base * (1 - descuento) * impuesto, 2),  # Valor del impuesto
            "total": total,  # Costo final
        }

    # ---------- Creación segura (try/except/else/finally) ----------
    @classmethod
    def crear_seguro(cls, *args, **kwargs):
        """Crea un servicio sin detener el programa si los parámetros son inválidos."""
        servicio = None  # Si algo falla, se devolverá None
        try:
            servicio = cls(*args, **kwargs)  # Intenta crear el servicio de la clase que llama
        except ServicioInvalidoError as error:
            # Parámetros con valores inválidos
            logger.error("Fallo en crear_seguro (%s): %s | Causa: %s", cls.__name__, error, error.__cause__)
            print(f"[ERROR] {error} -> Causa: {error.__cause__}")
        except TypeError as error:  # Parámetros faltantes o sobrantes
            logger.error("Parámetros incorrectos al crear %s: %s", cls.__name__, error)
            print(f"[ERROR] Parámetros incorrectos para {cls.__name__}: {error}")
        else:
            # Solo si no hubo excepción
            print(f"[OK] Servicio creado: {servicio}")
        finally:
            # Se ejecuta siempre
            logger.info("Intento de creación de %s finalizado", cls.__name__)
        return servicio

    def __repr__(self):
        # Representación técnica, útil al depurar
        return f"{type(self).__name__}(id={self.id}, nombre='{self._nombre}')"


class ReservaSala(Servicio):
    """Reserva de salas de reuniones o capacitación."""

    HORAS_MAX = 12  # Sobrescribe el límite: una sala se reserva máximo 12 horas
    CARGO_PROYECTOR_HORA = 20000  # Costo adicional por hora si se usa proyector

    def __init__(self, nombre, tarifa_hora, capacidad, con_proyector=False, disponible=True):
        # Se guardan los atributos propios antes de llamar al padre,
        # porque el padre invoca _validar_atributos_especificos()
        self._capacidad = capacidad
        self._con_proyector = con_proyector
        super().__init__(nombre, tarifa_hora, disponible)  # Valida y guarda los datos comunes

    def _validar_atributos_especificos(self):
        # Capacidad: entero entre 1 y 200 personas
        self._capacidad = self._validar_entero_en_rango(self._capacidad, "capacidad", 1, 200)
        # con_proyector debe ser True o False
        if not isinstance(self._con_proyector, bool):
            raise ServicioInvalidoError("'con_proyector' debe ser True o False")

    def _costo_base(self, horas):
        costo = self._tarifa_hora * horas  # Tarifa por hora × horas
        if self._con_proyector:
            costo += self.CARGO_PROYECTOR_HORA * horas  # Suma el cargo del proyector
        return costo

    def describir(self):
        # Texto que describe la sala (sobrescribe el método abstracto)
        extra = "con proyector" if self._con_proyector else "sin proyector"
        return (f"Sala #{self.id} | {self._nombre} | Capacidad: {self._capacidad} personas | "
                f"{extra} | ${self._tarifa_hora:,.0f}/hora")


class AlquilerEquipo(Servicio):
    """Alquiler de equipos tecnológicos."""

    HORAS_MAX = 72  # Un equipo se puede alquilar hasta 72 horas (3 días)
    RECARGO_SEGURO = 0.05  # 5 % de seguro sobre el alquiler

    def __init__(self, nombre, tarifa_hora, tipo_equipo, cantidad=1, disponible=True):
        # Atributos propios guardados antes de llamar al constructor del padre
        self._tipo_equipo = tipo_equipo
        self._cantidad = cantidad
        super().__init__(nombre, tarifa_hora, disponible)

    def _validar_atributos_especificos(self):
        # El tipo de equipo debe ser texto de al menos 3 caracteres
        self._tipo_equipo = self._validar_texto(self._tipo_equipo, "tipo de equipo")
        # La cantidad debe ser un entero entre 1 y 50
        self._cantidad = self._validar_entero_en_rango(self._cantidad, "cantidad", 1, 50)

    def _costo_base(self, horas):
        # Tarifa × horas × cantidad de equipos, más el 5 % de seguro
        return self._tarifa_hora * horas * self._cantidad * (1 + self.RECARGO_SEGURO)

    def describir(self):
        # Texto que describe el alquiler (sobrescribe el método abstracto)
        return (f"Equipo #{self.id} | {self._nombre} | Tipo: {self._tipo_equipo} | "
                f"Cantidad: {self._cantidad} | ${self._tarifa_hora:,.0f}/hora c/u (incluye seguro 5%)")


class Asesoria(Servicio):
    """Asesoría especializada con un profesional junior o senior."""

    HORAS_MAX = 8  # Una asesoría dura máximo 8 horas
    MULTIPLICADORES = {"junior": 1.0, "senior": 1.5}  # El nivel senior cuesta 50 % más

    def __init__(self, nombre, tarifa_hora, especialidad, nivel="junior", disponible=True):
        # Atributos propios guardados antes de llamar al constructor del padre
        self._especialidad = especialidad
        self._nivel = nivel
        super().__init__(nombre, tarifa_hora, disponible)

    def _validar_atributos_especificos(self):
        # La especialidad debe ser texto de al menos 3 caracteres
        self._especialidad = self._validar_texto(self._especialidad, "especialidad")
        # El nivel solo puede ser "junior" o "senior" (sin importar mayúsculas)
        if not isinstance(self._nivel, str) or self._nivel.lower() not in self.MULTIPLICADORES:
            raise ServicioInvalidoError("El nivel debe ser 'junior' o 'senior'")
        self._nivel = self._nivel.lower()  # Se normaliza a minúsculas

    def _costo_base(self, horas):
        # Tarifa × horas × multiplicador del nivel
        return self._tarifa_hora * horas * self.MULTIPLICADORES[self._nivel]

    def validar_parametros(self, horas):
        super().validar_parametros(horas)  # Reutiliza la validación general
        # Regla propia: la asesoría mínima es de media hora
        if horas < 0.5:
            raise ServicioInvalidoError("La asesoría mínima es de 0.5 horas")
        return True

    def describir(self):
        # Texto que describe la asesoría (sobrescribe el método abstracto)
        return (f"Asesoría #{self.id} | {self._nombre} | Especialidad: {self._especialidad} | "
                f"Nivel: {self._nivel} | ${self._tarifa_hora:,.0f}/hora")
