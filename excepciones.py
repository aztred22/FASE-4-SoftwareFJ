# Función de este archivo: concentrar todos los errores personalizados del sistema en un solo lugar.
"""Excepciones personalizadas del sistema Software FJ."""

# Excepción base: todas las demás heredan de ella, así que con
# "except SoftwareFJError" se puede capturar cualquier error propio del sistema.
class SoftwareFJError(Exception):
    """Excepción base de todo el sistema."""
    pass  # No necesita lógica: solo da nombre a la jerarquía de errores


# Se lanza desde Cliente cuando el nombre, documento, correo o teléfono no son válidos
class ClienteInvalidoError(SoftwareFJError):
    """Datos inválidos o faltantes de un cliente."""
    pass


# Se lanza desde Servicio y sus hijas cuando los parámetros de creación o la duración son incorrectos
class ServicioInvalidoError(SoftwareFJError):
    """Parámetros inválidos al crear o configurar un servicio."""
    pass


# Se lanza desde Reserva cuando se intenta confirmar un servicio marcado como no disponible
class ServicioNoDisponibleError(SoftwareFJError):
    """El servicio solicitado no está disponible."""
    pass


# Se lanza desde Reserva cuando el cliente, el servicio o la duración recibidos no son válidos
class ReservaInvalidaError(SoftwareFJError):
    """Intento de reserva incorrecto o con datos inconsistentes."""
    pass


# Se lanza desde Reserva cuando la operación no corresponde al estado actual
class OperacionNoPermitidaError(SoftwareFJError):
    """Operación no permitida en el estado actual (ej. cancelar una reserva ya cancelada)."""
    pass


# Se lanza desde Servicio cuando el impuesto, el descuento o el costo calculado no tienen sentido
class CalculoInconsistenteError(SoftwareFJError):
    """Error en cálculos de costos, impuestos o descuentos."""
    pass
