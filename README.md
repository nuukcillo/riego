# Riego

Aplicación que hace webscrap para conseguir datos que luego se muestran en gráficas.

## Estructura del Proyecto

### Archivos Principales

- `webscrapU.py`: Script principal que realiza el web scraping y guarda los datos en archivos CSV.
- `riegosemanal.py`: Script que procesa los datos de riego semanal desde los archivos CSV y la base de datos.
- `create_db.py`: Script para crear y poblar la base de datos SQLite con datos iniciales.
- `delete_csv_files.ps1`: Script de PowerShell para eliminar archivos CSV.
- `run_webscrapU.sh`: Script de shell para ejecutar `webscrapU.py` en sistemas Linux.

### Directorios

- `database/`: Contiene scripts relacionados con la base de datos.
  - `create_db.py`: Script para crear y poblar la base de datos SQLite.
  - `database.db`: Archivo de la base de datos SQLite.
- `csv_files/`: Directorio donde se almacenan los archivos CSV generados por `webscrapU.py`.

### Archivos de Configuración

- `config.json`: Archivo de configuración que contiene URLs y otros parámetros necesarios para el web scraping.

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

Para ejecutar el script de web scraping y guardar los datos en archivos CSV:
```sh
python webscrapU.py
```

### Procesar Datos de Riego Semanal

Para procesar los datos de riego semanal y generar un informe:
```sh
python riegosemanal.py
```

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

## Programación de Tareas

### Windows

Para programar la ejecución diaria del script `webscrapU.py` a las 00:05 en Windows, usa el Programador de Tareas.

### Linux

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
