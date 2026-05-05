from datetime import datetime
import psycopg2
import bcrypt
import secrets
from config import DATABASE_URL


class Usuarios:
    def __init__(self):
        self.connection = psycopg2.connect(DATABASE_URL)
        self.create_user_tables()

    def create_user_tables(self):
        """
        Criamos as tabelas de usuário e sessões
        as sessões possuem um token que será vinculado ao usuário e ao navegador.
        Ao fazer login compararemos os tokens e se for igual concederemos acesso.
        """

        query_table_user = """CREATE TABLE IF NOT EXISTS usuarios (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(), 
        nome TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        senha TEXT NOT NULL,
        createdAt DATE
        )"""

        query_table_sessions = """CREATE TABLE IF NOT EXISTS sessoes (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        token TEXT NOT NULL,
        email_usuario TEXT NOT NULL REFERENCES usuarios(email),
        createdAt DATE NOT NULL
        )"""

        with self.connection:
            cursor = self.connection.cursor()
            cursor.execute(query_table_user)
            cursor.execute(query_table_sessions)
            self.connection.commit()

    def insert_user(self, nome, email, senha):
        """
        Inserimos o usuário com nome, email, senha e a data da criação.
        Em caso de sucesso retornamos uma string iniciada com 'Sucesso', caso contrário uma string iniciada com 'Erro'
        """

        salt = bcrypt.gensalt()
        senha_hashed = bcrypt.hashpw(senha.encode("utf-8"), salt)
        parametros = (nome, email, senha_hashed.decode(
            "utf-8"), datetime.now())
        with self.connection:
            try:
                cursor = self.connection.cursor()
                cursor.execute(
                    f"""INSERT INTO usuarios (nome, email, senha, createdAt) VALUES (%s, %s, %s, %s);""", parametros)
                self.connection.commit()
                return "Sucesso. Usuário inserido com sucesso."
            except Exception as e:
                return f"Erro. Falha ao inserir usuário: {e}"

    def return_user_by_email(self, email):
        """
        Procuramos o usuário no banco com o email.
        Se obtivermos sucesso ao buscar retornamos um objeto com 'id', 'nome', 'email', 'senha'.
        Em caso de erro uma string iniciada com 'Erro'
        """

        with self.connection:
            try:
                cursor = self.connection.cursor()
                cursor.execute(
                    """SELECT * FROM usuarios WHERE email = %s;""", (email,))
                resposta = cursor.fetchone()
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
        """
        Buscamos o usuário por email e comparamos a senha retornada do banco com a senha informada criptografada.
        Se forem as mesmas a gente retorna o usuário.
        Se não coincidirem a gente retorna uma string iniciada com 'Erro'
        """

        with self.connection:
            try:
                cursor = self.connection.cursor()
                cursor.execute(
                    """SELECT * FROM usuarios WHERE email = %s""", (email,))
                usuario = cursor.fetchone()
                senha_banco = usuario[3].encode("utf-8")
                valid_user = bcrypt.checkpw(senha.encode("utf-8"), senha_banco)
                if valid_user:
                    return usuario
                else:
                    return f"Erro. Email ou senha incorretos."
            except Exception as e:
                return f"Erro. Falha ao validar usuário: {e}"

    def atualiza_senha(self, email, nova_senha):
        """
        Criptografamos a senha enviada e a salvamos no banco utilizando o email do usuário
        """

        salt = bcrypt.gensalt()
        nova_senha_hashed = bcrypt.hashpw(nova_senha, salt)
        parametros = (nova_senha_hashed, email)
        with self.connection:
            try:
                cursor = self.connection.cursor()
                cursor.execute(
                    """UPDATE usuarios SET senha = %s WHERE email = %s""", (parametros))
                self.connection.commit()
                return "Sucesso. Senha atualizada com sucesso."
            except Exception as e:
                return f"Erro. Falha ao atualizar senha do usuário: {e}"

    def delet_user(self, email):
        """
        Deletemos usuário do banco utilizando o email
        """

        with self.connection:
            try:
                cursor = self.connection.cursor()
                cursor.execute(
                    """DELETE FROM usuarios WHERE email = %s""", (email,))
                self.connection.commit()
                return "Sucesso. Usuário deletado com sucesso."
            except Exception as e:
                return f"Erro. Falha ao deletar usuário: {e}"

    def create_token(self):
        """
        Criamos e retornamos um token usando a biblioteca secrets
        """

        return secrets.token_urlsafe()

    def create_session(self, email_usuario, token):
        """
        Criamos uma sessão no banco de dados e a atribuimos a um usuário
        """

        parametros = (token, email_usuario, datetime.now())
        with self.connection:
            try:
                cursor = self.connection.cursor()
                cursor.execute(
                    """INSERT INTO sessoes (token, email_usuario, createdAt) VALUES (%s, %s, %s)""", parametros)
                self.connection.commit()
                return {"status": "success", "message": "Sessão inserida com sucesso!"}
            except Exception as e:
                return {"status": "error", "message": f"Falha ao inserir sessão: {e}"}
