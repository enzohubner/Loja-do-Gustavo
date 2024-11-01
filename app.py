from flask import Flask, request, render_template, redirect
import psycopg2
from psycopg2 import sql

app = Flask(__name__)

def bd():
    return 'CREATE TABLE usuarios (id SERIAL PRIMARY KEY,nome VARCHAR(100),email VARCHAR(100) UNIQUE,senha VARCHAR(100))'


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']
        
        conn = psycopg2.connect('')
        cursor = conn.cursor()
        
        inserir_query = "INSERT INTO usuarios (nome, email, senha) VALUES (%s, %s, %s)"
        cursor.execute(inserir_query, (nome, email, senha))

        conn.commit()  
        cursor.close()
        conn.close()

        return render_template('resposta.html', nome=nome, email=email, senha=senha)
    else:
        return render_template('index.html')

@app.route('/resposta', methods=['GET'])
def resposta():
    nome = request.args.get('nome')
    email = request.args.get('email')
    senha = request.args.get('senha')
    return render_template('resposta.html', nome=nome, email=email, senha=senha)

if __name__ == '__main__':
    app.run(debug=True)
