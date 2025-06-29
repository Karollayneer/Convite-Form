import os
from flask import Flask, render_template, request, redirect, url_for, session # type: ignore
from flask_sqlalchemy import SQLAlchemy # type: ignore

app = Flask(__name__)
app.secret_key = 'chave_super_secreta'

# Configuração do banco: variável de ambiente DATABASE_URL ou fallback para SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL', 
    'sqlite:///banco.db'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Modelo do banco
class Convidado(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)

# Rotas
@app.route('/')
def index():
    mensagem_confirmacao = session.pop('mensagem_confirmacao', '')
    return render_template('index.html', mensagem_confirmacao=mensagem_confirmacao)

@app.route('/confirmar', methods=['POST'])
def confirmar():
    nome = request.form['nome'].strip()
    if nome:
        novo = Convidado(nome=nome)
        db.session.add(novo)
        db.session.commit()
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
    nomes = Convidado.query.all()
    total = len(nomes)
    return render_template('confirmados.html', nomes=nomes, total=total)

@app.route('/excluir/<int:id>', methods=['POST'])
def excluir(id):
    if not session.get('logado'):
        return redirect(url_for('login'))
    convidado = Convidado.query.get(id)
    if convidado:
        db.session.delete(convidado)
        db.session.commit()
    return redirect(url_for('confirmados'))

@app.route('/logout')
def logout():
    session.pop('logado', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
