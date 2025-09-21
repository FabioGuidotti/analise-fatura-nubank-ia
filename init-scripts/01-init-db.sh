#!/bin/bash
set -e

echo "Iniciando configuração do banco de dados..."

# Aguarda o PostgreSQL estar pronto
until pg_isready -h localhost -p 5432 -U $POSTGRES_USER; do
  echo "Aguardando PostgreSQL estar pronto..."
  sleep 2
done

echo "PostgreSQL está pronto. Executando migrações do Alembic..."

# Executa as migrações do Alembic
cd /app
alembic upgrade head

echo "Migrações executadas com sucesso!"
