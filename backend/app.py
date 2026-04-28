from datetime import datetime
import psycopg2
import bcrypt
from config import DATABASE_URL


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
        senha_hashed = bcrypt.hashpw(senha, salt)
        parametros = (nome, email, senha_hashed, datetime.now())
        try:
            self.cursor.execute(
                f"""INSERT INTO usuarios (nome, email, senha, createdAt) VALUES (%s, %s, %s, %s);""", parametros)
            self.connection.commit()
            return "Sucesso. Usuário inserido com sucesso"
        except Exception as e:
            return f"Erro. Falha ao inserir usuário: {e}"

    def return_user(self, email):
        try:
            self.cursor.execute(
                """SELECT * FROM usuarios WHERE email = %s;""", (email,))
            resposta = self.cursor.fetchone()
            return resposta
        except Exception as e:
            return f"Erro. Fala ao buscar usuário: {e}"


gestor_usuarios = Usuarios()
# print(gestor_usuarios.insert_user("Rodrigo Duque", "rodukao@gmail.com", b"123456"))
print(gestor_usuarios.return_user("rodukao@gmail.com"))
