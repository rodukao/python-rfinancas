from datetime import datetime
import psycopg2
import bcrypt
from config import DATABASE_URL
import json


class Usuarios:
    def __init__(self):
        self.connection = psycopg2.connect(DATABASE_URL)
        self.cursor = self.connection.cursor()
        self.create_user_tables()

    def create_user_tables(self):
        query = """CREATE TABLE IF NOT EXISTS usuarios (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(), 
        nome TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        senha TEXT NOT NULL,
        createdAt DATE
        )"""
        self.cursor.execute(query)
        self.connection.commit()

    def insert_user(self, nome, email, senha):
        salt = bcrypt.gensalt()
        senha_hashed = bcrypt.hashpw(senha.encode("utf-8"), salt)
        parametros = (nome, email, senha_hashed.decode(
            "utf-8"), datetime.now())
        try:
            self.cursor.execute(
                f"""INSERT INTO usuarios (nome, email, senha, createdAt) VALUES (%s, %s, %s, %s);""", parametros)
            self.connection.commit()
            return "Sucesso. Usuário inserido com sucesso."
        except Exception as e:
            return f"Erro. Falha ao inserir usuário: {e}"

    def return_user_by_email(self, email):
        try:
            self.cursor.execute(
                """SELECT * FROM usuarios WHERE email = %s;""", (email,))
            resposta = self.cursor.fetchone()
            if resposta:
                return {
                    "id": resposta[0],
                    "nome": resposta[1],
                    "email": resposta[2],
                    "senha": resposta[3]
                }
            else:
                return None
        except Exception as e:
            return f"Erro. Fala ao buscar usuário: {e}"

    def validate_user(self, email, senha):
        try:
            self.cursor.execute(
                """SELECT * FROM usuarios WHERE email = %s""", (email,))
            usuario = self.cursor.fetchone()
            senha_banco = usuario[3].encode("utf-8")
            valid_user = bcrypt.checkpw(senha.encode("utf-8"), senha_banco)
            if valid_user:
                return usuario
            else:
                return f"Erro. Email ou senha incorretos."
        except Exception as e:
            return f"Erro. Falha ao validar usuário: {e}"

    def atualiza_senha(self, email, nova_senha):
        salt = bcrypt.gensalt()
        nova_senha_hashed = bcrypt.hashpw(nova_senha, salt)
        parametros = (nova_senha_hashed, email)
        try:
            self.cursor.execute(
                """UPDATE usuarios SET senha = %s WHERE email = %s""", (parametros))
            self.connection.commit()
            return "Sucesso. Senha atualizada com sucesso."
        except Exception as e:
            return f"Erro. Falha ao atualizar senha do usuário: {e}"

    def delet_user(self, email):
        try:
            self.cursor.execute(
                """DELETE FROM usuarios WHERE email = %s""", (email,))
            self.connection.commit()
            return "Sucesso. Usuário deletado com sucesso."
        except Exception as e:
            return f"Erro. Falha ao deletar usuário: {e}"
