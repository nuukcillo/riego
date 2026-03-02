# Riego

Aplicación para monitorizar y analizar datos de riego mediante web scraping, almacenamiento en base de datos y notificaciones automáticas.

## Estructura del Proyecto

### Archivos Principales

- `webscrapU.py`: Script principal que realiza el web scraping y guarda los datos en archivos CSV.
- `webscrapBD.py`: Script que realiza el scraping y guarda los datos directamente en la base de datos SQLite.
- `riegosemanal.py`: Procesa los datos de riego semanal desde la base de datos y genera informes.
- `avisosriego.py`: Detecta riegos anormalmente altos y genera avisos.
- `telegramutils.py`: Funciones para enviar mensajes y avisos a Telegram.
- `create_db.py`: Script para crear y poblar la base de datos SQLite con datos iniciales.
- `delete_csv_files.ps1`: Script de PowerShell para eliminar archivos CSV.
- `run_webscrapU.sh`: Script de shell para ejecutar `webscrapU.py` en sistemas Linux.

### Directorios

- `database/`: Scripts y archivos relacionados con la base de datos.
  - `create_db.py`: Script para crear y poblar la base de datos SQLite.
  - `riego.db`: Archivo de la base de datos SQLite.
- `csv_files/`: Directorio donde se almacenan los archivos CSV generados por `webscrapU.py`.

### Archivos de Configuración

- `config.json`: Archivo de configuración con URLs y parámetros para el scraping.
- `.github/workflows/python-app.yml`: Workflow de GitHub Actions para ejecución automática y actualización de la base de datos.

## Instalación

1. Clona el repositorio:
    ```sh
    git clone https://github.com/tu_usuario/riego.git
    cd riego
    ```

2. Crea y activa un entorno virtual:
    ```sh
    python -m venv .venv
    source .venv/bin/activate  # En Windows: .venv\Scripts\activate
    ```

3. Instala las dependencias:
    ```sh
    pip install -r requirements.txt
    ```

4. Crea la base de datos y puebla los datos iniciales:
    ```sh
    python database/create_db.py
    ```

## Uso

### Ejecutar el Web Scraping

Para guardar los datos en archivos CSV:
```sh
python webscrapU.py
```

Para guardar los datos directamente en la base de datos:
```sh
python webscrapBD.py [--parse_all] [--month_year MMYYYY]
```

**Argumentos:**
- `--parse_all`: (Opcional) Si se incluye, analiza todas las filas de la tabla HTML en lugar de solo la última fila. Por defecto, solo se analiza la última fila.
- `--month_year MMYYYY`: (Opcional) Especifica el mes y el año para extraer los datos. El formato debe ser `MMYYYY` (ejemplo: `042024` para Abril de 2024). Si no se especifica, se utiliza el mes y año actual.

Ejemplo para analizar todos los datos de Mayo de 2023:
```sh
python webscrapBD.py --parse_all --month_year 052023
```

### Procesar Datos de Riego Semanal

Para procesar los datos de riego semanal y generar un informe:
```sh
python riegosemanal.py
```

### Detectar Riegos Anormales

Para detectar riegos anormalmente altos comparando el riego de hoy con la media de la última semana:
```sh
python avisosriego.py
```

### Envío de Avisos y Reportes a Telegram

El sistema envía automáticamente reportes diarios y avisos de riego anormal al canal de Telegram configurado en `config.json` o mediante variables de entorno `TELEGRAM_TOKEN` y `TELEGRAM_CHAT_ID`.

### Eliminar Archivos CSV

Para eliminar los archivos CSV generados:
```sh
powershell -File delete_csv_files.ps1 -directory "path\to\csv_files"
```

### Dockerización

Para ejecutar la aplicación en un contenedor Docker:

1. Construye la imagen Docker:
    ```sh
    docker build -t riego .
    ```

2. Ejecuta el contenedor:
    ```sh
    docker run -d --name riego_container riego
    ```

## Automatización y CI/CD

### GitHub Actions

El workflow `.github/workflows/python-app.yml` permite ejecutar el scraping y actualizar la base de datos automáticamente. Al finalizar el scraping, los cambios en la base de datos se hacen commit y push al repositorio.

### Programación de Tareas

#### Windows

Para programar la ejecución diaria del script `webscrapU.py` a las 00:05 en Windows, usa el Programador de Tareas.

#### Linux

Para programar la ejecución diaria del script `webscrapU.py` a las 00:05 en Linux, usa `cron`:
```sh
crontab -e
```
Agrega la siguiente línea:
```sh
5 0 * * * /path/to/your/project/run_webscrapU.sh
```

## Contribuciones

Las contribuciones son bienvenidas. Por favor, abre un issue o un pull request para discutir cualquier cambio que te gustaría hacer.

## Licencia

Este proyecto está licenciado bajo la Licencia MIT. Consulta el archivo `LICENSE` para más detalles.
