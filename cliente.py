"""Clase Cliente del sistema Software FJ."""
import re  # Expresiones regulares: sirven para validar el formato del nombre y del correo
import logging  # Para registrar eventos y errores en logs.txt

from entidad import Entidad  # Clase abstracta de la que hereda Cliente
from excepciones import ClienteInvalidoError  # Excepción propia para datos de cliente inválidos

# Se obtiene el logger "SoftwareFJ" (ya configurado en main.py mediante configurar_logger)
logger = logging.getLogger("SoftwareFJ")


class Cliente(Entidad):  # Herencia: Cliente es un tipo de Entidad
    """Representa a un cliente de Software FJ.

    Los datos personales son privados y solo se
    acceden o modifican mediante propiedades con validación estricta.
    """

    _contador_id = 0  # Genera identificadores únicos automáticamente (compartido por toda la clase)

    def __init__(self, nombre, documento, correo, telefono):
        try:
            # Se declaran los atributos privados (doble guion bajo = encapsulación)
            self.__nombre = None
            self.__documento = None
            self.__correo = None
            self.__telefono = None

            # Al asignar, se ejecutan los setters, que validan cada dato
            self.nombre = nombre
            self.documento = documento
            self.correo = correo
            self.telefono = telefono
        except ClienteInvalidoError as error:
            # Si algún dato es inválido: se registra el error en el log...
            logger.error("No se pudo crear el cliente: %s", error)
            # ...y se lanza una nueva excepción conservando la original como causa
            raise ClienteInvalidoError(
                "Registro de cliente rechazado por datos inválidos"
            ) from error  # Encadenamiento de excepciones

        # Solo si todo es válido se asigna un id nuevo
        Cliente._contador_id += 1
        self.__id_cliente = Cliente._contador_id
        super().__init__(self.__id_cliente)  # Llama al constructor de Entidad con el id
        self.__reservas = []  # Lista interna de reservas del cliente
        logger.info("Cliente creado: ID %s - %s", self.__id_cliente, self.__nombre)

    # ########Propiedades###########
    @property
    def id_cliente(self):
        # Solo lectura: el id no se puede cambiar desde fuera
        return self.__id_cliente

    @property
    def nombre(self):
        return self.__nombre  # Getter: devuelve el nombre

    @nombre.setter
    def nombre(self, valor):
        # Debe existir y ser texto
        if valor is None or not isinstance(valor, str):
            raise ClienteInvalidoError("El nombre es obligatorio y debe ser texto")
        valor = valor.strip()  # Quita espacios al inicio y al final
        # Mínimo 3 caracteres
        if len(valor) < 3:
            raise ClienteInvalidoError("El nombre debe tener al menos 3 caracteres")
        # Solo letras (con tildes y ñ) y espacios
        if not re.fullmatch(r"[A-Za-zÁÉÍÓÚáéíóúÑñÜü ]+", valor):
            raise ClienteInvalidoError("El nombre solo puede contener letras y espacios")
        self.__nombre = valor.title()  # Guarda con la primera letra de cada palabra en mayúscula

    @property
    def documento(self):
        return self.__documento  # Getter: devuelve el documento

    @documento.setter
    def documento(self, valor):
        # El documento es obligatorio
        if valor is None:
            raise ClienteInvalidoError("El documento es obligatorio")
        valor = str(valor).strip()  # Se convierte a texto y se limpian espacios
        # Debe ser solo dígitos y tener entre 6 y 12 caracteres
        if not valor.isdigit() or not (6 <= len(valor) <= 12):
            raise ClienteInvalidoError(
                "El documento debe ser numérico y tener entre 6 y 12 dígitos"
            )
        self.__documento = valor

    @property
    def correo(self):
        return self.__correo  # Getter: devuelve el correo

    @correo.setter
    def correo(self, valor):
        # Debe existir y ser texto
        if valor is None or not isinstance(valor, str):
            raise ClienteInvalidoError("El correo es obligatorio y debe ser texto")
        valor = valor.strip().lower()  # Se normaliza: sin espacios y en minúsculas
        # Formato básico: algo@dominio.extensión
        if not re.fullmatch(r"[\w\.\-]+@[\w\-]+(\.[\w\-]+)+", valor):
            raise ClienteInvalidoError(f"Formato de correo inválido: '{valor}'")
        self.__correo = valor

    @property
    def telefono(self):
        return self.__telefono  # Getter: devuelve el teléfono

    @telefono.setter
    def telefono(self, valor):
        # El teléfono es obligatorio
        if valor is None:
            raise ClienteInvalidoError("El teléfono es obligatorio")
        valor = str(valor).strip().replace(" ", "")  # Quita espacios internos y externos
        # Debe tener exactamente 10 dígitos numéricos
        if not valor.isdigit() or len(valor) != 10:
            raise ClienteInvalidoError("El teléfono debe tener exactamente 10 dígitos")
        self.__telefono = valor

    # Manejo de la lista interna de reservas 
    def agregar_reserva(self, reserva):
        # No se permite asociar una reserva nula
        if reserva is None:
            raise ClienteInvalidoError("No se puede asociar una reserva nula")
        self.__reservas.append(reserva)  # Agrega la reserva a la lista interna

    def obtener_reservas(self):
        return list(self.__reservas)  ###### Copia y protege la lista interna

    # #####Creación segura (try/except/else/finally) ##########
    @classmethod
    def crear_seguro(cls, nombre, documento, correo, telefono):
        """Intenta crear un cliente sin detener el programa si hay errores."""
        cliente = None  # Si algo falla, se devolverá None
        try:
            cliente = cls(nombre, documento, correo, telefono)  # Intenta crear el cliente
        except ClienteInvalidoError as error:
            # Captura el error: lo registra y lo muestra, pero el programa sigue
            logger.error("Fallo en crear_seguro: %s | Causa: %s", error, error.__cause__)
            print(f"[ERROR] {error} -> Causa: {error.__cause__}")
        else:
            # Solo se ejecuta si NO hubo excepción
            print(f"[OK] Cliente registrado: {cliente}")
        finally:
            # Se ejecuta siempre, haya o no error
            logger.info("Intento de registro de cliente finalizado")
        return cliente

    # ######## Representaciones #########
    def describir(self):
        # Implementa el método abstracto de Entidad (polimorfismo)
        return (f"Cliente #{self.__id_cliente} | {self.__nombre} | "
                f"Doc: {self.__documento} | {self.__correo} | Tel: {self.__telefono}")

    def __repr__(self):
        # Representación técnica del objeto (útil al depurar)
        return f"Cliente(id={self.__id_cliente}, nombre='{self.__nombre}')"
