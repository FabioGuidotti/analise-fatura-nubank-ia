import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String, Float, Date, ForeignKey, text
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import IntegrityError
import pandas as pd
from datetime import datetime

# Definição de Base
Base = declarative_base()

# Definição dos modelos
class Usuario(Base):
    __tablename__ = 'usuarios'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    senha = Column(String, nullable=False)

class Categoria(Base):
    __tablename__ = 'categorias'
    id = Column(Integer, primary_key=True)
    nome = Column(String, nullable=False)
    usuario_id = Column(Integer, ForeignKey('usuarios.id'), nullable=False)

class Transacao(Base):
    __tablename__ = 'transacoes'
    id = Column(Integer, primary_key=True)
    data = Column(Date)
    descricao = Column(String)
    valor = Column(Float)
    categoria = Column(String)
    arquivo_origem = Column(String)
    usuario_id = Column(Integer, ForeignKey('usuarios.id'), nullable=False)

# Carrega as variáveis de ambiente
load_dotenv()

# Configuração do banco de dados
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

# String de conexão do PostgreSQL
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Cria o engine do SQLAlchemy
engine = create_engine(DATABASE_URL)

# Cria uma sessão
Session = sessionmaker(bind=engine)

# Funções para interagir com o banco de dados
def salvar_dados(dados, arquivo_origem, usuario_id):
    session = Session()
    try:
        print("Iniciando importação dos dados")
        for index, row in dados.iterrows():
            try:
                if isinstance(row['data'], pd.Timestamp):
                    data = row['data'].date()
                else:
                    data = datetime.strptime(str(row['data']), '%Y-%m-%d').date()

                transacao = Transacao(
                    data=data,
                    descricao=str(row.get('descricao', '')),
                    valor=float(row.get('valor', 0)),
                    categoria=str(row.get('categoria', 'Outros')),
                    arquivo_origem=arquivo_origem,
                    usuario_id=usuario_id
                )
                session.add(transacao)

            except Exception as row_error:
                print(f"Erro ao processar linha {index}: {str(row_error)}")
                print(f"Conteúdo da linha: {row.to_dict()}")

        session.commit()
        print(f"Importação concluída. {len(dados)} transações salvas.")
    except Exception as e:
        session.rollback()
        print(f"Erro ao salvar dados: {str(e)}")
        print("Detalhes do erro:", e)
        raise
    finally:
        session.close()
        print("Sessão fechada")

def carregar_dados(usuario_id):
    session = Session()
    transacoes = session.query(Transacao).filter_by(usuario_id=usuario_id).all()
    session.close()
    return pd.DataFrame([
        {
            'id': t.id,
            'Data': t.data,
            'Descrição': t.descricao,
            'Valor': t.valor,
            'Categoria': t.categoria,
            'Arquivo de Origem': t.arquivo_origem
        } for t in transacoes
    ])

def excluir_transacao(id_transacao, usuario_id):
    session = Session()
    transacao = session.query(Transacao).filter_by(id=id_transacao, usuario_id=usuario_id).first()
    if transacao:
        session.delete(transacao)
        session.commit()
    session.close()

def obter_datas_faturas(usuario_id):
    session = Session()
    datas = session.query(Transacao.data).filter_by(usuario_id=usuario_id).distinct().order_by(Transacao.data.desc()).all()
    session.close()
    return [data[0] for data in datas]

def excluir_transacoes_por_data(data, usuario_id):
    session = Session()
    session.query(Transacao).filter(Transacao.data == data, Transacao.usuario_id == usuario_id).delete()
    session.commit()
    session.close()

def obter_arquivos_origem(usuario_id):
    session = Session()
    arquivos = session.query(Transacao.arquivo_origem).filter_by(usuario_id=usuario_id).distinct().all()
    session.close()
    return [arquivo[0] for arquivo in arquivos]

def excluir_transacoes_por_arquivo(arquivo, usuario_id):
    session = Session()
    session.query(Transacao).filter(Transacao.arquivo_origem == arquivo, Transacao.usuario_id == usuario_id).delete()
    session.commit()
    session.close()

def garantir_categoria_outros(usuario_id):
    session = Session()
    outros = session.query(Categoria).filter_by(nome='Outros', usuario_id=usuario_id).first()
    if not outros:
        outros = Categoria(nome='Outros', usuario_id=usuario_id)
        session.add(outros)
        session.commit()
    session.close()

def testar_conexao():
    try:
        session = Session()
        session.execute(text("SELECT 1"))
        print("Conexão com o banco de dados estabelecida com sucesso!")
        session.close()
        return True
    except Exception as e:
        print(f"Erro ao conectar ao banco de dados: {str(e)}")
        return False

def recriar_tabela_transacoes():
    Base.metadata.drop_all(engine, tables=[Transacao.__table__])
    Base.metadata.create_all(engine, tables=[Transacao.__table__])
    print("Tabela 'transacoes' recriada com sucesso.")

def obter_categorias(usuario_id):
    session = Session()
    categorias = session.query(Categoria.nome).filter_by(usuario_id=usuario_id).distinct().all()
    session.close()
    return [categoria[0] for categoria in categorias]

def adicionar_categoria(nome_categoria, usuario_id):
    session = Session()
    try:
        nova_categoria = Categoria(nome=nome_categoria, usuario_id=usuario_id)
        session.add(nova_categoria)
        session.commit()
        return True
    except IntegrityError:
        session.rollback()
        print(f"A categoria '{nome_categoria}' já existe para este usuário.")
        return False
    finally:
        session.close()

def excluir_categoria(nome_categoria, usuario_id):
    session = Session()
    categoria = session.query(Categoria).filter_by(nome=nome_categoria, usuario_id=usuario_id).first()
    if categoria:
        session.delete(categoria)
        session.commit()
    session.close()

def atualizar_categoria(nome_antigo, nome_novo, usuario_id):
    session = Session()
    try:
        categoria = session.query(Categoria).filter_by(nome=nome_antigo, usuario_id=usuario_id).first()
        if categoria:
            categoria_existente = session.query(Categoria).filter_by(nome=nome_novo).first()
            if categoria_existente and categoria_existente.id != categoria.id:
                print(f"A categoria '{nome_novo}' já existe. Não é possível atualizar.")
                return False
            
            categoria.nome = nome_novo
            session.commit()
            print(f"Categoria atualizada de '{nome_antigo}' para '{nome_novo}'")
            return True
        else:
            print(f"Categoria '{nome_antigo}' não encontrada")
            return False
    except IntegrityError:
        session.rollback()
        print(f"Erro de integridade ao atualizar a categoria. A categoria '{nome_novo}' já existe.")
        return False
    except Exception as e:
        session.rollback()
        print(f"Erro ao atualizar categoria: {str(e)}")
        return False
    finally:
        session.close()

def limpar_todos_dados(usuario_id):
    session = Session()
    try:
        session.query(Transacao).filter_by(usuario_id=usuario_id).delete()
        session.commit()
        print("Todos os dados foram removidos do banco de dados!")
        return True
    except Exception as e:
        session.rollback()
        print(f"Erro ao limpar dados: {str(e)}")
        return False
    finally:
        session.close()

# Inicialização
def inicializar_banco():
    Base.metadata.create_all(engine)
    # Remova a chamada para garantir_categoria_outros() aqui, 
    # pois agora ela precisa do usuario_id

# Substitua a chamada direta por esta função
inicializar_banco()

def criar_usuario(nome, email, senha):
    session = Session()
    try:
        novo_usuario = Usuario(name=nome, senha=senha)
        session.add(novo_usuario)
        session.commit()
        return novo_usuario.id
    except IntegrityError:
        session.rollback()
        print("Usuário com este nome já existe")
        return None
    finally:
        session.close()

def autenticar_usuario(nome, senha):
    session = Session()
    try:
        usuario = session.query(Usuario).filter_by(name=nome).first()
        return usuario.id if usuario and usuario.senha == senha else None
    finally:
        session.close()