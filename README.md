# 🔍 Búsqueda Ciega — DFS & BFS

Implementación completa de algoritmos de búsqueda no informada aplicados a tres problemas clásicos de IA, con interfaz gráfica y métricas de rendimiento.

---

## 📁 Estructura del Proyecto

```
practica_1/
├── algorithms/
│   ├── __init__.py
│   └── search.py          # DFS y BFS + medición de tiempo/memoria
├── problems/
│   ├── __init__.py
│   ├── maze.py            # Generación y solución de laberintos
│   ├── jugs.py            # Problema de las jarras
│   └── puzzle.py          # 8-Puzzle
├── gui/
│   ├── __init__.py
│   └── app.py             # Interfaz gráfica con Tkinter
├── tests/
│   └── test_algorithms.py # Tests unitarios con pytest
├── main.py                # Punto de entrada
├── Dockerfile             # Imagen Docker
├── docker-compose.yml     # Orquestación Docker
├── requirements.txt       # Dependencias
└── README.md
```

---

## 🚀 Cómo Ejecutar

### Opción 1: Directamente con Python (recomendado para desarrollo)

```bash
# Desde dentro de la carpeta practica_1:
cd practica_1
python main.py
```

**Requisito:** Python 3.8+ con Tkinter instalado.

- **Windows / Mac:** Tkinter viene incluido con Python.
- **Linux (Ubuntu/Debian):**
  ```bash
  sudo apt install python3-tk
  ```

### Opción 2: Con Docker (recomendado para entrega/reproducibilidad)

#### ¿Por qué Docker?
Docker empaqueta el código y todas las dependencias en un contenedor. Funciona igual en cualquier máquina sin instalar nada extra, ideal si no tienes experiencia con entornos virtuales.

#### Pasos en Linux/Mac:
```bash
# 1. Permitir conexiones X11 (para mostrar la ventana)
xhost +local:docker

# 2. Construir la imagen
docker compose build

# 3. Ejecutar la app
docker compose up
```

#### Solo ejecutar tests (sin GUI):
```bash
docker run --rm busqueda-ciega python -m pytest tests/ -v
```

#### En Windows:
Necesitas un servidor X11. Opciones:
- **VcXsrv** (gratuito): https://sourceforge.net/projects/vcxsrv/
- **X410** (de pago, más fácil)

---

## 🧪 Tests

```bash
# Sin Docker
python -m pytest tests/ -v

# Con cobertura
python -m pytest tests/ -v --cov=algorithms --cov=problems

# Con Docker
docker compose run busqueda-ciega python -m pytest tests/ -v
```

---

## 🔬 Algoritmos Implementados

### BFS — Búsqueda en Amplitud
- Usa una **cola (deque)** — FIFO
- **Garantiza** el camino más corto
- Mayor uso de memoria (expande nivel por nivel)
- Complejidad: O(b^d) tiempo y memoria

### DFS — Búsqueda en Profundidad
- Usa una **pila (list)** — LIFO
- **No garantiza** el camino óptimo
- Menor uso de memoria (explora una rama a la vez)
- Complejidad: O(b^m) tiempo, O(bm) memoria

---

## 🎮 Problemas Implementados

### A. Laberinto
- Generación con **Recursive Backtracker** (siempre resoluble)
- Tamaños: 10×10, 20×20, 50×50
- Animación del camino encontrado en tiempo real

### B. Jarras
- 6 movimientos posibles desde cada estado
- Presets clásicos + configuración manual
- Visualización gráfica del nivel de agua por paso

### C. 8-Puzzle
- Detección de estados irresolubles (paridad de inversiones)
- Navegación paso a paso con botones ◀ ▶
- Reproducción automática con ▶▶

---

## 📊 Métricas Medidas

| Métrica         | Descripción                              |
|----------------|------------------------------------------|
| Tiempo (ms)     | `time.perf_counter()` de alta resolución |
| Memoria (KB)    | `tracemalloc` — pico de memoria usada    |
| Nodos visitados | Contador en cada iteración del algoritmo |
| Pasos del camino| Longitud de la solución encontrada       |

---

## 📌 Notas de Diseño

- DFS usa **pila explícita** (no recursivo) para evitar `RecursionError` en laberintos grandes
- BFS garantiza solución óptima; DFS puede dar caminos más largos pero usa menos memoria en grafos profundos
- El 8-Puzzle con DFS tiene límite de profundidad 50 para evitar búsquedas infinitas
- El decorador `@measure` envuelve cada búsqueda para capturar métricas sin modificar los algoritmos
