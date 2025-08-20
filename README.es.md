Editor Markdown Visual - Guía de Instalación
Esta es una aplicación web ligera escrita en Python que proporciona un editor de Markdown visual (WYSIWYG), protegido por autenticación de usuario y contraseña.

Requisitos
Un servidor con Linux (se recomiendan distribuciones basadas en Debian/Ubuntu).

Python 3.8 o superior.

pip (gestor de paquetes de Python).

venv (módulo para crear entornos virtuales).

1. Instalación
Sigue estos pasos para configurar la aplicación en tu servidor.

a. Prepara el Directorio y el Código
Primero, crea un directorio para la aplicación y navega hacia él.

mkdir ~/markdown-editor
cd ~/markdown-editor

Ahora, crea los archivos app.py, hash_generator.py y la estructura de carpetas necesaria.

b. Crea y Activa el Entorno Virtual
Es una buena práctica aislar las dependencias del proyecto en un entorno virtual.

python3 -m venv venv
source venv/bin/activate

Verás (venv) al principio de la línea de comandos, indicando que el entorno está activo.

c. Instala las Dependencias
Instala las librerías de Python necesarias.

pip install Flask waitress Werkzeug

2. Configuración de Seguridad
Las credenciales de usuario se gestionan de forma segura mediante hashes y variables de entorno.

a. Genera los Hashes de Contraseña
Usa el script hash_generator.py para convertir las contraseñas que desees en hashes seguros. Ejecuta el siguiente comando por cada usuario que quieras crear.

# Ejemplo para crear un hash para la contraseña 'miClaveSecreta123'
python hash_generator.py 'miClaveSecreta123'

Copia el hash completo que se genera en la terminal (ej. scrypt:32768:8:1$...).

b. Configura las Variables de Entorno
Para una prueba manual, puedes exportar las variables directamente en tu terminal. Recuerda que estas variables se perderán si cierras la sesión. Más adelante, las configuraremos de forma permanente en el servicio systemd.

# Sintaxis: export AUTH_USER_<nombre_de_usuario>='<hash_generado>'
export AUTH_USER_admin='el_hash_que_generaste_para_admin'
export AUTH_USER_editor1='el_hash_que_generaste_para_otro_usuario'

3. Ejecución
a. Ejecución Manual (para pruebas)
Con el entorno venv activado y las variables exportadas, puedes iniciar el servidor:

python app.py

La aplicación estará disponible en http://<IP_de_tu_servidor>:3555.

b. Ejecución como Servicio (systemd) - Recomendado
Para que la aplicación se ejecute de forma continua en segundo plano y se reinicie automáticamente, crearemos un servicio systemd.

1. Crea el archivo de servicio:

Usa un editor de texto como nano para crear el archivo de configuración del servicio.

sudo nano /etc/systemd/system/markdown-editor.service

2. Pega el siguiente contenido:

¡Importante! Modifica las siguientes líneas:

User: Cambia tu_usuario por tu nombre de usuario en el servidor.

WorkingDirectory: Asegúrate de que la ruta /home/tu_usuario/markdown-editor sea correcta.

Environment: Pega aquí las variables de entorno con los hashes que generaste.

[Unit]
Description=Servidor del Editor Markdown Visual
After=network.target

[Service]
# Cambia 'tu_usuario' por tu nombre de usuario real
User=tu_usuario
Group=www-data

# Cambia la ruta si has instalado la aplicación en otro lugar
WorkingDirectory=/home/tu_usuario/markdown-editor
ExecStart=/home/tu_usuario/markdown-editor/venv/bin/python app.py

# --- Variables de Entorno para los usuarios ---
# Aquí se definen los usuarios y sus hashes de forma permanente.
# Reemplaza los valores de ejemplo con los tuyos.
Environment="AUTH_USER_admin=scrypt:32768:8:1$..."
Environment="AUTH_USER_editor1=scrypt:32768:8:1$..."

[Install]
WantedBy=multi-user.target

3. Habilita e Inicia el Servicio:

Una vez guardado el archivo, ejecuta los siguientes comandos para que systemd reconozca y ponga en marcha tu servicio.

# Recarga la configuración de systemd
sudo systemctl daemon-reload

# Habilita el servicio para que se inicie automáticamente con el sistema
sudo systemctl enable markdown-editor.service

# Inicia el servicio ahora mismo
sudo systemctl start markdown-editor.service

4. Gestión del Servicio
Puedes gestionar el servicio con los siguientes comandos:

Verificar el estado: sudo systemctl status markdown-editor.service

Ver los logs en tiempo real: sudo journalctl -u markdown-editor.service -f

Reiniciar el servicio: sudo systemctl restart markdown-editor.service

Detener el servicio: sudo systemctl stop markdown-editor.service

5. Seguridad Avanzada: Integración con Fail2Ban
Para protegerte contra ataques de fuerza bruta, puedes integrar fail2ban para que bloquee automáticamente las IPs después de múltiples intentos de inicio de sesión fallidos.

a. Instala Fail2Ban
Si no lo tienes instalado, añádelo a tu servidor:

sudo apt update
sudo apt install fail2ban

b. Crea el Archivo de Log
La aplicación necesita un lugar donde escribir sus logs. Crea el archivo de log y dale al usuario de la aplicación permiso para escribir en él.

sudo touch /var/log/markdown-editor.log
sudo chown tu_usuario:www-data /var/log/markdown-editor.log
sudo chmod 664 /var/log/markdown-editor.log

Recuerda reemplazar tu_usuario por tu nombre de usuario real (el mismo que usaste en el archivo de servicio de systemd).

c. Crea el Filtro de Fail2Ban
Este filtro le dice a fail2ban cómo reconocer un intento de inicio de sesión fallido en nuestro archivo de log.

Crea un nuevo archivo de filtro:

sudo nano /etc/fail2ban/filter.d/markdown-editor.conf

Pega el siguiente contenido:

[Definition]
failregex = ^.* Failed login attempt for user '.*' from IP '<HOST>'$
ignoreregex =

d. Crea la "Jaula" (Jail) de Fail2Ban
Esta configuración de "jaula" vincula nuestro filtro a una acción (bloquear la IP).

Crea un nuevo archivo de jaula:

sudo nano /etc/fail2ban/jail.d/markdown-editor.local

Pega el siguiente contenido. Esta configuración bloqueará una IP durante 10 minutos después de 3 intentos fallidos en una ventana de 10 minutos.

[markdown-editor]
enabled = true
port = 3555
filter = markdown-editor
logpath = /var/log/markdown-editor.log
maxretry = 3
findtime = 600
bantime = 600

e. Reinicia y Verifica
Aplica la nueva configuración reiniciando tanto tu aplicación como el servicio de fail2ban.

# Reinicia tu app para aplicar los cambios de logging
sudo systemctl restart markdown-editor.service

# Reinicia fail2ban para cargar la nueva jaula
sudo systemctl restart fail2ban

Puedes comprobar el estado de tu nueva jaula con:

sudo fail2ban-client status markdown-editor

Ahora, cualquier IP que falle al iniciar sesión 3 veces será bloqueada automáticamente por el firewall de tu servidor.
