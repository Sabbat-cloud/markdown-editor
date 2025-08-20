# app.py
import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, render_template, request, jsonify, Response, abort
from waitress import serve
from werkzeug.security import check_password_hash

# --- CONFIGURACIÓN ---
MARKDOWN_FOLDER = 'markdown_files' 
PORT = 3555
LOG_FILE = '/var/log/markdown-editor.log' # Ruta para el archivo de logs

# Inicializamos la aplicación Flask ANTES de configurar el logger
app = Flask(__name__)

# --- CONFIGURACIÓN DE LOGGING ---
# Configura el logger para escribir en un archivo con rotación.
# Esto registrará los intentos de inicio de sesión fallidos para que fail2ban los detecte.
try:
    handler = RotatingFileHandler(LOG_FILE, maxBytes=10000, backupCount=3)
    handler.setLevel(logging.WARNING) # Solo nos interesan los warnings o errores
    log_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(log_format)
    app.logger.addHandler(handler)
    app.logger.setLevel(logging.WARNING)
except PermissionError:
    print(f"ADVERTENCIA: No se pudo escribir en el archivo de log '{LOG_FILE}'.")
    print("Asegúrate de que el archivo exista y de que el usuario que ejecuta la app tenga permisos de escritura.")
# --- FIN DE CONFIGURACIÓN DE LOGGING ---


# --- CARGA SEGURA DE USUARIOS ---
AUTHORIZED_USERS = {}
for key, value in os.environ.items():
    if key.startswith('AUTH_USER_'):
        username = key.split('AUTH_USER_')[1]
        AUTHORIZED_USERS[username] = value

if not AUTHORIZED_USERS:
    app.logger.warning("No se han encontrado usuarios en las variables de entorno (ej. AUTH_USER_admin).")

AUTHORIZED_IPS = [] 
# --- FIN DE LA CONFIGURACIÓN ---

if not os.path.exists(MARKDOWN_FOLDER):
    os.makedirs(MARKDOWN_FOLDER)

# --- LÓGICA DE AUTENTICACIÓN Y AUTORIZACIÓN ---

def check_auth(username, password):
    if username not in AUTHORIZED_USERS:
        return False
    return check_password_hash(AUTHORIZED_USERS[username], password)

def check_ip():
    if not AUTHORIZED_IPS:
        return True
    return request.remote_addr in AUTHORIZED_IPS

def require_auth(f):
    def decorated(*args, **kwargs):
        if not check_ip():
            abort(403)

        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            # --- REGISTRO DE FALLO PARA FAIL2BAN ---
            user_info = f"'{auth.username}'" if auth else "'(no user provided)'"
            app.logger.warning(f"Failed login attempt for user {user_info} from IP '{request.remote_addr}'")
            
            return Response(
                'Acceso no autorizado.', 401,
                {'WWW-Authenticate': 'Basic realm="Login Required"'}
            )
        return f(*args, **kwargs)
    decorated.__name__ = f.__name__
    return decorated


# --- RUTAS DE LA APLICACIÓN (ENDPOINTS) ---

@app.route('/')
@require_auth
def index():
    return render_template('index.html')

@app.route('/api/files', methods=['GET'])
@require_auth
def list_files():
    try:
        files = [f for f in os.listdir(MARKDOWN_FOLDER) if f.endswith('.md')]
        return jsonify(files)
    except Exception as e:
        app.logger.error(f"Error al listar archivos: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/files/<string:filename>', methods=['GET'])
@require_auth
def get_file(filename):
    if '..' in filename or filename.startswith('/'):
        return jsonify({"error": "Nombre de archivo no válido"}), 400
    filepath = os.path.join(MARKDOWN_FOLDER, filename)
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        return jsonify({"filename": filename, "content": content})
    else:
        return jsonify({"error": "El archivo no existe"}), 404

@app.route('/api/files/<string:filename>', methods=['POST'])
@require_auth
def save_file(filename):
    if '..' in filename or filename.startswith('/'):
        return jsonify({"error": "Nombre de archivo no válido"}), 400
    if not filename.endswith('.md'):
        filename += '.md'
    filepath = os.path.join(MARKDOWN_FOLDER, filename)
    data = request.json
    if 'content' not in data:
        return jsonify({"error": "Falta el contenido"}), 400
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(data['content'])
        return jsonify({"success": True, "message": f"Archivo '{filename}' guardado correctamente."})
    except Exception as e:
        app.logger.error(f"Error al guardar el archivo '{filename}': {e}")
        return jsonify({"error": str(e)}), 500

# --- INICIO DE LA APLICACIÓN ---

if __name__ == '__main__':
    print(f"Servidor del editor Markdown iniciado en http://0.0.0.0:{PORT}")
    print("Usando el servidor de producción Waitress.")
    print(f"Usuarios cargados: {list(AUTHORIZED_USERS.keys())}")
    print("Para detener el servidor, presiona CTRL+C.")
    serve(app, host='0.0.0.0', port=PORT)

