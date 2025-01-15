from flask import Flask, request, render_template, redirect, jsonify
import psycopg2
from psycopg2 import sql
from db import cursor, conn

cursor.execute("INSERT INTO produtos (nome, valor, descricao) VALUES ('produtob', '1234', 'testeb')")

cursor.execute("SELECT * FROM produtos")
usuarios = cursor.fetchall()
print(usuarios)
"""
cursor.execute("CREATE TABLE produtos (id SERIAL PRIMARY KEY, nome VARCHAR(100), valor VARCHAR(5), descricao VARCHAR(255) UNIQUE)")
conn.commit()
cursor.execute("DROP TABLE produtos")
conn.commit()
cursor.execute("CREATE TABLE produtos (id SERIAL PRIMARY KEY, nome VARCHAR(100), valor INT, descricao VARCHAR(255) UNIQUE)")
conn.commit()
cursor.execute("SELECT * from produtos")
usuarios = cursor.fetchall()
print(usuarios)
"""
