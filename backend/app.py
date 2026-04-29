from flask import Flask, request, jsonify
from Usuarios import Usuarios

app = Flask(__name__)
gerencia_usuarios = Usuarios()


@app.route("/", methods=['GET'])
def hello_world():
    return "<p>Hello World asdasd</p>"


@app.route("/insere_usuario", methods=['POST'])
def insert_user():
    nome = request.form.get("nome")
    email = request.form.get("email")
    senha = request.form.get("senha")
    resposta = gerencia_usuarios.insert_user(nome, email, senha)
    return resposta


@app.route("/dados_usuario", methods=['POST'])
def dados_usuario():
    email = request.form.get("email")
    resposta = gerencia_usuarios.return_user_by_email(email)
    return resposta
