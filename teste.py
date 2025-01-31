from flask import Flask, request, render_template, redirect, jsonify
import psycopg2
from psycopg2 import sql
from db import cursor, conn

# cursor.execute("UPDATE notificacoes SET coluna1 = novo_valor1, coluna2 = novo_valor2 WHERE condicao;")
cursor.execute("CREATE TABLE requisicoes (id SERIAL PRIMARY KEY,id_usuario INT NOT NULL,id_produto INT NOT NULL,quantidade INT NOT NULL CHECK (quantidade > 0),data_requisicao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,FOREIGN KEY (id_usuario) REFERENCES usuarios(id) ON DELETE CASCADE,FOREIGN KEY (id_produto) REFERENCES produtos(id) ON DELETE CASCADE);") 
printar = cursor.fetchall()
print(printar)
"""cursor.execute("INSERT INTO produtos (nome, valor, descricao) VALUES ('produtob', '1234', 'testeb')")
cursor.execute("CREATE TABLE produtos (id SERIAL PRIMARY KEY, nome VARCHAR(100), valor VARCHAR(5), descricao VARCHAR(255) UNIQUE)")
conn.commit()
SELECT column_name, data_type, is_nullable, column_default FROM information_schema.columns WHERE table_name = 'notificacoes';
cursor.execute("DROP TABLE produtos")
conn.commit()
cursor.execute("CREATE TABLE produtos (id SERIAL PRIMARY KEY, nome VARCHAR(100), valor INT, descricao VARCHAR(255) UNIQUE)")
conn.commit()
cursor.execute("SELECT * from produtos")
usuarios = cursor.fetchall()
print(usuarios)
"""
