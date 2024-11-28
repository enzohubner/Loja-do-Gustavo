from flask import Flask, request, render_template, redirect, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import psycopg2
from db import cursor, conn

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class Usuario(UserMixin):
    def __init__(self, id, email, nome):
        self.id = id
        self.email = email
        self.nome = nome

@login_manager.user_loader
def load_user(user_id):
    cursor.execute("SELECT id, nome, email FROM usuarios WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    if user:
        return Usuario(user[0], user[2], user[1])
    return None

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']
        
        cursor.execute("INSERT INTO usuarios (nome, email, senha) VALUES (%s, %s, %s)", (nome, email, senha))
        conn.commit()
        return redirect('/login')
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']

        if email and senha:
            cursor.execute("SELECT id, email, senha, nome FROM usuarios WHERE email = %s", (email,))
            user = cursor.fetchone()
            if user and user[2] == senha:  
                usuario = Usuario(user[0], user[1], user[3])
                login_user(usuario) 
                return redirect('/menu')
            return jsonify({"message": "Credenciais inválidas"}), 400
    return render_template('login.html')

@app.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    return redirect('/login')

@app.route('/altera_usuario', methods=['GET', 'POST'])
@login_required
def altera_usuario():
    if request.method == 'POST':
        nome = request.form['nome']
        email_novo = request.form['email']
        senha = request.form['senha']

        if nome and email_novo and senha:
            cursor.execute("UPDATE usuarios SET nome = %s, email = %s, senha = %s WHERE email = %s",(nome, email_novo, senha, current_user.email))
            conn.commit()

            current_user.email = email_novo
            return redirect('/menu')
        return jsonify({"message": "Campos incompletos"}), 400
    else:
        return render_template('altera_usuario.html', usuario=current_user)


@app.route('/deleta_usuario', methods=['POST'])
@login_required
def deleta_usuario():
    cursor.execute("DELETE FROM usuarios WHERE email = %s", (current_user.email,))
    conn.commit()
    logout_user()
    return redirect('/login')

@app.route('/cadastra_produto', methods=['GET', 'POST'])
@login_required
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
        return jsonify({"message": "Campos incompletos"}), 400
    return render_template('cadastra_produto.html')

@app.route('/edita_produto', methods=['GET', 'POST'])
@login_required
def edita_produto():
    if request.method == 'POST':
        nome = request.form['nome']
        novo_nome = request.form['novo_nome']
        descricao = request.form['descricao']
        preco = request.form['preco']
        quantidade = request.form['quantidade']

        if nome and novo_nome and descricao and preco and quantidade:
            cursor.execute("UPDATE produtos SET nome = %s, descricao = %s, preco = %s, quantidade = %s WHERE nome = %s",(novo_nome, descricao, preco, quantidade, nome))
            conn.commit()
            return redirect('/menu')
        return jsonify({"message": "Campos incompletos"}), 400
    else:
        nome = request.args.get('nome')
        if not nome:
            return jsonify({"message": "Nome do produto não fornecido"}), 400

        cursor.execute("SELECT nome, descricao, preco, quantidade FROM produtos WHERE nome = %s", (nome,))
        produto = cursor.fetchone()

        if not produto:
            return jsonify({"message": "Produto não encontrado"}), 404
        return render_template('editar_produto.html', produto=produto)

@app.route('/deleta_produto', methods=['POST'])
@login_required
def deleta_produto():
    nome = request.form['nome']
    if nome:
        cursor.execute("DELETE FROM produtos WHERE nome = %s", (nome,))
        conn.commit()
        return redirect('/menu')
    return jsonify({"message": "Nome do produto não fornecido"}), 400

if __name__ == '__main__':
    app.run(debug=True)


@app.route('/navbar', methods=['GET'])
def altera():
    notificacoes_ativas = ["Notificação 1", "Notificação 2", "Notificação 3"]
    
    return render_template('navbar.html', notificacoes_ativas=notificacoes_ativas)

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
    return render_template('chat.html')

@app.route('/configuracao', methods=['GET', 'POST'])
def configuracao():
    return render_template('configuracoes.html')

@app.route('/relatorios', methods=['GET', 'POST'])
def relatorios():
    return render_template('relatorios.html')

if __name__ == '__main__':
    app.run(debug=True)
