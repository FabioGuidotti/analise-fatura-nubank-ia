from sqlalchemy import Column, Integer, String
from base import Base

class Usuario(Base):
    __tablename__ = 'usuarios'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    senha = Column(String, nullable=False)

class Categoria(Base):
    __tablename__ = 'categorias'

    id = Column(Integer, primary_key=True)
    nome = Column(String, unique=True, nullable=False)

class Transacao(Base):
    __tablename__ = 'transacoes'

    id = Column(Integer, primary_key=True)
    data = Column(Date)
    descricao = Column(String)
    valor = Column(Float)
    categoria = Column(String)
    arquivo_origem = Column(String)
    usuario_id = Column(Integer, ForeignKey('usuarios.id'), nullable=False)