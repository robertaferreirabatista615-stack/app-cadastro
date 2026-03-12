from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
import bcrypt
import re

app = Flask(__name__)

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "12345",
    "database": "teste"
}

# Improved Email Regex
EMAIL_RE = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")

def senha_forte(s: str) -> bool:
    if len(s) < 8:
        return False
    if not re.search(r"[A-Za-z]", s):
        return False
    if not re.search(r"\d", s):
        return False  
    return True

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/register", methods=["POST"])
def register():
    # Receive data from Form
    # The "or ''" ensures that if .get() returns None, it uses an empty string instead.
    nome = (request.form.get("nome") or "").strip()
    email = (request.form.get("email") or "").strip()
    senha = (request.form.get("senha") or "").strip()
    
    # Validations
    if len(nome) < 3:
        return "Nome deve ter pelo menos 3 caracteres.", 400
    if not EMAIL_RE.match(email):
        return "Email inválido.", 400
    if not senha_forte(senha):
        return "Senha fraca. Use 8+ caracteres, com letras e números.", 400
        
    # Hashing the password correctly
    hashed_senha = bcrypt.hashpw(senha.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    conn = None
    cur = None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor()

        # Check if user exists
        cur.execute("SELECT id FROM usuarios WHERE email=%s", (email,))
        if cur.fetchone():
            return "Esse email já está cadastrado.", 400

        # Insert new user
        cur.execute(
            "INSERT INTO usuarios (nome, email, senha) VALUES (%s, %s, %s)",
            (nome, email, hashed_senha)
        )
        conn.commit() # Fixed typo here

        return redirect(url_for("home"))
    
    except mysql.connector.Error as e:
        return f"Erro no banco de dados: {e}", 500
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    app.run(debug=True)