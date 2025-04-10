from cryptography.fernet import Fernet, InvalidToken
from flask import Flask
import sqlite3
import os

app = Flask(__name__)
DB_PATH = "cles_users.db"

# 📌 Initialisation BDD si elle n'existe pas
def init_db():
    if not os.path.exists(DB_PATH):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE users (
                username TEXT PRIMARY KEY,
                key TEXT NOT NULL
            )
        ''')
        conn.commit()
        conn.close()

init_db()

# 📥 Génère une clé pour un utilisateur et la sauvegarde
@app.route('/generate_key/<username>')
def generate_key(username):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Vérifie si le user a déjà une clé
    c.execute("SELECT key FROM users WHERE username = ?", (username,))
    result = c.fetchone()

    if result:
        # Ne regénère pas la clé, renvoie l'existante
        key = result[0]
        message = f"Clé déjà existante pour {username} : {key}"
    else:
        # Crée une nouvelle clé uniquement si l'user est nouveau
        key = Fernet.generate_key().decode()
        c.execute("INSERT INTO users (username, key) VALUES (?, ?)", (username, key))
        conn.commit()
        message = f"Nouvelle clé générée pour {username} : {key}"

    conn.close()
    return message


# 🔒 Chiffre une valeur avec la clé du user
@app.route('/encrypt/<username>/<valeur>')
def encrypt(username, valeur):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT key FROM users WHERE username = ?", (username,))
    result = c.fetchone()
    conn.close()

    if result:
        key = result[0]
        f = Fernet(key.encode())
        token = f.encrypt(valeur.encode())
        return f"Valeur encryptée : {token.decode()}"
    else:
        return f"Aucune clé trouvée pour l'utilisateur {username}"

# 🔓 Déchiffre une valeur avec la clé du user
@app.route('/decrypt/<username>/<valeur>')
def decrypt(username, valeur):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT key FROM users WHERE username = ?", (username,))
    result = c.fetchone()
    conn.close()

    if result:
        key = result[0]
        f = Fernet(key.encode())
        try:
            decrypted = f.decrypt(valeur.encode())
            return f"Valeur décryptée : {decrypted.decode()}"
        except InvalidToken:
            return "Erreur : le token ne correspond pas à la clé."
    else:
        return f"Aucune clé trouvée pour l'utilisateur {username}"

# Page d'accueil
@app.route('/')
def home():
    return "Bienvenue sur l'API de chiffrement personnalisée 🔐"

if __name__ == "__main__":
    app.run(debug=True)
