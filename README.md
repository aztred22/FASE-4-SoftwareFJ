# Software FJ – Sistema Integral de Gestión de Clientes, Servicios y Reservas

Proyecto de la Fase 4 del curso **Programación (213023)**, UNAD – Ingeniería de Sistemas.
Aplicación orientada a objetos, **sin bases de datos**: toda la información vive en objetos y
listas en memoria; el único archivo que se escribe es `logs.txt` (registro de eventos y errores).

## Requisitos
- Python 3.8 o superior. No requiere librerías externas.

## Cómo ejecutar
```
python main.py
```
La simulación ejecuta 23 operaciones (válidas e inválidas) y genera/actualiza `logs.txt`.
El programa no se detiene ante ningún error.

## Estructura del proyecto

| Archivo | Contenido |
|---|---|
| `excepciones.py` | Excepciones personalizadas. Base `SoftwareFJError` y las hijas `ClienteInvalidoError`, `ServicioInvalidoError`, `ServicioNoDisponibleError`, `ReservaInvalidaError`, `OperacionNoPermitidaError`, `CalculoInconsistenteError`. |
| `logger.py` | `configurar_logger()`: configura el archivo `logs.txt` (fecha, nivel, mensaje). |
| `entidad.py` | Clase abstracta `Entidad` (id + método abstracto `describir()`). Raíz de la herencia. |
| `cliente.py` | `Cliente(Entidad)`: datos personales privados con validación estricta, lista interna de reservas y `crear_seguro()`. |
| `servicios.py` | `Servicio(Entidad)` abstracta y tres servicios: `ReservaSala`, `AlquilerEquipo` y `Asesoria`. |
| `reserva.py` | `Reserva(Entidad)`: integra cliente, servicio, duración y estado; `confirmar()`, `cancelar()` y `procesar()`. |
| `main.py` | Simulación de 23 operaciones con éxitos y fallos controlados. |
| `fase_4.py` | Notas de la actividad sobre comandos de Git (no forma parte del sistema). |
| `logs.txt` | Se genera al ejecutar. No se sube al repositorio (`.gitignore`). |

## Conceptos de POO aplicados
- **Abstracción:** `Entidad` y `Servicio` son abstractas y no se pueden instanciar.
- **Herencia:** `Cliente`, `Servicio` y `Reserva` heredan de `Entidad`; las tres clases de servicio heredan de `Servicio`.
- **Polimorfismo:** cada servicio sobrescribe `_costo_base()`, `describir()`, `validar_parametros()` y `_validar_atributos_especificos()`.
- **Encapsulación:** atributos privados o protegidos con propiedades que validan los datos.
- **Sobrecarga:** `calcular_costo(horas, impuesto=0.0, descuento=0.0)` y `desglose(...)` aceptan varias combinaciones de parámetros (solo horas; horas + impuesto; horas + impuesto + descuento). En Python se logra con parámetros opcionales.

## Manejo de excepciones
- Excepciones personalizadas con jerarquía propia.
- `try/except/else/finally` en `Cliente.crear_seguro()`, `Servicio.crear_seguro()`, `Reserva.crear_segura()` y `Reserva.procesar()`.
- Encadenamiento con `raise ... from ...` (por ejemplo, un `ServicioInvalidoError` se convierte en `ReservaInvalidaError` conservando la causa).
- Todos los errores y eventos relevantes quedan registrados en `logs.txt`.

## Servicios disponibles
| Servicio | Regla de costo | Duración máxima |
|---|---|---|
| `ReservaSala` | tarifa × horas (+ cargo de proyector por hora si aplica) | 12 h |
| `AlquilerEquipo` | tarifa × horas × cantidad + 5 % de seguro | 72 h |
| `Asesoria` | tarifa × horas × multiplicador (junior 1.0 / senior 1.5) | 8 h (mínimo 0.5 h) |

## Estados de una reserva
`PENDIENTE` → `CONFIRMADA` → (opcionalmente) `CANCELADA`. No se puede confirmar una reserva cancelada ni cancelar dos veces la misma.

## Trabajo colaborativo
Intente comunicarme durante varias semanas con los compañeros para consolidar el proyecto de forma colaborativa, mas sin embargo debido a la negativa, decidi entregarlo de forma individual, para no retrasarme en los tiempos de entrega de proyecto.

