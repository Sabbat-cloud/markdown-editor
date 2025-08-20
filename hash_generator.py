# hash_generator.py
# Este script te ayuda a crear hashes seguros para tus contraseñas.
# Necesitarás instalar la librería werkzeug, que ya viene con Flask.
# Si no la tuvieras, ejecuta: pip install Werkzeug

from werkzeug.security import generate_password_hash
import sys

if len(sys.argv) != 2:
    print("Uso: python hash_generator.py 'tu_contraseña_aqui'")
    sys.exit(1)

password = sys.argv[1]
hashed_password = generate_password_hash(password)

print("\nContraseña original:", password)
print("Hash generado (cópialo):", hashed_password)
print("\nRecuerda usar este hash en tus variables de entorno.\n")
