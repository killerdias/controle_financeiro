from database import get_db

# Conta Bancária
def add_conta(nome, saldo_inicial):
    conn = get_db()
    c = conn.cursor()
    c.execute("INSERT INTO conta_bancaria (nome, saldo_inicial) VALUES (?, ?)", (nome, saldo_inicial))
    conn.commit()

def get_contas():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM conta_bancaria")
    contas = c.fetchall()
    return contas

def update_conta(id, nome, saldo_inicial):
    conn = get_db()
    c = conn.cursor()
    c.execute("UPDATE conta_bancaria SET nome = ?, saldo_inicial = ? WHERE id = ?", (nome, saldo_inicial, id))
    conn.commit()

def delete_conta(id):
    conn = get_db()
    c = conn.cursor()
    c.execute("DELETE FROM conta_bancaria WHERE id = ?", (id,))
    conn.commit()

def get_saldo_conta(conta_id):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT saldo_inicial FROM conta_bancaria WHERE id = ?", (conta_id,))
    saldo_inicial = c.fetchone()['saldo_inicial']
    c.execute("""
        SELECT SUM(CASE WHEN tipo = 'receita' THEN valor ELSE -valor END) as total 
        FROM lancamento 
        WHERE conta_bancaria_id = ? AND status = 'pago'
    """, (conta_id,))
    total_lancamentos = c.fetchone()['total'] or 0
    return saldo_inicial + total_lancamentos

def baixar_lancamento(id):
    conn = get_db()
    c = conn.cursor()
    c.execute("UPDATE lancamento SET status = 'pago' WHERE id = ?", (id,))
    conn.commit()

# Centro de Custo
def add_centro_custo(nome):
    conn = get_db()
    c = conn.cursor()
    c.execute("INSERT INTO centro_custo (nome) VALUES (?)", (nome,))
    conn.commit()

def get_centros_custo():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM centro_custo")
    centros = c.fetchall()
    return centros

def update_centro_custo(id, nome):
    conn = get_db()
    c = conn.cursor()
    c.execute("UPDATE centro_custo SET nome = ? WHERE id = ?", (nome, id))
    conn.commit()

def delete_centro_custo(id):
    conn = get_db()
    c = conn.cursor()
    c.execute("DELETE FROM centro_custo WHERE id = ?", (id,))
    conn.commit()

# Plano de Contas
def add_plano(nome, categoria_pai=None, centro_custo_id=None):
    conn = get_db()
    c = conn.cursor()
    c.execute("INSERT INTO plano_contas (nome, categoria_pai, centro_custo_id) VALUES (?, ?, ?)", 
              (nome, categoria_pai, centro_custo_id))
    conn.commit()

def get_planos():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT pc.*, cc.nome AS centro_custo_nome FROM plano_contas pc LEFT JOIN centro_custo cc ON pc.centro_custo_id = cc.id")
    planos = c.fetchall()
    return planos

def update_plano(id, nome, categoria_pai=None, centro_custo_id=None):
    conn = get_db()
    c = conn.cursor()
    c.execute("UPDATE plano_contas SET nome = ?, categoria_pai = ?, centro_custo_id = ? WHERE id = ?", 
              (nome, categoria_pai, centro_custo_id, id))
    conn.commit()

def delete_plano(id):
    conn = get_db()
    c = conn.cursor()
    c.execute("DELETE FROM plano_contas WHERE id = ?", (id,))
    conn.commit()

# Fornecedor
def add_fornecedor(cnpj, nome_fantasia, razao_social):
    conn = get_db()
    c = conn.cursor()
    c.execute("INSERT INTO fornecedor (cnpj, nome_fantasia, razao_social) VALUES (?, ?, ?)", (cnpj, nome_fantasia, razao_social))
    conn.commit()

def get_fornecedores():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM fornecedor")
    fornecedores = c.fetchall()
    return fornecedores

def update_fornecedor(id, cnpj, nome_fantasia, razao_social):
    conn = get_db()
    c = conn.cursor()
    c.execute("UPDATE fornecedor SET cnpj = ?, nome_fantasia = ?, razao_social = ? WHERE id = ?", (cnpj, nome_fantasia, razao_social, id))
    conn.commit()

def delete_fornecedor(id):
    conn = get_db()
    c = conn.cursor()
    c.execute("DELETE FROM fornecedor WHERE id = ?", (id,))
    conn.commit()

# Cliente
def add_cliente(cpf_cnpj, nome):
    conn = get_db()
    c = conn.cursor()
    c.execute("INSERT INTO cliente (cpf_cnpj, nome) VALUES (?, ?)", (cpf_cnpj, nome))
    conn.commit()

def get_clientes():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM cliente")
    clientes = c.fetchall()
    return clientes

def update_cliente(id, cpf_cnpj, nome):
    conn = get_db()
    c = conn.cursor()
    c.execute("UPDATE cliente SET cpf_cnpj = ?, nome = ? WHERE id = ?", (cpf_cnpj, nome, id))
    conn.commit()

def delete_cliente(id):
    conn = get_db()
    c = conn.cursor()
    c.execute("DELETE FROM cliente WHERE id = ?", (id,))
    conn.commit()

# Forma de Pagamento
def get_formas_pagamento():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM forma_pagamento")
    formas = c.fetchall()
    return formas

def add_forma_pagamento(nome):
    conn = get_db()
    c = conn.cursor()
    c.execute("INSERT INTO forma_pagamento (nome) VALUES (?)", (nome,))
    conn.commit()

def update_forma_pagamento(id, nome):
    conn = get_db()
    c = conn.cursor()
    c.execute("UPDATE forma_pagamento SET nome = ? WHERE id = ?", (nome, id))
    conn.commit()

def delete_forma_pagamento(id):
    conn = get_db()
    c = conn.cursor()
    c.execute("DELETE FROM forma_pagamento WHERE id = ?", (id,))
    conn.commit()

# Lançamento
def add_lancamento(data, valor, tipo, conta_id, plano_id, fornecedor_id, cliente_id, forma_id, status='pendente'):
    conn = get_db()
    c = conn.cursor()
    c.execute("""
        INSERT INTO lancamento (data_lancamento, valor, tipo, conta_bancaria_id, plano_contas_id, fornecedor_id, cliente_id, forma_pagamento_id, status) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (data, valor, tipo, conta_id, plano_id, fornecedor_id, cliente_id, forma_id, status))
    conn.commit()

def get_lancamentos(data_inicio=None, data_fim=None):
    conn = get_db()  # Usar get_db() em vez de sqlite3.connect
    c = conn.cursor()
    query = """
        SELECT l.*, cb.nome as conta_nome, pc.nome as plano_nome, f.nome_fantasia as fornecedor_nome,
               cl.nome as cliente_nome, fp.nome as forma_nome
        FROM lancamento l
        LEFT JOIN conta_bancaria cb ON l.conta_bancaria_id = cb.id
        LEFT JOIN plano_contas pc ON l.plano_contas_id = pc.id
        LEFT JOIN fornecedor f ON l.fornecedor_id = f.id
        LEFT JOIN cliente cl ON l.cliente_id = cl.id
        LEFT JOIN forma_pagamento fp ON l.forma_pagamento_id = fp.id
        WHERE 1=1
    """
    params = []

    # Adicionar filtros de data se fornecidos
    if data_inicio:
        query += " AND l.data_lancamento >= ?"
        params.append(data_inicio)
    if data_fim:
        query += " AND l.data_lancamento <= ?"
        params.append(data_fim)

    c.execute(query, params)
    lancamentos = c.fetchall()
    return [dict(lancamento) for lancamento in lancamentos]

def delete_lancamento(id):
    conn = get_db()
    c = conn.cursor()
    c.execute("DELETE FROM lancamento WHERE id = ?", (id,))
    conn.commit()