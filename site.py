import csv, os
from os.path import exists
from flask import Flask, render_template, redirect, url_for, request


#diretório para armazenar as imagens
upload_folder = 'static/backup'

app = Flask(__name__)

#permitir fazer upload de imagens
app.config['upload_folder'] = upload_folder


#tipo começa como comum
tipo = "usuario"

#ao chamar a função acesso muda para administrador
def acesso():
    global tipo 
    tipo = "administrador" 

#acesso volta para o usuario
def clear():
    global tipo 
    tipo = "usuario"



#página inicial
@app.route("/")
def index():
    clear()
    return render_template("index.html")



#página de login
@app.route('/login', methods=['POST', 'GET'])
def login():
    
    erro = None
    
    if request.method == 'POST':

        usuario = request.form['usuario']
        senha = request.form['senha']

        if usuario == 'admin' and senha == '1234':
            acesso()
            return redirect(url_for('cadastro'))
        else:
            erro = "Usuário ou Senha Inválidos !!"

    return render_template('login.html', erro = erro)



#página de cadastro
@app.route("/cadastro", methods=['POST', 'GET'])
def cadastro():

    erro = None 
    mensagem = None

    if request.method == 'POST':

        nome = request.form['nome']
        categoria = request.form['select']
        descricao = request.form['descricao']
        arquivo = request.files['arquivo']
        
        if arquivo.filename == '' or nome == '' or descricao == '':

            erro = "Por favor, preencha todos os campos !!"

        else:

            path = os.path.join(app.config['upload_folder'], arquivo.filename)
            arquivo.save(path)

            global tasks

            tasks = [
                        {'nome': nome,'categoria': categoria,'descricao': descricao,'arquivo': path}
                    ]

            if not exists('cadastro.csv'):

                with open('cadastro.csv', 'xt') as file_out:
                    escritor = csv.DictWriter(file_out, ['nome', 'categoria', 'descricao', 'arquivo'])
                    escritor.writeheader()
                    escritor.writerows(tasks)

            else:

                with open('cadastro.csv', 'at') as file_out:
                    escritor = csv.DictWriter(file_out, ['nome', 'categoria', 'descricao', 'arquivo']) 
                    escritor.writerows(tasks)
                        
            mensagem = "Produto cadastrado com sucesso !!"

    return render_template('cadastro.html', erro = erro, mensagem = mensagem)



#página de listagem
@app.route("/lista", methods=['POST', 'GET'])
def lista():


    if tipo == "administrador":

        area_exclusiva = "sim"

        global tasks

        tasks = [
                 {'nome': nome,'categoria': categoria,'descricao': descricao,'arquivo': path}
                ]
        tasks.append(task)        


        with open('cadastro.csv','rt') as file_out:
            leitor= csv.DictReader(file_out,['nome','categoria','descricao','arquivo'])
            leitor.readheader()
            leitor.readrows(tasks)
            for linha in leitor:
                print(linha['nome'])

        return render_template('lista.html', area_exclusiva = area_exclusiva,tasks=tasks)

    else:

        return render_template('lista.html')



if __name__ == "__main__":
    app.run(debug=True)