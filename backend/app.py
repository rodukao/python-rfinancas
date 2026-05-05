from flask import Flask, request, make_response
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


@app.route("/insere_sessao", methods=['POST'])
def insert_session():
    token = gerencia_usuarios.create_token()
    email_usuario = request.form.get("email")
    resposta = gerencia_usuarios.create_session(email_usuario, token)
    print(resposta)
    if resposta['status'] == "success":
        resp = make_response(resposta['message'])
        resp.set_cookie("token", token,
                        httponly=True,
                        secure=True,
                        samesite='Lax')
        return resp
    else:
        return make_response(resposta['message']), 400
