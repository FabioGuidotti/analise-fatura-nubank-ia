import sqlite3
import pandas as pd
from alembic import command
from alembic.config import Config

def run_migrations():
    alembic_cfg = Config("alembic.ini")
    try:
        command.upgrade(alembic_cfg, "head")
    except Exception as e:
        print(f"Erro durante a migração: {str(e)}")

def salvar_dados(dados, nome_arquivo):
    conn = sqlite3.connect('fatura_nubank.db')
    
    # Renomear as colunas para corresponder às colunas do banco de dados
    dados = dados.rename(columns={
        'Data': 'data',
        'Descrição': 'descricao',
        'Valor': 'valor',
        'Categoria': 'categoria'
    })
    
    dados['arquivo_origem'] = nome_arquivo
    dados.to_sql('transacoes', conn, if_exists='append', index=False)
    conn.close()

def carregar_dados():
    conn = sqlite3.connect('fatura_nubank.db')
    df = pd.read_sql_query("SELECT * FROM transacoes", conn)
    conn.close()
    
    # Renomear as colunas para manter consistência na interface do usuário
    df = df.rename(columns={
        'data': 'Data',
        'descricao': 'Descrição',
        'valor': 'Valor',
        'categoria': 'Categoria',
        'arquivo_origem': 'Arquivo de Origem'
    })
    
    # Converter a coluna 'Data' para datetime
    df['Data'] = pd.to_datetime(df['Data'])
    
    return df

def excluir_transacao(id_transacao):
    conn = sqlite3.connect('fatura_nubank.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM transacoes WHERE id = ?", (id_transacao,))
    conn.commit()
    conn.close()

def obter_datas_faturas():
    conn = sqlite3.connect('fatura_nubank.db')
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT strftime('%Y-%m', data) as mes_ano FROM transacoes ORDER BY mes_ano DESC")
    datas = [row[0] for row in cursor.fetchall()]
    conn.close()
    return datas

def excluir_transacoes_por_data(mes_ano):
    conn = sqlite3.connect('fatura_nubank.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM transacoes WHERE strftime('%Y-%m', data) = ?", (mes_ano,))
    conn.commit()
    conn.close()

def obter_arquivos_origem():
    conn = sqlite3.connect('fatura_nubank.db')
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT arquivo_origem FROM transacoes ORDER BY arquivo_origem")
    arquivos = [row[0] for row in cursor.fetchall()]
    conn.close()
    return arquivos

def excluir_transacoes_por_arquivo(arquivo_origem):
    conn = sqlite3.connect('fatura_nubank.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM transacoes WHERE arquivo_origem = ?", (arquivo_origem,))
    conn.commit()
    conn.close()

def obter_categorias():
    conn = sqlite3.connect('fatura_nubank.db')
    cursor = conn.cursor()
    cursor.execute("SELECT nome FROM categorias ORDER BY nome")
    categorias = [row[0] for row in cursor.fetchall()]
    conn.close()
    return categorias

def adicionar_categoria(nova_categoria):
    conn = sqlite3.connect('fatura_nubank.db')
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO categorias (nome) VALUES (?)", (nova_categoria,))
        conn.commit()
    except sqlite3.IntegrityError:
        pass
    finally:
        conn.close()

def excluir_categoria(categoria):
    conn = sqlite3.connect('fatura_nubank.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM categorias WHERE nome = ?", (categoria,))
    conn.commit()
    conn.close()

def atualizar_categoria(antiga_categoria, nova_categoria):
    conn = sqlite3.connect('fatura_nubank.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE transacoes SET categoria = ? WHERE categoria = ?", (nova_categoria, antiga_categoria))
    cursor.execute("UPDATE categorias SET nome = ? WHERE nome = ?", (nova_categoria, antiga_categoria))
    conn.commit()
    conn.close()