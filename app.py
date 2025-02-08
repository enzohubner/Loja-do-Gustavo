import base64
from datetime import datetime, timedelta
import io
import os
from flask import Flask, abort, flash, g, request, render_template, redirect, jsonify, send_file, url_for
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from psycopg2 import sql
from flask_socketio import SocketIO, send, emit
from db import cursor, conn
from utils.bd_functions import get_emails, get_notificacoes, get_produtos, get_vendas
from utils.pdf_generator import create_sales_report_pdf
from components.database import DataBase
from components.utilities import *

from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

app = Flask(__name__)
app.config['SECRET_KEY'] = '@teste22@.22'
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'cakesbigusta@gmail.com'  # Seu email
app.config['MAIL_PASSWORD'] = 'nzep gpkv jgii wygq'

mail = Mail(app)
serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])

socketio = SocketIO(app)
db = DataBase()
rooms = {}

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class Usuario(UserMixin):
    def __init__(self, id, nome, email, senha, role, telefone, escola):
        self.id = id
        self.nome = nome
        self.email = email
        self.senha = senha
        self.role = role
        self.telefone = telefone
        self.escola = escola

@login_manager.user_loader
def load_user(id_usuario):
    cursor.execute("SELECT id, nome, email, senha, role, telefone, escola FROM usuarios WHERE id = %s", (id_usuario,))
    dados_usuario = cursor.fetchone()
    print(dados_usuario)
    if dados_usuario:
        return Usuario(id=dados_usuario[0], 
                      nome=dados_usuario[1], 
                      email=dados_usuario[2], 
                      senha=dados_usuario[3],
                      role=dados_usuario[4],
                      telefone=dados_usuario[5],
                      escola=dados_usuario[6])
    return None

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        telefone = request.form['telefone']
        escola = request.form['escola']
        senha = request.form['senha']
        senha2 = request.form['confirmeSenha']
        role = 'user'

        if senha == senha2:
            inserir_query = "INSERT INTO usuarios (nome, email, senha, telefone, escola,role) VALUES (%s, %s, %s, %s, %s,%s)"
            cursor.execute(inserir_query, (nome, email, senha, telefone, escola, role))
            conn.commit()
            return redirect('/login')
        else:
            return jsonify({"message":"Credenciais invalidas"}), 400
    else:
        return render_template('cadastro.html')

 
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        if email and senha:
            cursor.execute("SELECT id, nome, email, senha, role, telefone, escola FROM usuarios WHERE email = %s", (email,))
            dados_usuario = cursor.fetchone()
            print(dados_usuario, dados_usuario[3], senha)

            if dados_usuario and dados_usuario[3] == senha:  # Substituir por hashing seguro posteriormente
                print("passou")
                user =  Usuario(id=dados_usuario[0], 
                      nome=dados_usuario[1], 
                      email=dados_usuario[2],
                      senha=dados_usuario[3],
                      role=dados_usuario[4],
                      telefone=dados_usuario[5],
                      escola=dados_usuario[6])
                login_user(user)
                return redirect(url_for('menu'))
            else:
                print('Credenciais inválidas')
                return redirect(url_for('login'))
        print('Campos incompletos')
        return redirect(url_for('login'))
    else:
        return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/altera_usuario', methods=['GET', 'POST'])
@login_required
def altera_usuario():
    user = {"role": current_user.role}
    if request.method == 'POST':
        nome = request.form['nome']
        senha_antiga = request.form['senhaAntiga']  
        email_novo = request.form['email']
        senha_nova = request.form['novaSenha']

        email = current_user.email
        cursor.execute("SELECT senha FROM usuarios WHERE email = %s", (email,))
        senha = cursor.fetchone()

        if senha_antiga == senha[0]: 
            cursor.execute("UPDATE usuarios SET nome = %s, email = %s, senha = %s WHERE email = %s", (nome, email_novo, senha_nova, email))
            conn.commit()
            return jsonify({"message": "Alterações salvas com sucesso!"}), 200
        else:
            return jsonify({"message": "Senha antiga incorreta"}), 400
    else:
        usuario = {
            'id': current_user.id,
            'email': current_user.email,
            'nome': current_user.nome,
            'telefone': '99999-9999',
            'escola': 'Escola XYZ',
            'role': current_user.role
        }
        return render_template('altera_usuario.html', usuario=usuario, user=user)

@app.route('/deleta_usuario', methods=['POST'])
@login_required
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
@login_required
def cadastra_produto():
    user = {"role": current_user.role}
    if request.method == 'POST':
        nome = request.form['nome']
        descricao = request.form['descricao']
        preco = request.form['preco']
        quantidade = request.form['quantidade']
        imagem = request.files.get('imagem')
        if imagem:
            # Create directory if it doesn't exist
            import os
            upload_folder = os.path.join('static', 'imagens')
            os.makedirs(upload_folder, exist_ok=True)
            
            # Save file to the directory
            filename = os.path.join(upload_folder, imagem.filename)
            imagem.save(filename)
            imagem = f'static/imagens/{imagem.filename}'
        else:
            imagem = None

        if nome and descricao and preco: 
            cursor.execute("INSERT INTO produtos (nome, valor, descricao, quantidade, imagem) VALUES (%s, %s, %s, %s, %s)",(nome, preco, descricao, quantidade, imagem))
            conn.commit()

            return redirect('/menu')
        else:
            return jsonify({"message": "Campos incompletos"}), 400
    return render_template('cadastra_produto.html', user=user)


@app.route('/produtos', methods=['GET'])
@login_required
def lista_produtos():
    cursor.execute("SELECT id, nome, descricao, preco, quantidade FROM produtos")
    produtos = cursor.fetchall()

    return render_template('produtos.html', produtos=produtos)

@app.route('/editar_produto/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_produto(id):
    user = {"role": current_user.role}
    if request.method == 'POST':
        id = request.form['codigo']  
        nome = request.form['nome'] 
        valor = request.form['valor']
        descricao = request.form['descricao']

        imagem = request.files.get('imagem')

        if imagem:
            imagem.save(f'imagens/{imagem.filename}')

        if id and nome and valor and descricao: 
            cursor.execute("UPDATE produtos SET nome=%s, valor=%s, descricao=%s WHERE id=%s", (nome, valor, descricao, id))
            conn.commit()
            return redirect('/menu')
        else:
            return jsonify({"message": "Campos incompletos"}), 400 
    else:
        cursor.execute("SELECT * FROM produtos WHERE id=%s", (id,))
        produto_db = cursor.fetchone()

        produto = {
            "id": produto_db[0],
            "nome": produto_db[1],
            "descricao": str(produto_db[3]),
            "preco": produto_db[2],
            "quantidade": int(produto_db[0]),
            "imagem": "/static/png-logo-black.png"
        }
        print(produto)
        return render_template('editar_produto.html', produto=produto, user=user)

@app.route('/excluir_produto/<int:id>', methods=['GET', 'POST'])
@login_required
def excluir_produto(id):
    if request.method == 'GET':
        if id:
            cursor.execute("DELETE FROM produtos WHERE id=%s", (id,))
            conn.commit()
            return redirect('/menu')
        else:
            return jsonify({"message": "Campos incompletos"}), 400 
    else:
        return render_template('excluir_produto.html')

@app.route('/navbar', methods=['GET'])
def altera():
    notificacoes_ativas = ["Notificação 1", "Notificação 2", "Notificação 3"]
    usuario = "admin"
    
    return render_template('navbar.html', notificacoes_ativas=notificacoes_ativas, usuario=usuario)

@app.route('/notificacoes', methods=['GET', 'POST'])
def notificacoes():
    user = {"role": current_user.role}

    if request.method == 'POST':
        mensagem = request.form['mensagem']
        tipo = request.form['tipo']
        print(mensagem, tipo)
        if mensagem:
            if tipo == "cliente":
                cursor.execute('INSERT INTO notificacoes (texto, usuario) VALUES (%s, %s)', (mensagem, current_user.id))
                conn.commit()
            if tipo == "funcionario":
                cursor.execute('INSERT INTO notificacoes (texto, usuario) VALUES (%s, %s)', (mensagem, current_user.id))
                conn.commit()

            return redirect('/menu')
        else:
            return jsonify({"message": "Campos incompletos"}), 400
    else:
        return render_template('notificacoes.html', user=user)

@app.route('/requisitar/<int:id_produto>/<int:quantidade>', methods=['GET', 'POST'])
@login_required
def requistar(id_produto, quantidade):
    id_usuario = current_user.id

    if request.method == 'GET':
        if id_produto and quantidade:
            cursor.execute("INSERT INTO requisicoes (id_usuario, id_produto, quantidade) VALUES (%s, %s, %s)", (id_usuario, id_produto, quantidade))
            conn.commit()
            return redirect('/menu')
        else:
            return jsonify({"message": "Campos incompletos"}), 400 
    else:
        return render_template('menu.html')

@app.route('/lista_requisicoes', methods=['GET', 'POST'])
@login_required
def lista_requisicoes():
    cursor.execute("SELECT * FROM requisicoes")
    requisicoes_db = cursor.fetchall()
    
    requisicoes = []

    user={"role":current_user.role}

    for i, item in enumerate(requisicoes_db, start=1):
        cursor.execute("SELECT nome, telefone FROM usuarios WHERE id=%s", (item[1],))
        dados_usuario = cursor.fetchone()

        nome_usuario = dados_usuario[0]
        telefone = dados_usuario[1]

        cursor.execute("SELECT nome FROM produtos WHERE id=%s", (item[2],))
        nome_produto = cursor.fetchone()

        requisicoes.append({
            "id": item[0],
            "nome_usuario": nome_usuario,
            "telefone": telefone,
            "nome_produto": nome_produto,
            "quantidade": item[3]
        })

    return render_template('lista_requisicoes.html', requisicoes=requisicoes, user=user)

@app.route('/menu', methods=['GET', 'POST'])
@login_required
def menu():
    cursor.execute("SELECT * FROM produtos")
    produtos_db = cursor.fetchall()
    
    produtos = []

    for i, item in enumerate(produtos_db, start=1):
        produtos.append({
            "id": item[0],
            "nome": item[1].capitalize(),
            "preco": item[2],
            "descricao": str(item[3]),
            "quantidade": int(item[4]),
            "imagem": item[5]
        })

    user={"role":current_user.role}
    notificacoes_ativas = get_notificacoes(current_user.id)    

    return render_template('menu.html', produtos=produtos, user=user, notificacoes_ativas=notificacoes_ativas)

@app.route('/requisitar/<int:numero>/<int:qnt>', methods=['GET', 'POST'])
def requistitar(numero, qnt):
    cursor.execute("SELECT quantidade FROM produtos WHERE id = %s", (numero,))
    quantidade = cursor.fetchone()[0]
    if quantidade >= qnt:
        cursor.execute("UPDATE produtos SET quantidade = %s WHERE id = %s", (quantidade - qnt, numero))
        conn.commit()
        return redirect('/menu')
    else:
        return jsonify({"message": "Quantidade indisponível"}), 400

@app.route('/contato', methods=['GET', 'POST'])
def contato():
    return render_template('chat.html')

@app.route('/configuracao', methods=['GET', 'POST'])
def configuracao():
    user = {"role": current_user.role}
    return render_template('configuracoes.html', user=user)

@app.route('/relatorios', methods=['GET', 'POST'])
def relatorios():
    user = {"role": current_user.role}
    sales = get_vendas()
    products = get_produtos()
    return render_template('relatorios.html', products=products, user=user, sales=sales)

@app.route('/api/sales', methods=['GET'])
def get_sales():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    products = request.args.getlist('products[]')
    sales = get_vendas()

    # Convert dates to datetime objects
    start = datetime.strptime(start_date, '%Y-%m-%d')
    end = datetime.strptime(end_date, '%Y-%m-%d')
    
    # Filter data based on date range and selected products
    filtered_data = {}
    for product in products:
        if product in sales:
            product_data = {}
            for date, value in sales[product].items():
                date_obj = datetime.strptime(date, '%Y-%m')
                if start <= date_obj <= end:
                    product_data[date] = value
            filtered_data[product] = product_data
    
    return jsonify(filtered_data)

@app.route('/generate-pdf', methods=['POST'])
def generate_pdf():
    try:
        print("entrou")
        data = request.json
        
        chart_image = base64.b64decode(data['chart_image'].split(",")[1])
        print("ola")
        pdf = create_sales_report_pdf(
            chart_image_data=chart_image,
            start_date=data['start_date'],
            end_date=data['end_date'],
            products=data['products']
        )
        return send_file(
            io.BytesIO(pdf),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'relatorio-vendas-{data["start_date"]}-{data["end_date"]}.pdf'
        )
    except Exception as e:
        return jsonify({
            'error': 'Erro ao gerar PDF',
            'details': str(e)
        }), 500


@app.route("/adm-chat")
@login_required
def adm():
    user = {"role": current_user.role, "nome": current_user.nome}
    client_list = db.get_client_info()
    return render_template("list_chats.html", client_list=client_list,user=user)

@app.route("/chat/<code>", methods=["GET", "POST"])
@app.route("/chat", methods=["GET", "POST"], defaults={'code': None})
@login_required
def chat(code):
    user = {"role": current_user.role, "nome": current_user.nome}
    if user['role'] == "admin" and code is None:
        return redirect('/adm-chat')
    
    if code is None:
        # Gera um novo código de chat e redireciona diretamente
        code = f"{user['nome']}-adm"
        if not db.table_exists(user['nome']):
            db.create_table(user['nome'])
            db.adm_append(user['nome'])
        return redirect(url_for("chat", code=code))
    else:
        # Lógica para a sala de chat
        if code.startswith("adm-"):
            user = code.split('-')[1]  # Extrai o nome do usuário após o hífen
            # Lógica para a sala de chat como administrador
            raw = db.get(user) if db.table_exists(user) else []
            #code = f"{user}-adm"
        else:
            # Lógica para a sala de chat normal
            raw = db.get(code.split('-')[0]) if db.table_exists(code.split('-')[0]) else []

        messages = [(x[1], x[2], x[3]) for x in raw]
    
        if messages:
            messages.reverse()
            age = messages[len(messages)-1][1]
            count = len(messages)
        else:
            age, count = "N/A", "N/A"
        
        if code.startswith("adm-"):
            adm = "adm"
            return render_template("chat.html", code=code, messages=messages, age=age, count=count, adm=adm, user=user)
        return render_template("chat.html", code=code, messages=messages, age=age, count=count, user=user)


# renders chat history page
@app.route("/chat/<code>/history", methods=["GET", "POST"])
def history(code):
    if code.startswith("adm-"):
        raw = db.get(code.split('-')[1])
    else:
        raw = db.get(code.split('-')[0])
    print(raw)
    print()
    # Update to handle 4 columns: user, message, date, read
    messages = [(x[1], x[2], x[3]) for x in raw]
    print(messages)

    if messages:
        messages.reverse()
        age = messages[len(messages)-1][2] # Date is now at index 2
        count = len(messages)
    else:
        age, count = "N/A", "N/A"

    return render_template("history.html", code=code, messages=messages, age=age, count=count)


# deletes account and information
@app.route("/delete-account/<user>")
def delete(user):
    global rooms
    print(rooms)
    print(user)
    for room in list(rooms.keys()):
        if user in rooms[room]:
            rooms.pop(room)
    db.adm_drop(user)
    db.drop_table(user)
    return redirect("/")



# method for socket broadcast
@socketio.on("message")
def handle_my_custom_event(json):
    global rooms
    user, code = json["user"], json["room"]

    
    if user.startswith("adm-"):
        user = user.split('-')[1]
        json.update({"user": "adm"})

    else:
        user = user.split('-')[0]
        json.update({"user": user})
    
    print("haha")
    print(json)
    dnow = datetime.now()

    if code not in rooms:
        rooms[code] = []
    if user not in rooms[code]:
        rooms[code].append(user)
        
        print(f"\n[Current connections] {len(rooms[code])}")
        print(f"[Current users] {rooms[code]}\n")

    print(f"\n[Message received] {json}\n")

    if "data" in json:
        if json["user"] == "adm":
            db.append(user, json["data"], dnow.strftime("%d/%m/%Y %H:%M"), "adm")
        else:
            db.append(user, json["data"], dnow.strftime("%d/%m/%Y %H:%M"))
        socketio.emit("relay", json)
    else:
        socketio.emit("online now", str(len(rooms[code])))


# method for socket disconnection
@socketio.on("disconnection")
def handle_disconnection(json):
	global rooms
	user, code = json["user"], json["room"]
	rooms[code].remove(user)

	print("\n[User disconnected]\n")

	if check_empty(rooms, code):
		rooms.pop(code)
	else:
		print(f"\n[Current connections] {len(rooms[code])}")
		print(f"[Current users] {rooms[code]}\n")
		print("AHAHAHH")

		socketio.emit("online now", str(len(rooms[code])))

users_db = {
    'enzonsei@gmail.com': {
        'password': 'senha123'
    }
}

@app.route('/esqueceu-senha', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        
        email_usuarios = get_emails()
        print(email_usuarios)
        if email in email_usuarios:
            # Gera token com validade de 1 hora
            token = serializer.dumps(email, salt='recover-key')
            
            # Cria o link de recuperação
            recover_url = url_for(
                'reset_password',
                token=token,
                _external=True
            )
            
            # Configura o email
            msg = Message(
                'Recuperação de Senha',
                sender=app.config['MAIL_USERNAME'],
                recipients=[email]
            )
            
            msg.body = f'''Para redefinir sua senha, visite o seguinte link:
            {recover_url}
            
            Se você não solicitou a redefinição de senha, ignore este email.
            
            O link é válido por 1 hora.
            '''
            
            # Envia o email
            mail.send(msg)
            
            flash('Um email com instruções foi enviado para você!', 'success')
            return redirect(url_for('forgot_password'))
        
        flash('Email não encontrado.', 'error')
    
    return render_template('forgot_password.html')

@app.route('/redefinir-senha/<token>', methods=['GET', 'POST'])
def reset_password(token):
    try:
        # Verifica se o token é válido e não expirou (3600 segundos = 1 hora)
        email = serializer.loads(token, salt='recover-key', max_age=3600)
    except:
        flash('O link de recuperação é inválido ou expirou.', 'error')
        return redirect('/esqueceu-senha')
    
    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if password != confirm_password:
            flash('As senhas não coincidem.', 'error')
            return render_template('reset_password.html')
        

        cursor.execute("UPDATE usuarios SET senha = %s WHERE email = %s", (password, email))
        conn.commit()
        
        flash('Sua senha foi atualizada com sucesso!', 'success')
        return redirect(url_for('login'))
    
    return render_template('reset_password.html')

def navbar_info():
    usuario = {
        "id": current_user.id,
        "role": current_user.role
        }
    cursor.execute("SELECT * FROM notificacoes WHERE usuario = %s", (usuario["id"], ))
    notificacoes_ativas = cursor.fetchall()
    return usuario, notificacoes_ativas


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, host='0.0.0.0', port=port, debug=True)
