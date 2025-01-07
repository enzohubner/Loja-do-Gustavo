import base64
from datetime import datetime
import io
from flask import Flask, request, render_template, redirect, jsonify, send_file, url_for
import psycopg2
from psycopg2 import sql
from flask_socketio import SocketIO
from db import cursor, conn
from utils.pdf_generator import create_sales_report_pdf
from components.database import DataBase
from components.utilities import *

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

app = Flask(__name__)
app.config('SECRET_KEY')
socketio = SocketIO(app)

db = DataBase()
rooms = {}
print("teste", rooms, "iniciais")

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
        return render_template('cadastro.html')
    
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
        usuario = {
            'id': 'usuario',
            'email': 'usuario@',
            'telefone': '99999-9999',
            'escola': 'Escola XYZ'
        }
        return render_template('altera_usuario.html', usuario=usuario)


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

@app.route('/editar_produto/<int:id>', methods=['GET', 'POST'])
def editar_produto(id):
    cursor.execute("SELECT * FROM produtos WHERE id=%s", (id,))
    produto = cursor.fetchone()

    if request.method == 'POST':

        id = request.form['codigo']  
        nome = request.form['nome'] 
        valor = request.form['valor']
        descricao = request.form['descricao']

        '''Cara, tive que aprender pra testar se a pagina tava funcionando, entao vou deixar aqui pq deve te ajudar
        em algum momento, o request.files.get('imagem') pega a imagem que o usuario submeteu, e o save salva ela na pasta 
        que no nosso caso é imagens! Depois de salvar ela na pasta, no banco de dados voce só vai salvar o caminho dela
        que é o f' imagens/{imagem.filename}'  '''

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
        return render_template('editar_produto.html', produto=produto)

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
    usuario = "admin"
    
    return render_template('navbar.html', notificacoes_ativas=notificacoes_ativas, usuario=usuario)

@app.route('/notificacoes', methods=['GET', 'POST'])
def notificacoes():
    return render_template('notificacoes.html')

@app.route('/menu', methods=['GET', 'POST'])
def menu():
    produtos = [
        {"id": 1, "nome": "Produto A", "descricao": "Descrição do Produto A", "preco": 10.99, "quantidade": 100, "imagem":'/static/png-logo-black.png'},
        {"id": 2, "nome": "Produto B", "descricao": "Descrição do Produto B", "preco": 20.99, "quantidade": 200},
        {"id": 3, "nome": "Produto C", "descricao": "Descrição do Produto C", "preco": 30.99, "quantidade": 300},
        {"id": 4, "nome": "Produto D", "descricao": "Descrição do Produto D", "preco": 40.99, "quantidade": 400},
        {"id": 5, "nome": "Produto E", "descricao": "Descrição do Produto E", "preco": 50.99, "quantidade": 500},
        {"id": 6, "nome": "Produto F", "descricao": "Descrição do Produto E", "preco": 50.99, "quantidade": 500}
    ]

    user= {'role' : 'admin'}

    return render_template('menu.html', produtos=produtos, user=user)

@app.route('/navbar_alternativa', methods=['GET', 'POST'])
def navbar_alternativa():
    notificacoes_ativas = [
        {"notificacao": "Notificação 1", "permissao":'admin'},
        {"notificacao": "Notificação 2", "permissao":'funcionario'},
        {"notificacao": "Notificação 3", "permissao":'usuario'}]
    role = 'admin'
    return render_template('navbar_alternativa.html', role=role, notificacoes_ativas=notificacoes_ativas)

@app.route('/contato', methods=['GET', 'POST'])
def contato():
    return render_template('chat.html')

@app.route('/configuracao', methods=['GET', 'POST'])
def configuracao():
    return render_template('configuracoes.html')

PRODUCTS = [
    {"id": 1, "name": "Alfajor"},
    {"id": 2, "name": "Bolos"},
    {"id": 3, "name": "Cookies"},
    {"id": 4, "name": "Doces"}
]

# Sample sales data
SALES_DATA = {
    "Alfajor": {
        "2024-01": 50, "2024-02": 75, "2024-03": 100,
        "2024-04": 120, "2024-05": 90, "2024-06": 130,
        "2024-07": 140, "2024-08": 145, "2024-09": 130,
        "2024-10": 110, "2024-11": 90, "2024-12": 110
    },
    "Bolos": {
        "2024-01": 80, "2024-02": 100, "2024-03": 120,
        "2024-04": 140, "2024-05": 110, "2024-06": 150,
        "2024-07": 160, "2024-08": 170, "2024-09": 130,
        "2024-10": 100, "2024-11": 100, "2024-12": 120
    }
}
@app.route('/relatorios', methods=['GET', 'POST'])
def relatorios():
    return render_template('relatorios.html', products=PRODUCTS)

@app.route('/api/sales', methods=['GET'])
def get_sales():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    products = request.args.getlist('products[]')
    
    # Convert dates to datetime objects
    start = datetime.strptime(start_date, '%Y-%m-%d')
    end = datetime.strptime(end_date, '%Y-%m-%d')
    
    # Filter data based on date range and selected products
    filtered_data = {}
    for product in products:
        if product in SALES_DATA:
            product_data = {}
            for date, value in SALES_DATA[product].items():
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
def adm():
    client_list = db.get_client_info()
    return render_template("list_chats.html", client_list=client_list)

@app.route("/chat/<code>", methods=["GET", "POST"])
@app.route("/chat", methods=["GET", "POST"], defaults={'code': None})
def chat(code):
    user = "adm"  # Exemplo de usuário, você pode obter isso de uma sessão ou autenticação
    adm = "adm"

    if user == "adm" and code is None:
        return redirect('/adm-chat')
    
    if code is None:
        # Gera um novo código de chat e redireciona diretamente
        code = f"{user}-{adm}"
        if not db.table_exists(user):
            db.create_table(user)
            db.adm_append(user)
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
            return render_template("chat.html", code=code, messages=messages, age=age, count=count, adm=adm)
        return render_template("chat.html", code=code, messages=messages, age=age, count=count)


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




if __name__ == '__main__':
    socketio.run(app, debug=True)
