# Simulador de Contagio con Grid File

Este proyecto es una simulación interactiva de propagación de contagios desarrollada en Python utilizando `pygame`. Su propósito principal es demostrar la implementación y eficiencia de una estructura de datos espacial **Grid File** para el manejo de colisiones y consultas de rango en tiempo real.

## Características

- **Simulación de Agentes**: Cientos de agentes moviéndose independientemente.
- **Sistema de Infección**: Propagación de estado (Sano -> Infectado) basada en proximidad.
- **Estructura de Datos Grid File**:
  - Indexación espacial dinámica.
  - División de "buckets" (cubos) basada en densidad (Split policies).
  - Visualización en tiempo real de las líneas de división de la grilla.
- **Interactividad**:
  - **Click Izquierdo**: Inyectar nuevos agentes infectados en la posición del cursor.
  - **Click Derecho + Arrastre**: Realizar una "Query de Rango" para contar agentes en un área específica.
- **Obstáculos**: Paredes y zonas de rebote.
- **Estadísticas en Tiempo Real**: Visualización de conteo de agentes, buckets, profundidad de la grilla y utilización.
- **Gráfico de Historial**: Curva de infectados vs sanos actualizada en vivo.

## Estructura del Proyecto

El proyecto sigue un patrón de diseño MVC (Modelo-Vista-Controlador) simplificado:

- `main.py`: **Controlador**. Punto de entrada. Maneja el bucle principal, eventos de usuario y actualiza la lógica de la simulación.
- `model.py`: **Modelo**. Contiene la lógica de los datos:
  - `Agente`: Entidad móvil.
  - `Obstaculo`: Paredes estáticas.
  - `GridFile` y `GridBucket`: Implementación de la estructura de datos espacial.
- `view.py`: **Vista**. Maneja la renderización con Pygame, dibujando el grid, agentes, UI y gráficos.

## Requisitos

- Python 3.x
- Pygame

## Instalación

1. Clona este repositorio:
   ```bash
   git clone https://github.com/tu-usuario/simulador-contagio.git
   ```
2. Navega al directorio del proyecto:
   ```bash
   cd simulador-contagio
   ```
3. Instala las dependencias:
   ```bash
   pip install pygame
   ```

## Uso

Ejecuta el archivo principal para iniciar la simulación:

```bash
python main.py
```

### Controles
- **Mouse**: Mueve el cursor para interactuar.
- **Click Izquierdo**: Añade agentes infectados ("pacientes cero") en la posición.
- **Click Derecho (Arrastrar)**: Selecciona un área rectangular para ver cuántos agentes hay dentro (demostración de `query_range`).
- **Cerrar Ventana**: Termina la simulación.

## Personalización

Puedes ajustar los parámetros de la simulación editando las constantes en `main.py`:

- `SIM_WIDTH` / `SIM_HEIGHT`: Dimensiones de la simulación.
- `BUCKET_CAPACITY`: Capacidad máxima de un bucket antes de dividirse (Grid File).
