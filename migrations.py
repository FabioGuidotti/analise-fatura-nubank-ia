import sqlite3
import os

def run_migrations():
    conn = sqlite3.connect('fatura_nubank.db')
    cursor = conn.cursor()

    # Cria a tabela de controle de migrações se não existir
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS migrations (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Lista de migrações
    migrations = [
        ('001_create_transacoes_table', create_transacoes_table),
        ('002_add_categoria_column', add_categoria_column),
        # Adicione novas migrações aqui
    ]

    # Executa as migrações que ainda não foram aplicadas
    for migration_name, migration_func in migrations:
        cursor.execute('SELECT id FROM migrations WHERE name = ?', (migration_name,))
        if cursor.fetchone() is None:
            print(f"Applying migration: {migration_name}")
            migration_func(cursor)
            cursor.execute('INSERT INTO migrations (name) VALUES (?)', (migration_name,))
            conn.commit()

    conn.close()

def create_transacoes_table(cursor):
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS transacoes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        data DATE,
        descricao TEXT,
        valor REAL,
        categoria TEXT
    )
    ''')

def add_categoria_column(cursor):
    cursor.execute('PRAGMA table_info(transacoes)')
    columns = [column[1] for column in cursor.fetchall()]
    if 'categoria' not in columns:
        cursor.execute('ALTER TABLE transacoes ADD COLUMN categoria TEXT')

# Adicione novas funções de migração aqui

if __name__ == "__main__":
    run_migrations()