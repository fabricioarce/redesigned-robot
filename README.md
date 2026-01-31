# XP Moodle Automation

Este proyecto automatiza la navegación en la plataforma Moodle del Colegio Científico de Costa Rica (Sede San Carlos) utilizando Playwright.

## Funcionalidades

- **Inicio de Sesión Automático:** Accede con credenciales preconfiguradas.
- **Navegación Robusta:** Recorre todas las secciones y actividades de un curso específico (ID 77).
- **Sistema Anti-Ruido:** Detecta y cierra automáticamente ventanas emergentes y pop-ups.
- **Manejo de Sidebar:** Abre el índice del curso automáticamente si está cerrado.
- **Círculo de Navegación:** Ciclo infinito entre "Mis cursos" y el contenido del curso.

## Requisitos

- Python 3.10 o superior.
- Playwright.

## Instalación

1.  Clona el repositorio o descarga los archivos.
2.  Crea un entorno virtual (opcional pero recomendado):
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # En Linux
    ```
3.  Instala las dependencias:
    ```bash
    pip install playwright
    ```
4.  Instala los navegadores de Playwright:
    ```bash
    playwright install chromium
    ```

## Uso

Para ejecutar el script principal:

```bash
python v1.py
```

*Nota: Por defecto, el script está configurado en modo `headless=True` (sin ventana). Si deseas ver el proceso, cambia a `headless=False` en el archivo `v1.py`.*
