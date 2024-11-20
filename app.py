from flask import Flask, request, render_template, redirect, jsonify
import psycopg2
from psycopg2 import sql
from db import cursor, conn
app = Flask(__name__)

def bd():
    return 'CREATE TABLE usuarios (id SERIAL PRIMARY KEY,nome VARCHAR(100),email VARCHAR(100) UNIQUE,senha VARCHAR(100))'

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']
        
        inserir_query = "INSERT INTO usuarios (nome, email, senha) VALUES (%s, %s, %s)"
        cursor.execute(inserir_query, (nome, email, senha))
        cursor.close()
        conn.close()

        return redirect('/login')
    else:
        return render_template('home.html')
    
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']

        if email and senha:

            cursor.execute(f"SELECT * FROM usuarios WHERE email = '{email}'")

            rows = cursor.fetchall()
            print(rows)
            
            if rows and rows[0][3] == senha:
                return jsonify({"message":"Login efetuado com sucesso"}), 200     
                   
            return jsonify({"message":"Credenciais invalidas"}), 400
        
        cursor.close()
        conn.close()

        return jsonify({"message":"Campos incompletos"}), 400
    else:
        return render_template('login.html')

@app.route('/navbar', methods=['GET'])
def altera():
    email = request.args.get('email')
    senha = request.args.get('senha')
    return render_template('navbar.html', email=email, senha=senha)

@app.route('/cadastra_produto', methods=['GET', 'POST'])
def teste():
    return render_template('cadastra_produto.html')

@app.route('/altera_usuario', methods=['GET', 'POST'])
def altera_usuario():
    return render_template('altera_usuario.html')

if __name__ == '__main__':
    app.run(debug=True)
