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

#ao chamar a função o acesso muda para administrador
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

    id = '1'
    mensagem = None

    #atribui um id para cada produto
    if exists('cadastro.csv'):

        count = '0'

        with open('cadastro.csv', 'rt') as file_in:
            leitor = csv.DictReader(file_in)
            for row in leitor:
                produtos = dict(row)
                if produtos['id'] >= count:
                    id = int(produtos['id'])
            id = id + 1


    #cadastra os produtos
    if request.method == 'POST':

        nome = request.form['nome']
        categoria = request.form['select']
        descricao = request.form['descricao']
        arquivo = request.files['arquivo']

        #salva as imagens na pasta definida na variável upload_folder
        path = os.path.join(app.config['upload_folder'], arquivo.filename)
        arquivo.save(path)

        #lista de dicionários
        tasks = [
                    {'id': id, 'nome': nome,'categoria': categoria,'descricao': descricao,'arquivo': 'static/backup/' + arquivo.filename}
                ]

        if not exists('cadastro.csv'):

            #xt - cria um arquivo se ele não existir
            with open('cadastro.csv', 'xt') as file_out:
                escritor = csv.DictWriter(file_out, ['id', 'nome', 'categoria', 'descricao', 'arquivo'])
                escritor.writeheader()
                escritor.writerows(tasks)

        else:

            #at - adiciona ao final do arquivo se ele existir
            with open('cadastro.csv', 'at') as file_out:
                escritor = csv.DictWriter(file_out, ['id', 'nome', 'categoria', 'descricao', 'arquivo']) 
                escritor.writerows(tasks)
                    
        mensagem = "Produto cadastrado com sucesso !!"

    return render_template('cadastro.html', mensagem = mensagem)



#página de listagem
@app.route("/lista/", methods=['POST', 'GET'])
def lista():

    pesquisa = ""

    #pesquisa transformando as palavras em letras minúsculas
    if request.method == 'POST':

        pesquisa = request.form['pesquisa'].lower()
            
    #se o arquivo cadastro.csv não existir mostra a lista vazia
    if not exists('cadastro.csv'):

        if tipo == "administrador":

            area_exclusiva = "sim"

            return render_template('lista.html', area_exclusiva = area_exclusiva, pesquisa = pesquisa)

        else:
            
            return render_template('lista.html', pesquisa = pesquisa)
    
    #se existir mostra a lista com os dados correspondentes
    else:

        with open('cadastro.csv', 'rt') as file_in:
            leitor = csv.DictReader(file_in)

            if tipo == "administrador":

                area_exclusiva = "sim"

                return render_template('lista.html', area_exclusiva = area_exclusiva, leitor = leitor, pesquisa = pesquisa)

            else:

                return render_template('lista.html', leitor = leitor, pesquisa = pesquisa)



#página de alteração para mostrar os dados do produto
@app.route("/alteracao/<id>", methods=['POST', 'GET'])
def alteracao(id):

    with open('cadastro.csv', 'rt') as file_in:
        leitor = csv.DictReader(file_in)
        for row in leitor:
            produtos = dict(row)
            if produtos['id'] == id:   
                return render_template('alteracao.html', produtos = produtos)
                


#página de alteração para alterar os dados do produto
@app.route("/alteracaoProdutos/<id>", methods=['POST', 'GET'])
def alteracao_produtos(id):

    new_tasks = []

    if request.method == 'POST':

        nome = request.form['nome']
        categoria = request.form['select']
        descricao = request.form['descricao']
        arquivo = request.files['arquivo']

        #cria uma nova lista, substituindo a linha do produto escolhido
        with open('cadastro.csv', 'rt') as file_in:
            leitor = csv.DictReader(file_in)
            for row in leitor:
                produtos = dict(row)
                if produtos['id'] == id: 

                    #remove a imagem da pasta
                    os.remove(produtos['arquivo'])
                    
                    #salva a nova imagem na pasta
                    path = os.path.join(app.config['upload_folder'], arquivo.filename)
                    arquivo.save(path)

                    new_tasks.append({'id': id, 'nome': nome,'categoria': categoria,'descricao': descricao,'arquivo': 'static/backup/' + arquivo.filename})
                
                else:
                
                    new_tasks.append(produtos)

        #wt - substitui o arquivo se ele existir e cria um caso contrário
        with open('cadastro.csv', 'wt') as file_out:
            escritor = csv.DictWriter(file_out, ['id', 'nome', 'categoria', 'descricao', 'arquivo'])
            escritor.writeheader()
            escritor.writerows(new_tasks)

    return redirect(url_for('lista'))



#página de exclusão
@app.route("/exclusao/<id>", methods=['POST', 'GET'])
def exclusao(id):

    new_tasks = []

    #exclui o produto selecionado
    with open('cadastro.csv', 'rt') as file_in:
        leitor = csv.DictReader(file_in)
        for row in leitor:
            produtos = dict(row)
            new_tasks.append(produtos)
            if produtos['id'] == id:   
                new_tasks.remove(produtos)
                #remove a imagem da pasta
                os.remove(produtos['arquivo'])

    #wt - substitui o arquivo se ele existir e cria um caso contrário
    with open('cadastro.csv', 'wt') as file_out:
        escritor = csv.DictWriter(file_out, ['id', 'nome', 'categoria', 'descricao', 'arquivo'])
        escritor.writeheader()
        escritor.writerows(new_tasks)
    
    return redirect(url_for('lista'))


if __name__ == "__main__":
    app.run(debug=True)