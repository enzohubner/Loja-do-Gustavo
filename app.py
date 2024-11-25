from flask import Flask, request, render_template, redirect, jsonify
import psycopg2
from psycopg2 import sql
from db import cursor, conn
app = Flask(__name__)

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
        return render_template('index.html')
    
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

@app.route('/altera_usuario', methods=['GET', 'POST'])
def altera_usuario():
    if request.method == 'POST':
        email_antigo = request.form['email_antigo']
        nome = request.form['nome']
        email_novo = request.form['email']
        senha = request.form['senha']

        if nome and email_antigo and email_novo and senha:
            cursor.execute("UPDATE usuarios SET nome = %s, email = %s, senha = %s WHERE email = %s",(nome, email_novo, senha, email_antigo))
            conn.commit()
            return redirect('/lista_usuario')
        else:
            return jsonify({"message": "Campos incompletos"}), 400
    else:
        email = request.args.get('email') 
        if not email:
            return jsonify({"message": "Email não fornecido"}), 400

        cursor.execute("SELECT nome, email FROM usuarios WHERE email = %s", (email,))
        usuario = cursor.fetchone()

        if not usuario:
            return jsonify({"message": "Usuário não encontrado"}), 404

        return render_template('altera_usuario.html', usuario=usuario)


@app.route('/deleta_usuario', methods=['POST'])
def deleta_usuario():
    if request.method == 'POST':
        email = request.form['email']

        if email:
            cursor.execute("DELETE FROM usuarios WHERE email = %s", (email,))
            conn.commit()

            return redirect('/lista_usuario')  
        else:
            return jsonify({"message": "Campos incompletos"}), 400
    else:
        return redirect('/deleta_usuario') 


@app.route('/cadastra_produto', methods=['GET', 'POST'])
def cadastra_produto():
    if request.method == 'POST':
        nome = request.form['nome']
        descricao = request.form['descricao']
        preco = request.form['preco']
        quantidade = request.form['quantidade']

        if nome and descricao and preco and quantidade: 
            cursor.execute("INSERT INTO produtos (nome, descricao, preco, quantidade) VALUES (%s, %s, %s, %s)",(nome, descricao, preco, quantidade))
            conn.commit()

            return redirect('/menu')
        else:
            return jsonify({"message": "Campos incompletos"}), 400

    return render_template('cadastra_produto.html')


@app.route('/produtos', methods=['GET'])
def lista_produtos():
    cursor.execute("SELECT id, nome, descricao, preco, quantidade FROM produtos")
    produtos = cursor.fetchall()

    return render_template('produtos.html', produtos=produtos)

@app.route('/edita_produto', methods=['GET', 'POST'])
def edita_produto():
    if request.method == 'POST':
        nome = request.form['nome']  
        novo_nome = request.form['novo_nome'] 
        descricao = request.form['descricao']
        preco = request.form['preco']
        quantidade = request.form['quantidade']

        if nome and novo_nome and descricao and preco and quantidade: 
            cursor.execute("UPDATE produtos SET nome=%s, descricao=%s, preco=%s, quantidade=%s WHERE nome=%s", (novo_nome, descricao, preco, quantidade, nome))
            conn.commit()
            return redirect('/produtos')
        else:
            return jsonify({"message": "Campos incompletos"}), 400 

    else:
        nome = request.args.get('nome')  
        if not nome:
            return jsonify({"message": "Nome não fornecido"}), 400

        cursor.execute("SELECT nome, descricao, preco, quantidade FROM produtos WHERE nome=%s", (nome,))
        produto = cursor.fetchone()

        if not produto:  
            return jsonify({"message": "Produto não encontrado"}), 404

        return render_template('editar_produto.html', produto=produto)

@app.route('/deleta_produto', methods=['POST'])
def deleta_produto():
    nome = request.form['nome']  

    if nome:
        cursor.execute("DELETE FROM produtos WHERE nome = %s", (nome,))
        conn.commit()
        return redirect('/produtos')
    else:
        return jsonify({"message": "Nome do produto não fornecido"}), 400  


@app.route('/navbar', methods=['GET'])
def altera():
    email = request.args.get('email')
    senha = request.args.get('senha')
    return render_template('navbar.html', email=email, senha=senha)

@app.route('/cadastra_produto', methods=['GET', 'POST'])
def teste():
    return render_template('cadastra_produto.html')

@app.route('/notificacoes', methods=['GET', 'POST'])
def notificacoes():
    return render_template('notificacoes.html')

@app.route('/editar_produto', methods=['GET', 'POST'])
def editar_produtos():
    return render_template('editar_produto.html')

@app.route('/menu', methods=['GET', 'POST'])
def menu():
    produtos = [
        {"id": 1, "nome": "Produto A", "descricao": "Descrição do Produto A", "preco": 10.99, "quantidade": 100},
        {"id": 2, "nome": "Produto B", "descricao": "Descrição do Produto B", "preco": 20.99, "quantidade": 200},
        {"id": 3, "nome": "Produto C", "descricao": "Descrição do Produto C", "preco": 30.99, "quantidade": 300},
        {"id": 4, "nome": "Produto D", "descricao": "Descrição do Produto D", "preco": 40.99, "quantidade": 400},
        {"id": 5, "nome": "Produto E", "descricao": "Descrição do Produto E", "preco": 50.99, "quantidade": 500}
    ]
    return render_template('menu.html', produtos=produtos)

@app.route('/alt_usuario', methods=['GET', 'POST'])
def alt_usuario():
    return render_template('altera_usuario.html')

@app.route('/contato', methods=['GET', 'POST'])
def contato():
    return render_template('contato.html')

if __name__ == '__main__':
    app.run(debug=True)
