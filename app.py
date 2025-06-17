from flask import Flask, render_template, request, redirect, url_for, session # type: ignore
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'chave_super_secreta'


# Função para conectar ao banco
def conectar():
    return sqlite3.connect('banco.db')


# Buscar todos os confirmados
def buscar_confirmados():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome FROM confirmados")
    dados = cursor.fetchall()
    conn.close()
    return dados


# Inserir novo nome
def inserir_confirmado(nome):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO confirmados (nome) VALUES (?)", (nome,))
    conn.commit()
    conn.close()


# Excluir nome pelo ID
def excluir_confirmado(id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM confirmados WHERE id = ?", (id,))
    conn.commit()
    conn.close()


# Rota inicial
@app.route('/')
def index():
    confirmados = buscar_confirmados()
    mensagem_confirmacao = session.pop('mensagem_confirmacao', None)
    return render_template('index.html',
                           total_confirmados=len(confirmados),
                           mensagem_confirmacao=mensagem_confirmacao)


# Rota para confirmar presença
@app.route('/confirmar', methods=['POST'])
def confirmar():
    nome = request.form.get('nome')
    if nome:
        inserir_confirmado(nome)
        session['mensagem_confirmacao'] = f"Presença confirmada, {nome}! 🎉"
    return redirect(url_for('index'))


# Rota de login (admin)
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        senha = request.form.get('senha')
        if senha == 'Ane2001':
            session['logado'] = True
            return redirect(url_for('lista_confirmados'))
        else:
            return render_template('login.html', erro="Senha incorreta!")
    return render_template('login.html')


# Página dos confirmados (admin)
@app.route('/confirmados')
def lista_confirmados():
    if not session.get('logado'):
        return redirect(url_for('login'))
    confirmados = buscar_confirmados()
    return render_template('confirmados.html',
                           nomes=confirmados,
                           total=len(confirmados))


# Excluir um confirmado (admin)
@app.route('/excluir/<int:id>', methods=['POST'])
def excluir(id):
    if not session.get('logado'):
        return redirect(url_for('login'))
    excluir_confirmado(id)
    return redirect(url_for('lista_confirmados'))


# Logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


# Execução
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
