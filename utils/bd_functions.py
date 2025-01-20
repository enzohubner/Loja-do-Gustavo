from db import cursor, conn

def get_notificacoes(id_usuario):
    cursor.execute('SELECT * FROM notificacoes WHERE usuario = %s', (id_usuario,))
    rows = cursor.fetchall()
    return rows

def get_produtos():
    cursor.execute('SELECT id, nome FROM produtos')
    rows = cursor.fetchall()
    return [{"id": row[0], "name": row[1]} for row in rows]

def get_vendas():
    cursor.execute('''
        SELECT 
            nome_produto,
            to_char(data_venda, 'YYYY-MM') as month,
            SUM(quantidade) as total_vendas
        FROM vendas
        GROUP BY nome_produto, to_char(data_venda, 'YYYY-MM')
        ORDER BY nome_produto, month
    ''')
    rows = cursor.fetchall()
    sales_data = {}
    for row in rows:
        produto, month, quantidade = row
        if produto not in sales_data:
            sales_data[produto] = {}
        sales_data[produto][month] = quantidade

    print(sales_data)
    return sales_data