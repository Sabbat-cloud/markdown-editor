-----

### `README.es.md`

````markdown
# Visual Markdown Editor - Guía de Instalación 📝

Esta es una aplicación web ligera escrita en Python que proporciona un editor de Markdown visual (WYSIWYG), protegido por autenticación de usuario y contraseña.

***
## 📋 Prerrequisitos

* Un servidor **Linux** (se recomiendan distribuciones basadas en Debian/Ubuntu).
* **Python 3.8** o superior.
* **pip** (gestor de paquetes de Python).
* **venv** (módulo para crear entornos virtuales).

***
## ⚙️ Instalación

Sigue estos pasos para configurar la aplicación en tu servidor.

### a. Preparar el Directorio y el Código
Crea un directorio para la aplicación y navega dentro de él.
```bash
# Crear el directorio principal para el editor
mkdir ~/markdown-editor

# Entrar en el nuevo directorio
cd ~/markdown-editor
````

Ahora, crea los archivos `app.py`, `hash_generator.py` y la estructura de carpetas necesaria.

### b. Crear y Activar el Entorno Virtual

Es una buena práctica aislar las dependencias del proyecto en un entorno virtual.

```bash
# Crear el entorno virtual llamado 'venv'
python3 -m venv venv

# Activar el entorno virtual
source venv/bin/activate
```

Verás **`(venv)`** al principio de tu línea de comandos, lo que indica que el entorno está activo.

### c. Instalar Dependencias

Instala las librerías de Python necesarias.

```bash
# Instalar Flask, Waitress y Werkzeug desde pip
pip install Flask waitress Werkzeug
```

-----

## 🔒 Configuración de Seguridad (Método Recomendado)

Gestionaremos las credenciales de forma segura y limpia, separando las contraseñas del archivo de servicio.

### a. Generar Hashes de Contraseña

Usa el script `hash_generator.py` para convertir las contraseñas deseadas en hashes seguros.

```bash
# Asegúrate de que tu entorno virtual esté activado
# Uso: python hash_generator.py 'tu_contraseña'
python hash_generator.py 'mySecretKey123'
```

Copia el hash completo que se genera en la terminal (ej: `scrypt:32768:8:1$...`). **No necesitas modificarlo.**

### b. Crear Archivo de Configuración de Entorno

Crearemos un archivo dedicado para almacenar los hashes de los usuarios.

```bash
# Crear un directorio para la configuración
sudo mkdir -p /etc/markdown

# Crear y editar el archivo de configuración
sudo nano /etc/markdown/markdown.conf
```

Dentro de este archivo, pega los hashes con el formato `CLAVE=VALOR`. No uses comillas ni `export`.

```ini
# /etc/markdown/markdown.conf
# Variables de entorno para el editor de Markdown.
# Pega aquí el hash directamente desde la salida del script.

AUTH_USER_admin=scrypt:32768:8:1$LBUyfkd9sC2KI837$65d189...
AUTH_USER_editor1=scrypt:32768:8:1$anotherHashValue...
```

-----

## 🚀 Ejecución de la Aplicación

### a. Ejecución Manual (para pruebas)

Para probar manualmente, exporta las variables y ejecuta la aplicación.

```bash
# Exportar las variables para la sesión actual
export AUTH_USER_admin='scrypt:32768:8:1$LBUyfkd9sC2KI837$...'

# Iniciar el servidor
python app.py
```

La aplicación estará disponible en `http://<IP_de_tu_servidor>:3555`.

### b. Ejecución como Servicio (`systemd`)

Esta es la forma correcta de ejecutar la aplicación en producción.

1.  **Crear el archivo del servicio:**
    ```bash
    sudo nano /etc/systemd/system/markdown-editor.service
    ```
2.  **Pegar el siguiente contenido:**
    Este contenido ya está actualizado para usar el archivo de configuración externo, lo que lo hace mucho más limpio.
    ```ini
    [Unit]
    Description=Visual Markdown Editor Server
    After=network.target

    [Service]
    # Cambia 'your_user' por tu nombre de usuario real
    User=your_user
    Group=www-data

    # Asegúrate de que esta ruta es correcta
    WorkingDirectory=/home/your_user/markdown-editor
    ExecStart=/home/your_user/markdown-editor/venv/bin/python app.py

    # Carga las variables de usuario desde el archivo de configuración externo
    EnvironmentFile=/etc/markdown/markdown.conf

    [Install]
    WantedBy=multi-user.target
    ```
3.  **Habilitar e Iniciar el Servicio:**
    ```bash
    # Recargar la configuración de systemd
    sudo systemctl daemon-reload

    # Habilitar el servicio para que inicie en el arranque
    sudo systemctl enable markdown-editor.service

    # Iniciar el servicio ahora
    sudo systemctl start markdown-editor.service
    ```

-----

## 🛠️ Gestión del Servicio

  * **Verificar estado:** `sudo systemctl status markdown-editor.service`
  * **Ver logs en tiempo real:** `sudo journalctl -u markdown-editor.service -f`
  * **Reiniciar el servicio:** `sudo systemctl restart markdown-editor.service`
  * **Detener el servicio:** `sudo systemctl stop markdown-editor.service`

-----

## 🛡️ Seguridad Avanzada: Integración con Fail2Ban

Para protegerte contra ataques de fuerza bruta, puedes integrar `fail2ban` para banear automáticamente las IPs después de múltiples intentos de inicio de sesión fallidos.

### a. Instalar Fail2Ban

Si no lo tienes instalado, añádelo a tu servidor:

```bash
sudo apt update
sudo apt install fail2ban
```

### b. Crear el Archivo de Log

La aplicación necesita un lugar donde escribir sus logs.

```bash
# Crear el archivo de log vacío
sudo touch /var/log/markdown-editor.log

# Asignar propietario (tu usuario) y grupo (www-data)
sudo chown your_user:www-data /var/log/markdown-editor.log

# Establecer permisos de lectura/escritura
sudo chmod 664 /var/log/markdown-editor.log
```

### c. Crear el Filtro de Fail2Ban

```bash
# Crear un nuevo archivo de filtro
sudo nano /etc/fail2ban/filter.d/markdown-editor.conf
```

Pega el siguiente contenido:

```ini
[Definition]
failregex = ^.* Failed login attempt for user '.*' from IP '<HOST>'$
ignoreregex =
```

### d. Crear la Jaula (Jail) de Fail2Ban

```bash
# Crear un nuevo archivo de configuración de jaula
sudo nano /etc/fail2ban/jail.d/markdown-editor.local
```

Pega lo siguiente. Esto baneará una IP por **10 minutos** después de **3 intentos fallidos**.

```ini
[markdown-editor]
enabled  = true
port     = 3555
filter   = markdown-editor
logpath  = /var/log/markdown-editor.log
maxretry = 3
findtime = 600
bantime  = 600
```

### e. Reiniciar y Verificar

```bash
# Reinicia tu app y fail2ban
sudo systemctl restart markdown-editor.service
sudo systemctl restart fail2ban

# Comprueba el estado de la jaula
sudo fail2ban-client status markdown-editor
```

````

***
### `README.md`

```markdown
# Visual Markdown Editor - Installation Guide 📝

This is a lightweight web application written in Python that provides a visual (WYSIWYG) Markdown editor, protected by user and password authentication.

***
## 📋 Prerequisites

* A **Linux** server (Debian/Ubuntu-based distributions are recommended).
* **Python 3.8** or higher.
* **pip** (Python package manager).
* **venv** (module for creating virtual environments).

***
## ⚙️ Installation

Follow these steps to set up the application on your server.

### a. Prepare the Directory and Code
Create a directory for the application and navigate into it.
```bash
# Create the main directory for the editor
mkdir ~/markdown-editor

# Move into the new directory
cd ~/markdown-editor
````

Now, create the `app.py`, `hash_generator.py` files, and the necessary folder structure.

### b. Create and Activate the Virtual Environment

It's a best practice to isolate project dependencies in a virtual environment.

```bash
# Create a virtual environment named 'venv'
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate
```

You will see **`(venv)`** at the beginning of your command prompt, indicating the environment is active.

### c. Install Dependencies

Install the required Python libraries.

```bash
# Install Flask, Waitress, and Werkzeug using pip
pip install Flask waitress Werkzeug
```

-----

## 🔒 Security Configuration (Recommended Method)

We will manage user credentials securely and cleanly by separating the passwords from the service file.

### a. Generate Password Hashes

Use the `hash_generator.py` script to convert your desired passwords into secure hashes.

```bash
# Make sure your virtual environment is activated
# Usage: python hash_generator.py 'your_password'
python hash_generator.py 'mySecretKey123'
```

Copy the full hash generated by the terminal (e.g., `scrypt:32768:8:1$...`). **You do not need to modify it.**

### b. Create an Environment Configuration File

We will create a dedicated file to store the user hashes.

```bash
# Create a directory for the configuration
sudo mkdir -p /etc/markdown

# Create and edit the configuration file
sudo nano /etc/markdown/markdown.conf
```

Inside this file, paste the hashes using the `KEY=VALUE` format. Do not use quotes or the `export` command.

```ini
# /etc/markdown/markdown.conf
# Environment variables for the Markdown editor.
# Paste the hash directly from the script's output here.

AUTH_USER_admin=scrypt:32768:8:1$LBUyfkd9sC2KI837$65d189...
AUTH_USER_editor1=scrypt:32768:8:1$anotherHashValue...
```

-----

## 🚀 Running the Application

### a. Manual Execution (for testing)

To test manually, export the variables and run the application.

```bash
# Export variables for the current session
export AUTH_USER_admin='scrypt:32768:8:1$LBUyfkd9sC2KI837$...'

# Start the server
python app.py
```

The application will be available at `http://<your_server_IP>:3555`.

### b. Running as a Service (`systemd`)

This is the proper way to run the application in production.

1.  **Create the service file:**
    ```bash
    sudo nano /etc/systemd/system/markdown-editor.service
    ```
2.  **Paste the following content:**
    This template is already updated to use the external configuration file, which makes it much cleaner.
    ```ini
    [Unit]
    Description=Visual Markdown Editor Server
    After=network.target

    [Service]
    # Change 'your_user' to your actual username
    User=your_user
    Group=www-data

    # Make sure this path is correct
    WorkingDirectory=/home/your_user/markdown-editor
    ExecStart=/home/your_user/markdown-editor/venv/bin/python app.py

    # Load user variables from the external configuration file
    EnvironmentFile=/etc/markdown/markdown.conf

    [Install]
    WantedBy=multi-user.target
    ```
3.  **Enable and Start the Service:**
    ```bash
    # Reload the systemd configuration
    sudo systemctl daemon-reload

    # Enable the service to start on boot
    sudo systemctl enable markdown-editor.service

    # Start the service now
    sudo systemctl start markdown-editor.service
    ```

-----

## 🛠️ Managing the Service

  * **Check status:** `sudo systemctl status markdown-editor.service`
  * **View real-time logs:** `sudo journalctl -u markdown-editor.service -f`
  * **Restart the service:** `sudo systemctl restart markdown-editor.service`
  * **Stop the service:** `sudo systemctl stop markdown-editor.service`

-----

## 🛡️ Advanced Security: Fail2Ban Integration

To protect against brute-force attacks, you can integrate `fail2ban` to automatically ban IPs after multiple failed login attempts.

### a. Install Fail2Ban

If you don't have it installed, add it to your server:

```bash
sudo apt update
sudo apt install fail2ban
```

### b. Create the Log File

The application needs a place to write its logs.

```bash
# Create an empty log file
sudo touch /var/log/markdown-editor.log

# Assign ownership to your user and the www-data group
sudo chown your_user:www-data /var/log/markdown-editor.log

# Set read/write permissions
sudo chmod 664 /var/log/markdown-editor.log
```

### c. Create the Fail2Ban Filter

```bash
# Create a new filter configuration file
sudo nano /etc/fail2ban/filter.d/markdown-editor.conf
```

Paste the following content:

```ini
[Definition]
failregex = ^.* Failed login attempt for user '.*' from IP '<HOST>'$
ignoreregex =
```

### d. Create the Fail2Ban Jail

```bash
# Create a new local jail configuration file
sudo nano /etc/fail2ban/jail.d/markdown-editor.local
```

Paste the following. This will ban an IP for **10 minutes** after **3 failed attempts**.

```ini
[markdown-editor]
enabled  = true
port     = 3555
filter   = markdown-editor
logpath  = /var/log/markdown-editor.log
maxretry = 3
findtime = 600
bantime  = 600
```

### e. Restart and Verify

```bash
# Restart your app and fail2ban
sudo systemctl restart markdown-editor.service
sudo systemctl restart fail2ban

# Check the jail status
sudo fail2ban-client status markdown-editor
```

```
```
