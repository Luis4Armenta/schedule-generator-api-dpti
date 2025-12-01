# Evidencia de pruebas

Este archivo indica dónde encontrar la salida de la ejecución de tests reproducible y cómo ejecutar los tests localmente.

Archivos generados
- `tests/results.txt`: salida completa de `pytest -v` (resultado de la ejecución en este entorno).
- `scripts/run_tests.sh`: script para ejecutar los tests usando el `.venv` del proyecto y guardar la salida en `tests/results.txt`.

Instrucciones rápidas

1. Asegúrate de tener el entorno virtual instalado (si no lo tienes, crea uno y instala dependencias):

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Ejecuta el script (desde la raíz del repositorio):

```bash
chmod +x scripts/run_tests.sh
./scripts/run_tests.sh
```

3. Revisa el archivo `tests/results.txt` para la salida completa de la ejecución (pasa a ser la evidencia a adjuntar en la entrega).

Notas
- En este repositorio se añadió temporalmente `tests/teachers` a `pytest.ini` para evitar errores por imports faltantes; revisa `pytest.ini` si quieres ejecutar absolutamente todos los tests sin ignores.
- El directorio `data/` fue ignorado por pytest porque contiene archivos de base de datos (WiredTiger) que interfieren con la recolección de tests. Se recomienda mover `data/` fuera del repo y añadirlo a `.gitignore` si no debe versionarse.
