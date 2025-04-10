from cryptography.fernet import Fernet
from flask import Flask, render_template
import os

app = Flask(__name__)

# 🔐 Génère ou récupère une clé persistante (au lieu de générer à chaque lancement)
key_path = "secret.key"

if os.path.exists(key_path):
    with open(key_path, "rb") as f_key:
        key = f_key.read()
else:
    key = Fernet.generate_key()
    with open(key_path, "wb") as f_key:
        f_key.write(key)

f = Fernet(key)

# 🏠 Route d'accueil
@app.route('/')
def hello_world():
    return render_template('hello.html')

# 🔒 Route de chiffrement
@app.route('/encrypt/<string:valeur>')
def encryptage(valeur):
    valeur_bytes = valeur.encode()  # Conversion str -> bytes
    token = f.encrypt(valeur_bytes)  # Encrypt la valeur
    return f"Valeur encryptée : {token.decode()}"  # Retourne le token en str

# 🔓 Route de déchiffrement
@app.route('/decrypt/<string:valeur>')
def decryptage(valeur):
    try:
        valeur_bytes = valeur.encode()
        decrypted = f.decrypt(valeur_bytes)
        return f"Valeur décryptée : {decrypted.decode()}"
    except Exception as e:
        return f"Erreur de déchiffrement : {str(e)}"

# 🚀 Lancement local (inutile sur AlwaysData mais pratique en dev)
if __name__ == "__main__":
    app.run(debug=True)
