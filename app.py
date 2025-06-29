from flask import Flask, render_template, request, redirect, url_for, session # type: ignore
import sqlite3

app = Flask(__name__)
app.secret_key = 'chave_super_secreta'

# Conectar ao banco
def conectar():
    return sqlite3.connect('banco.db')

@app.route('/')
def index():
    mensagem_confirmacao = session.pop('mensagem_confirmacao', '')
    return render_template('index.html', mensagem_confirmacao=mensagem_confirmacao)

@app.route('/confirmar', methods=['POST'])
def confirmar():
    nome = request.form['nome'].strip()
    if nome:
        con = conectar()
        cur = con.cursor()
        cur.execute('INSERT INTO convidados (nome) VALUES (?)', (nome,))
        con.commit()
        con.close()
        session['mensagem_confirmacao'] = f"{nome}, 🥳 sua presença foi confirmada!🎉"
    return redirect(url_for('index'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    erro = ''
    if request.method == 'POST':
        senha = request.form['senha']
        if senha == 'Ane2001':
            session['logado'] = True
            return redirect(url_for('confirmados'))
        else:
            erro = 'Senha incorreta!'
    return render_template('login.html', erro=erro)

@app.route('/confirmados')
def confirmados():
    if not session.get('logado'):
        return redirect(url_for('login'))
    con = conectar()
    cur = con.cursor()
    cur.execute('SELECT id, nome FROM convidados')
    nomes = cur.fetchall()
    total = len(nomes)
    con.close()
    return render_template('confirmados.html', nomes=nomes, total=total)

@app.route('/excluir/<int:id>', methods=['POST'])
def excluir(id):
    if not session.get('logado'):
        return redirect(url_for('login'))
    con = conectar()
    cur = con.cursor()
    cur.execute('DELETE FROM convidados WHERE id = ?', (id,))
    con.commit()
    con.close()
    return redirect(url_for('confirmados'))

@app.route('/logout')
def logout():
    session.pop('logado', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    # Criar tabela se não existir
    con = conectar()
    cur = con.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS convidados (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL)''')
    con.commit()
    con.close()
    app.run(debug=True)
