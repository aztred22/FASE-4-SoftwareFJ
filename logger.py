"""Configuración central del archivo de logs de Software FJ."""
import logging  # Módulo estándar de Python para registrar eventos y errores

def configurar_logger(nombre_archivo="logs.txt"):
    # Obtiene (o crea) el logger llamado "SoftwareFJ"; todas las clases usan este mismo nombre
    logger = logging.getLogger("SoftwareFJ")
    # Nivel INFO: se registran eventos informativos, advertencias y errores
    logger.setLevel(logging.INFO)

    ##### Evita duplicar si se llama más de una vez#####
    # Si ya tiene un manejador, no se agrega otro (evitaría líneas repetidas en el log)
    if not logger.handlers:
        # El manejador escribe los mensajes en el archivo logs.txt (en UTF-8 para admitir tildes)
        manejador = logging.FileHandler(nombre_archivo, encoding="utf-8")
        # Formato de cada línea: fecha y hora | nivel | nombre del logger | mensaje
        formato = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
        )
        manejador.setFormatter(formato)  # Asocia el formato al manejador
        logger.addHandler(manejador)  # Conecta el manejador al logger

    return logger  # Devuelve el logger ya configurado
