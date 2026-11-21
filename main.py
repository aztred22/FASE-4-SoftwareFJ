"""Punto de entrada del sistema Software FJ.

Simula 20 operaciones (válidas e inválidas) sobre clientes, servicios y reservas.
El programa nunca se detiene ante un error: cada operación se ejecuta de forma
aislada, los errores se muestran en consola y se registran en logs.txt.
"""
from logger import configurar_logger

logger = configurar_logger()  # Se configura antes de importar las demás clases

from cliente import Cliente
from excepciones import SoftwareFJError
from reserva import Reserva
from servicios import Asesoria, AlquilerEquipo, ReservaSala

resultados = {"exitosas": 0, "con_error": 0}


def ejecutar(numero, titulo, operacion):
    """Ejecuta una operación sin permitir que un error detenga la simulación."""
    print(f"\n--- Operación {numero}: {titulo} ---")
    logger.info("Operación %s: %s", numero, titulo)
    try:
        operacion()
    except SoftwareFJError as error:
        resultados["con_error"] += 1
        logger.error("Operación %s falló (error controlado): %s | Causa: %s", numero, error, error.__cause__)
        print(f"[ERROR CONTROLADO] {type(error).__name__}: {error}")
    except Exception as error:  # Cualquier error inesperado también se contiene
        resultados["con_error"] += 1
        logger.exception("Operación %s falló (error inesperado): %s", numero, error)
        print(f"[ERROR INESPERADO] {type(error).__name__}: {error}")
    else:
        resultados["exitosas"] += 1
    finally:
        logger.info("Operación %s finalizada", numero)


def main():
    logger.info("=== Inicio de la simulación ===")
    print("=== SOFTWARE FJ: simulación de operaciones ===")

    # Estado compartido entre operaciones
    datos = {}

    # ---------------- CLIENTES ----------------
    def op_cliente_valido_1():
        datos["juan"] = Cliente.crear_seguro("Juan Pérez", "1012345678", "juan@correo.com", "3001234567")

    def op_cliente_valido_2():
        datos["ana"] = Cliente.crear_seguro("ana gómez", "52345678", "ana.gomez@correo.com", "3109876543")

    def op_cliente_invalido():
        datos["malo"] = Cliente.crear_seguro("", "abc", "correo-malo", "123")

    def op_cliente_parametros_faltantes():
        datos["nulo"] = Cliente.crear_seguro(None, None, None, None)

    # ---------------- SERVICIOS ----------------
    def op_sala_valida():
        datos["sala"] = ReservaSala.crear_seguro("Sala Ejecutiva", 80000, 12, con_proyector=True)

    def op_equipo_valido():
        datos["equipo"] = AlquilerEquipo.crear_seguro("Portátiles de Alto Rendimiento", 15000, "Portátil", cantidad=4)

    def op_asesoria_valida():
        datos["asesoria"] = Asesoria.crear_seguro("Asesoría en Arquitectura de Software", 120000, "Arquitectura", "senior")

    def op_servicio_invalido():
        ReservaSala.crear_seguro("Sa", -5000, 0)  # Nombre corto, tarifa negativa, capacidad 0

    def op_servicio_parametros_faltantes():
        AlquilerEquipo.crear_seguro("Proyectores")  # Faltan tarifa y tipo de equipo

    # ---------------- RESERVAS ----------------
    def op_reserva_exitosa():
        reserva = Reserva.crear_segura(datos["juan"], datos["sala"], 3)
        datos["reserva_juan"] = reserva
        reserva.procesar()  # Con IVA del 19 %

    def op_reserva_con_descuento():
        reserva = Reserva.crear_segura(datos["ana"], datos["equipo"], 10)
        datos["reserva_ana"] = reserva
        reserva.procesar(impuesto=0.19, descuento=0.10)

    def op_reserva_duracion_invalida():
        Reserva.crear_segura(datos["juan"], datos["sala"], 20)  # Excede el máximo de 12 h

    def op_reserva_cliente_invalido():
        Reserva.crear_segura(datos["malo"], datos["sala"], 2)  # El cliente nunca se creó (None)

    def op_servicio_no_disponible():
        datos["asesoria"].marcar_disponible(False)
        reserva = Reserva.crear_segura(datos["ana"], datos["asesoria"], 2)
        reserva.procesar()  # Falla: servicio no disponible

    def op_cancelar_reserva():
        datos["reserva_ana"].cancelar()
        print(f"[OK] {datos['reserva_ana']}")

    def op_cancelar_dos_veces():
        datos["reserva_ana"].cancelar()  # Operación no permitida: ya estaba cancelada

    def op_confirmar_reserva_cancelada():
        datos["reserva_ana"].confirmar()  # Operación no permitida

    # ---------------- CÁLCULOS ----------------
    def op_calculo_inconsistente():
        datos["sala"].calcular_costo(2, impuesto=0.19, descuento=1.5)  # Descuento de 150 %

    def op_parametro_tipo_incorrecto():
        datos["sala"].calcular_costo("tres horas")  # Tipo incorrecto

    def op_error_inesperado():
        datos["malo"].obtener_reservas()  # El cliente es None: AttributeError no previsto

    def op_sobrecarga_costos():
        sala = datos["sala"]
        print(f"Solo horas (4 h):              ${sala.calcular_costo(4):,.2f}")
        print(f"Horas + impuesto 19 %:         ${sala.calcular_costo(4, 0.19):,.2f}")
        print(f"Horas + impuesto + descuento:  ${sala.calcular_costo(4, 0.19, 0.10):,.2f}")
        print(f"Desglose: {sala.desglose(4, 0.19, 0.10)}")

    def op_polimorfismo():
        for servicio in (datos["sala"], datos["equipo"], datos["asesoria"]):
            print(servicio.describir())
            print(f"   Costo de 2 h con IVA: ${servicio.calcular_costo(2, 0.19):,.2f}")

    def op_resumen_cliente():
        juan = datos["juan"]
        print(juan.describir())
        for reserva in juan.obtener_reservas():
            print("  ->", reserva.describir())

    operaciones = [
        ("Registro válido de cliente (Juan)", op_cliente_valido_1),
        ("Registro válido de cliente (Ana)", op_cliente_valido_2),
        ("Registro INVÁLIDO de cliente (datos incorrectos)", op_cliente_invalido),
        ("Registro INVÁLIDO de cliente (parámetros faltantes)", op_cliente_parametros_faltantes),
        ("Creación válida de servicio: sala", op_sala_valida),
        ("Creación válida de servicio: equipo", op_equipo_valido),
        ("Creación válida de servicio: asesoría", op_asesoria_valida),
        ("Creación INVÁLIDA de servicio (parámetros incorrectos)", op_servicio_invalido),
        ("Creación INVÁLIDA de servicio (parámetros faltantes)", op_servicio_parametros_faltantes),
        ("Reserva exitosa con impuesto", op_reserva_exitosa),
        ("Reserva exitosa con impuesto y descuento", op_reserva_con_descuento),
        ("Reserva FALLIDA: duración inválida", op_reserva_duracion_invalida),
        ("Reserva FALLIDA: cliente inexistente", op_reserva_cliente_invalido),
        ("Reserva FALLIDA: servicio no disponible", op_servicio_no_disponible),
        ("Cancelación de una reserva", op_cancelar_reserva),
        ("Cancelar dos veces la misma reserva (no permitido)", op_cancelar_dos_veces),
        ("Confirmar una reserva cancelada (no permitido)", op_confirmar_reserva_cancelada),
        ("Cálculo inconsistente (descuento mayor al 100 %)", op_calculo_inconsistente),
        ("Parámetro de tipo incorrecto (horas como texto)", op_parametro_tipo_incorrecto),
        ("Error INESPERADO (consultar un cliente que no se creó)", op_error_inesperado),
        ("Métodos sobrecargados: variantes del cálculo de costos", op_sobrecarga_costos),
        ("Polimorfismo: describir y calcular costos de cada servicio", op_polimorfismo),
        ("Resumen de reservas de un cliente", op_resumen_cliente),
    ]

    for numero, (titulo, operacion) in enumerate(operaciones, start=1):
        ejecutar(numero, titulo, operacion)

    print("\n=== RESUMEN ===")
    print(f"Operaciones ejecutadas: {len(operaciones)}")
    print(f"Terminaron normalmente (incluye errores ya manejados dentro de la operación): {resultados['exitosas']}")
    print(f"Errores capturados por el controlador de la simulación: {resultados['con_error']}")
    print("El programa continuó funcionando en todo momento. Revise logs.txt para ver el detalle.")
    logger.info("=== Fin de la simulación ===")


if __name__ == "__main__":
    main()
