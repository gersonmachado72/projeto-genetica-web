from flask import current_app
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from database import mysql
import json

class Usuario(UserMixin):
    def __init__(self, id, nome, email, senha_hash, data_registro=None, ultimo_login=None, ativo=True):
        self.id = id
        self.nome = nome
        self.email = email
        self.senha_hash = senha_hash
        self.data_registro = data_registro
        self.ultimo_login = ultimo_login
        self.ativo = ativo
    
    @staticmethod
    def get_by_id(user_id):
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE id = %s", (user_id,))
        row = cursor.fetchone()
        cursor.close()
        if row:
            return Usuario(row['id'], row['nome'], row['email'], row['senha_hash'], 
                          row['data_registro'], row['ultimo_login'], row['ativo'])
        return None
    
    @staticmethod
    def get_by_email(email):
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
        row = cursor.fetchone()
        cursor.close()
        if row:
            return Usuario(row['id'], row['nome'], row['email'], row['senha_hash'],
                          row['data_registro'], row['ultimo_login'], row['ativo'])
        return None
    
    @staticmethod
    def create(nome, email, senha):
        senha_hash = generate_password_hash(senha)
        cursor = mysql.connection.cursor()
        cursor.execute(
            "INSERT INTO usuarios (nome, email, senha_hash) VALUES (%s, %s, %s)",
            (nome, email, senha_hash)
        )
        mysql.connection.commit()
        cursor.close()
        return True
    
    def check_password(self, senha):
        return check_password_hash(self.senha_hash, senha)
    
    def update_last_login(self):
        cursor = mysql.connection.cursor()
        cursor.execute(
            "UPDATE usuarios SET ultimo_login = NOW() WHERE id = %s",
            (self.id,)
        )
        mysql.connection.commit()
        cursor.close()

class Analise:
    @staticmethod
    def create(usuario_id, sequencia, arquivo_original=None, paciente_id=None):
        cursor = mysql.connection.cursor()
        cursor.execute(
            """INSERT INTO analises 
               (usuario_id, paciente_id, arquivo_original, sequencia, tamanho, status) 
               VALUES (%s, %s, %s, %s, %s, 'concluido')""",
            (usuario_id, paciente_id, arquivo_original, sequencia, len(sequencia))
        )
        analise_id = cursor.lastrowid
        mysql.connection.commit()
        cursor.close()
        return analise_id
    
    @staticmethod
    def save_result(analise_id, resultado):
        cursor = mysql.connection.cursor()
        cursor.execute(
            """UPDATE analises 
               SET resultado_json = %s, status = 'concluido', 
                   conteudo_gc = %s, data_analise = NOW()
               WHERE id = %s""",
            (json.dumps(resultado, ensure_ascii=False), 
             resultado['composicao']['gc'], analise_id)
        )
        mysql.connection.commit()
        cursor.close()
        
        for mutacao in resultado.get('mutacoes', []):
            cursor = mysql.connection.cursor()
            cursor.execute(
                """INSERT INTO mutacoes_detectadas 
                   (analise_id, gene, mutacao, doenca, risco, frequencia, descricao) 
                   VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                (analise_id, mutacao['gene'], mutacao['mutacao'], 
                 mutacao['doenca'], mutacao['risco'], 
                 mutacao['frequencia'], mutacao['descricao'])
            )
            mutacao_id = cursor.lastrowid
            mysql.connection.commit()
            
            for i, rec in enumerate(mutacao.get('recomendacoes', [])):
                cursor.execute(
                    "INSERT INTO recomendacoes (mutacao_id, texto, ordem) VALUES (%s, %s, %s)",
                    (mutacao_id, rec, i)
                )
            mysql.connection.commit()
            cursor.close()
    
    @staticmethod
    def get_by_user(usuario_id, limit=50, offset=0):
        cursor = mysql.connection.cursor()
        cursor.execute(
            """SELECT * FROM analises 
               WHERE usuario_id = %s 
               ORDER BY data_analise DESC 
               LIMIT %s OFFSET %s""",
            (usuario_id, limit, offset)
        )
        rows = cursor.fetchall()
        cursor.close()
        return rows
    
    @staticmethod
    def get_by_id(analise_id):
        cursor = mysql.connection.cursor()
        cursor.execute(
            """SELECT a.*, u.nome as usuario_nome 
               FROM analises a 
               LEFT JOIN usuarios u ON a.usuario_id = u.id 
               WHERE a.id = %s""",
            (analise_id,)
        )
        row = cursor.fetchone()
        cursor.close()
        return row
    
    @staticmethod
    def get_mutacoes(analise_id):
        cursor = mysql.connection.cursor()
        cursor.execute(
            """SELECT m.*, GROUP_CONCAT(r.texto ORDER BY r.ordem SEPARATOR '|||') as recomendacoes 
               FROM mutacoes_detectadas m
               LEFT JOIN recomendacoes r ON m.id = r.mutacao_id
               WHERE m.analise_id = %s
               GROUP BY m.id""",
            (analise_id,)
        )
        rows = cursor.fetchall()
        cursor.close()
        return rows
    
    @staticmethod
    def count_by_user(usuario_id):
        cursor = mysql.connection.cursor()
        cursor.execute(
            "SELECT COUNT(*) as total FROM analises WHERE usuario_id = %s",
            (usuario_id,)
        )
        row = cursor.fetchone()
        cursor.close()
        return row['total'] if row else 0

class LogAuditoria:
    @staticmethod
    def log(usuario_id, acao, detalhes, ip=None):
        cursor = mysql.connection.cursor()
        cursor.execute(
            "INSERT INTO logs_auditoria (usuario_id, acao, detalhes, ip) VALUES (%s, %s, %s, %s)",
            (usuario_id, acao, detalhes, ip)
        )
        mysql.connection.commit()
        cursor.close()
