import sqlite3
from flask import g

DATABASE = 'db.sqlite3'

def get_db():
    # Verifica se a conexão já existe no contexto da requisição
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    # Fecha a conexão ao final da requisição, se ela existir
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS conta_bancaria (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 nome TEXT NOT NULL,
                 saldo_inicial REAL DEFAULT 0.0)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS centro_custo (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 nome TEXT NOT NULL)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS plano_contas (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 nome TEXT NOT NULL,
                 categoria_pai INTEGER,
                 centro_custo_id INTEGER,
                 FOREIGN KEY (categoria_pai) REFERENCES plano_contas(id),
                 FOREIGN KEY (centro_custo_id) REFERENCES centro_custo(id))''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS fornecedor (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 cnpj TEXT UNIQUE NOT NULL,
                 nome_fantasia TEXT NOT NULL,
                 razao_social TEXT NOT NULL)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS cliente (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 cpf_cnpj TEXT UNIQUE NOT NULL,
                 nome TEXT NOT NULL)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS forma_pagamento (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 nome TEXT NOT NULL)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS lancamento (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 data_lancamento TEXT NOT NULL,
                 valor REAL NOT NULL,
                 tipo TEXT NOT NULL,
                 conta_bancaria_id INTEGER,
                 plano_contas_id INTEGER,
                 fornecedor_id INTEGER,
                 cliente_id INTEGER,
                 forma_pagamento_id INTEGER,
                 FOREIGN KEY (conta_bancaria_id) REFERENCES conta_bancaria(id),
                 FOREIGN KEY (plano_contas_id) REFERENCES plano_contas(id),
                 FOREIGN KEY (fornecedor_id) REFERENCES fornecedor(id),
                 FOREIGN KEY (cliente_id) REFERENCES cliente(id),
                 FOREIGN KEY (forma_pagamento_id) REFERENCES forma_pagamento(id))''')
    try:
        c.execute("ALTER TABLE lancamento ADD COLUMN status TEXT DEFAULT 'pendente'")
    except sqlite3.OperationalError:
        # Se o campo já existir, ignora o erro
        pass
    
    formas = [('Dinheiro',), ('Cartão de Crédito',), ('Boleto',), ('Pix',)]
    c.executemany("INSERT OR IGNORE INTO forma_pagamento (nome) VALUES (?)", formas)
    
    conn.commit()
    conn.close()

# Função para inicializar o banco ao rodar o app pela primeira vez
if __name__ == '__main__':
    init_db()