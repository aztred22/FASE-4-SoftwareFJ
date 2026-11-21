"""Configuración central del archivo de logs de Software FJ."""
import logging # Módulo estándar de Python para registrar eventos y errores

def configurar_logger(nombre_archivo="logs.txt"):
    # Obtiene (o crea) el logger llamado "SoftwareFJ"; todas las clases usan este mismo nombre
    logger = logging.getLogger("SoftwareFJ")
    # Nivel INFO: se registran eventos informativos, advertencias y errores
    logger.setLevel(logging.INFO)
##### Evita duplicar si se llama más de una vez#####
    # Si ya tiene un manejador, no se agrega otro (evitaría líneas repetidas en el log)
    if not logger.handlers:
        manejador = logging.FileHandler(nombre_archivo, encoding="utf-8")
        formato = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
        )
        manejador.setFormatter(formato)
        logger.addHandler(manejador)

    return logger
