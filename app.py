from flask import Flask, request, render_template, redirect, jsonify
import psycopg2
from psycopg2 import sql
from db import cursor, conn

app = Flask(__name__)

usuario = " "
psswd = " "
# equanto n implemento flask-login

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

        return redirect('/')
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
            
            global usuario 
            usuario = rows[0][2]

            if rows and rows[0][3] == senha:
                global psswd
                psswd = senha
                return render_template('menu.html')  
                   
            return jsonify({"message":"Credenciais invalidas"}), 400
        
        cursor.close()
        conn.close()

        return jsonify({"message":"Campos incompletos"}), 400
    else:
        return render_template('login.html')

@app.route('/altera_usuario', methods=['GET', 'POST'])
def altera_usuario():
    if request.method == 'POST':
        global usuario, psswd
        senhaAntiga = request.form['senhaAntiga']  
        email_antigo = usuario
        nome = request.form['nome']
        email_novo = request.form['email']
        novaSenha = request.form['novaSenha']

        if senhaAntiga == psswd:
            cursor.execute("UPDATE usuarios SET nome = %s, email = %s, senha = %s WHERE email = %s",(nome, email_novo, novaSenha, email_antigo))
            conn.commit()
            return jsonify({"message": "Alterações salvas com sucesso!"}), 200
        else:
            return jsonify({"message": "Senha antiga incorreta"}), 400
    else:
        return render_template('altera_usuario.html')#, usuario=usuario)


@app.route('/deleta_usuario', methods=['POST'])
def deleta_usuario():
    if request.method == 'POST':
        email = request.form['email']

        if email:
            cursor.execute("DELETE FROM usuarios WHERE email = %s", (email,))
            conn.commit()

            return render_template('deleta_usuario.html')    
        else:
            return jsonify({"message": "Campos incompletos"}), 400
    else:
        return render_template('deleta_usuario.html') 


@app.route('/cadastra_produto', methods=['GET', 'POST'])
def cadastra_produto():
    if request.method == 'POST':
        nome = request.form['nome']
        descricao = request.form['descricao']
        preco = request.form['preco']

        if nome and descricao and preco: 
            cursor.execute("INSERT INTO produtos (nome, valor, descricao) VALUES (%s, %s, %s)",(nome, preco, descricao))
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

@app.route('/editar_produto', methods=['GET', 'POST'])
def editar_produto():
    if request.method == 'POST':
        print("Foi post")
        id = request.form['codigo']  
        nome = request.form['nome'] 
        valor = request.form['valor']
        descricao = request.form['descricao']

        if id and nome and valor and descricao: 
            cursor.execute("UPDATE produtos SET nome=%s, valor=%s, descricao=%s WHERE id=%s", (nome, valor, descricao, id))
            conn.commit()
            return redirect('/menu')
        else:
            return jsonify({"message": "Campos incompletos"}), 400 
    else:
        return render_template('editar_produto.html')

@app.route('/excluir_produto', methods=['POST'])
def excluir_produto():
    if request.method == 'POST':
        id = request.form['codigo'] 
        if id:
            cursor.execute("DELETE * produtos WHERE id=%s", (id))
            conn.commit()
            return redirect('/menu')
        else:
            return jsonify({"message": "Campos incompletos"}), 400 
    else:
        return render_template('excluir_produto.html')


@app.route('/navbar', methods=['GET'])
def altera():
    notificacoes_ativas = ["Notificação 1", "Notificação 2", "Notificação 3"]
    
    return render_template('navbar.html', notificacoes_ativas=notificacoes_ativas)

@app.route('/notificacoes', methods=['GET', 'POST'])
def notificacoes():
    return render_template('notificacoes.html')

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

@app.route('/contato', methods=['GET', 'POST'])
def contato():
    return render_template('chat.html')

@app.route('/configuracao', methods=['GET', 'POST'])
def configuracao():
    return render_template('configuracoes.html')

@app.route('/relatorios', methods=['GET', 'POST'])
def relatorios():
    return render_template('relatorios.html')

if __name__ == '__main__':
    app.run(debug=True)
