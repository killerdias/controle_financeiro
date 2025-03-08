from flask import Flask, render_template, request, redirect, url_for, Response, flash
from database import init_db, close_db
from models import (add_conta, get_contas, update_conta, delete_conta, get_saldo_conta,
                   add_plano, get_planos, update_plano, delete_plano,
                   add_fornecedor, get_fornecedores, update_fornecedor, delete_fornecedor,
                   add_cliente, get_clientes, update_cliente, delete_cliente,
                   get_formas_pagamento, add_lancamento, get_lancamentos, delete_lancamento,
                   add_forma_pagamento, update_forma_pagamento, delete_forma_pagamento,
                   add_centro_custo, get_centros_custo, update_centro_custo, delete_centro_custo, baixar_lancamento)
from datetime import date, datetime


app = Flask(__name__)
app.jinja_env.auto_reload = True
app.teardown_appcontext(close_db)
app.secret_key = 'soeusei'  # Defina uma chave secreta única e segura

# Filtro personalizado para formatar datas
@app.template_filter('format_date')
def format_date(value):
    if isinstance(value, str):
        date_obj = datetime.strptime(value, '%Y-%m-%d')
        return date_obj.strftime('%d/%m/%Y')
    return value

# Filtro personalizado para formatar moeda (BRL)
@app.template_filter('format_currency')
def format_currency(value):
    if value is None or not isinstance(value, (int, float)):
        return 'R$ 0,00'
    # Formatar o valor com duas casas decimais e separadores brasileiros
    return f'R$ {value:,.2f}'.replace('.', '#').replace(',', '.').replace('#', ',')

init_db()

@app.route('/', methods=['GET'])
def home():
    contas = get_contas()
    saldos = {conta['id']: get_saldo_conta(conta['id']) for conta in contas}

    # Obter parâmetros de filtro da requisição GET
    filtro_data_inicio = request.args.get('data_inicio')
    filtro_data_fim = request.args.get('data_fim')

    # Obter todos os lançamentos
    lancamentos = get_lancamentos(filtro_data_inicio, filtro_data_fim)

    # Separar em pagos e a vencer (baseado no status)
    lancamentos_pagos = [l for l in lancamentos if l['status'] == 'pago']
    lancamentos_a_vencer = [l for l in lancamentos if l['status'] == 'pendente']

    return render_template('home.html', contas=contas, saldos=saldos, lancamentos_pagos=lancamentos_pagos,
                          lancamentos_a_vencer=lancamentos_a_vencer, filtro_data_inicio=filtro_data_inicio,
                          filtro_data_fim=filtro_data_fim)

@app.route('/relatorio', methods=['GET', 'POST'])
def relatorio():
    if request.method == 'POST':
        data_inicio = request.form.get('data_inicio')
        data_fim = request.form.get('data_fim')
        
        lancamentos = get_lancamentos(data_inicio=data_inicio, data_fim=data_fim)
        lancamentos = [{'id': l['id'], 'data_lancamento': l['data_lancamento'], 'valor': round(l['valor'], 2),
                        'tipo': l['tipo'], 'conta_nome': l['conta_nome'], 'plano_nome': l['plano_nome'],
                        'fornecedor_nome': l['fornecedor_nome'], 'cliente_nome': l['cliente_nome'],
                        'forma_nome': l['forma_nome']} for l in lancamentos]
        
        despesas = [l for l in lancamentos if l['tipo'] == 'despesa']
        receitas = [l for l in lancamentos if l['tipo'] == 'receita']
        
        total_despesas = sum(d['valor'] for d in despesas)
        total_receitas = sum(r['valor'] for r in receitas)
        
        relatorio_texto = f"📊 *Relatório Financeiro*\n"
        relatorio_texto += f"Período: {data_inicio or 'Sem início'} até {data_fim or 'Sem fim'}\n\n"
        
        relatorio_texto += "💸 *Despesas Pagas*\n"
        if despesas:
            for despesa in despesas:
                relatorio_texto += f"- {despesa['data_lancamento']} | R$ {despesa['valor']} | {despesa['plano_nome']} | {despesa['fornecedor_nome'] or '-'}\n"
        else:
            relatorio_texto += "Nenhuma despesa encontrada.\n"
        relatorio_texto += f"Total de Despesas: R$ {total_despesas:.2f}\n\n"
        
        relatorio_texto += "💰 *Recebimentos*\n"
        if receitas:
            for receita in receitas:
                relatorio_texto += f"- {receita['data_lancamento']} | R$ {receita['valor']} | {receita['plano_nome']} | {receita['cliente_nome'] or '-'}\n"
        else:
            relatorio_texto += "Nenhum recebimento encontrado.\n"
        relatorio_texto += f"Total de Recebimentos: R$ {total_receitas:.2f}\n\n"
        
        relatorio_texto += f"📈 *Saldo do Período*: R$ {(total_receitas - total_despesas):.2f}\n"
        
        return Response(relatorio_texto, mimetype='text/plain')
    return render_template('relatorio.html')  # Criaremos esse template abaixo

@app.route('/contas', methods=['GET', 'POST'])
def contas():
    if request.method == 'POST':
        if 'delete' in request.form:
            delete_conta(request.form['delete'])
        elif 'edit' in request.form:
            update_conta(request.form['id'], request.form['nome'], float(request.form['saldo_inicial']))
        else:
            add_conta(request.form['nome'], float(request.form['saldo_inicial']))
        return redirect(url_for('contas'))
    contas = get_contas()
    contas = [{'id': c['id'], 'nome': c['nome'], 'saldo_inicial': round(c['saldo_inicial'], 2)} for c in contas]
    return render_template('contas.html', contas=contas)

@app.route('/planos', methods=['GET', 'POST'])
def planos():
    if request.method == 'POST':
        if 'delete' in request.form:
            delete_plano(request.form['delete'])
        elif 'edit' in request.form:
            update_plano(request.form['id'], request.form['nome'], 
                        request.form['categoria_pai'] or None, request.form['centro_custo'] or None)
        else:
            add_plano(request.form['nome'], None, request.form['centro_custo'] or None)
        return redirect(url_for('planos'))
    planos = get_planos()
    centros_custo = get_centros_custo()
    return render_template('planos.html', planos=planos, centros_custo=centros_custo)

@app.route('/centros_custo', methods=['GET', 'POST'])
def centros_custo():
    if request.method == 'POST':
        if 'delete' in request.form:
            delete_centro_custo(request.form['delete'])
        elif 'edit' in request.form:
            update_centro_custo(request.form['id'], request.form['nome'])
        else:
            add_centro_custo(request.form['nome'])
        return redirect(url_for('centros_custo'))
    centros_custo = get_centros_custo()
    return render_template('centros_custo.html', centros_custo=centros_custo)

@app.route('/fornecedores', methods=['GET', 'POST'])
def fornecedores():
    if request.method == 'POST':
        if 'delete' in request.form:
            delete_fornecedor(request.form['delete'])
        elif 'edit' in request.form:
            update_fornecedor(request.form['id'], request.form['cnpj'], request.form['nome_fantasia'], 
                            request.form['razao_social'])
        else:
            add_fornecedor(request.form['cnpj'], request.form['nome_fantasia'], request.form['razao_social'])
        return redirect(url_for('fornecedores'))
    fornecedores = get_fornecedores()
    return render_template('fornecedores.html', fornecedores=fornecedores)

@app.route('/clientes', methods=['GET', 'POST'])
def clientes():
    if request.method == 'POST':
        if 'delete' in request.form:
            delete_cliente(request.form['delete'])
        elif 'edit' in request.form:
            update_cliente(request.form['id'], request.form['cpf_cnpj'], request.form['nome'])
        else:
            add_cliente(request.form['cpf_cnpj'], request.form['nome'])
        return redirect(url_for('clientes'))
    clientes = get_clientes()
    return render_template('clientes.html', clientes=clientes)

@app.route('/transferencia', methods=['GET', 'POST'])
def transferencia():
    contas = get_contas()
    planos = get_planos()
    formas = get_formas_pagamento()

    if request.method == 'POST':
        try:
            conta_origem_id = request.form['conta_origem']
            conta_destino_id = request.form['conta_destino']
            valor = float(request.form['valor'])
            data = request.form['data']
            plano_id = request.form['plano']
            forma_id = request.form['forma']

            # Validações
            if valor <= 0:
                flash('O valor deve ser maior que zero!', 'danger')
                return redirect(url_for('transferencia'))
            data_lancamento = date.fromisoformat(data)
            hoje = date.today()
            if data_lancamento < hoje:
                flash('A data da transferência não pode ser anterior ao dia atual!', 'danger')
                return redirect(url_for('transferencia'))
            if conta_origem_id == conta_destino_id:
                flash('A conta de origem e destino não podem ser as mesmas!', 'danger')
                return redirect(url_for('transferencia'))

            # Adicionar os dois lançamentos (despesa e receita)
            add_lancamento(data, valor, 'despesa', conta_origem_id, plano_id, None, None, forma_id)
            add_lancamento(data, valor, 'receita', conta_destino_id, plano_id, None, None, forma_id)
            flash('Transferência realizada com sucesso!', 'success')
        except ValueError as e:
            flash('Erro ao realizar a transferência: verifique os dados inseridos!', 'danger')
        except Exception as e:
            flash(f'Erro inesperado: {str(e)}', 'danger')
        return redirect(url_for('transferencia'))

    # Obter todas as transferências (simulando com base nos lançamentos)
    lancamentos = get_lancamentos()
    transferencias = []
    for i in range(0, len(lancamentos), 2):
        if i + 1 < len(lancamentos):
            lanc1 = lancamentos[i]
            lanc2 = lancamentos[i + 1]
            if (lanc1['valor'] == lanc2['valor'] and lanc1['data_lancamento'] == lanc2['data_lancamento'] and
                lanc1['tipo'] == 'despesa' and lanc2['tipo'] == 'receita'):
                transferencias.append({
                    'data': lanc1['data_lancamento'],
                    'valor': lanc1['valor'],
                    'conta_origem_nome': lanc1['conta_nome'],
                    'conta_destino_nome': lanc2['conta_nome'],
                    'plano_nome': lanc1['plano_nome'],
                    'forma_nome': lanc1['forma_nome']
                })

    return render_template('transferencia.html', contas=contas, planos=planos, formas=formas, transferencias=transferencias)

@app.route('/formas_pagamento', methods=['GET', 'POST'])
def formas_pagamento():
    if request.method == 'POST':
        if 'delete' in request.form:
            delete_forma_pagamento(request.form['delete'])
        elif 'edit' in request.form:
            update_forma_pagamento(request.form['id'], request.form['nome'])
        else:
            add_forma_pagamento(request.form['nome'])
        return redirect(url_for('formas_pagamento'))
    
    formas = get_formas_pagamento()
    return render_template('formas_pagamento.html', formas=formas)

@app.route('/lancamentos', methods=['GET', 'POST'])
def lancamentos():
    if request.method == 'POST':
        if 'delete' in request.form:
            delete_lancamento(request.form['delete'])
        elif 'baixar' in request.form:  # Nova ação para baixar
            baixar_lancamento(request.form['baixar'])
        elif 'filtro' in request.form:
            filtro_data = request.form.get('filtro_data')
            filtro_tipo = request.form.get('filtro_tipo')
            return redirect(url_for('lancamentos', filtro_data=filtro_data, filtro_tipo=filtro_tipo))
        else:
            data = request.form['data']
            valor = float(request.form['valor'])
            tipo = request.form['tipo']
            conta_id = request.form['conta']
            plano_id = request.form['plano']
            fornecedor_id = request.form['fornecedor'] or None
            cliente_id = request.form['cliente'] or None
            forma_id = request.form['forma']
            add_lancamento(data, valor, tipo, conta_id, plano_id, fornecedor_id, cliente_id, forma_id)
        return redirect(url_for('lancamentos'))
    
    filtro_data = request.args.get('filtro_data')
    filtro_tipo = request.args.get('filtro_tipo')
    contas = get_contas()
    planos = get_planos()
    fornecedores = get_fornecedores()
    clientes = get_clientes()
    formas = get_formas_pagamento()
    lancamentos = get_lancamentos(filtro_data, filtro_tipo)
    lancamentos = [{'id': l['id'], 'data_lancamento': l['data_lancamento'], 'valor': round(l['valor'], 2),
                    'tipo': l['tipo'], 'conta_nome': l['conta_nome'], 'plano_nome': l['plano_nome'],
                    'fornecedor_nome': l['fornecedor_nome'], 'cliente_nome': l['cliente_nome'],
                    'forma_nome': l['forma_nome'], 'status': l['status']} for l in lancamentos]
    return render_template('lancamentos.html', contas=contas, planos=planos, fornecedores=fornecedores, 
                          clientes=clientes, formas=formas, lancamentos=lancamentos, 
                          filtro_data=filtro_data, filtro_tipo=filtro_tipo)

if __name__ == '__main__':
    app.run(debug=True)