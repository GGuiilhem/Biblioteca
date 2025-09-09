from sqlalchemy import Column, Integer, String, Date, ForeignKey, Boolean, DateTime, Float, Text, Enum
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
from enum import Enum as PyEnum
from app.core.database import Base

class StatusLivro(str, PyEnum):
    DISPONIVEL = "disponível"
    EMPRESTADO = "emprestado"
    RESERVADO = "reservado"
    EM_MANUTENCAO = "em manutenção"

class StatusEmprestimo(str, PyEnum):
    ATIVO = "ativo"
    FINALIZADO = "finalizado"
    ATRASADO = "atrasado"
    DEVOLVIDO = "devolvido"

class TipoUsuario(str, PyEnum):
    ALUNO = "aluno"
    PROFESSOR = "professor"
    FUNCIONARIO = "funcionário"
    ADMIN = "administrador"

class Autor(Base):
    __tablename__ = "autores"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), index=True, nullable=False)
    nacionalidade = Column(String(50))
    data_nascimento = Column(Date)
    biografia = Column(Text, nullable=True)
    
    livros = relationship("Livro", back_populates="autor")

class Editora(Base):
    __tablename__ = "editoras"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    cidade = Column(String(50))
    pais = Column(String(50))
    
    livros = relationship("Livro", back_populates="editora")

class Categoria(Base):
    __tablename__ = "categorias"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(50), unique=True, nullable=False)
    descricao = Column(Text)
    
    livros = relationship("Livro", secondary="livro_categoria", back_populates="categorias")

class Livro(Base):
    __tablename__ = "livros"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String(200), index=True, nullable=False)
    subtitulo = Column(String(200), nullable=True)
    autor_id = Column(Integer, ForeignKey("autores.id"), nullable=False)
    editora_id = Column(Integer, ForeignKey("editoras.id"), nullable=True)
    isbn = Column(String(13), unique=True, index=True, nullable=False)
    edicao = Column(Integer, default=1)
    ano_publicacao = Column(Integer)
    num_paginas = Column(Integer)
    sinopse = Column(Text)
    idioma = Column(String(20), default="Português")
    status = Column(Enum(StatusLivro), default=StatusLivro.DISPONIVEL)
    capa_url = Column(String(255), nullable=True)
    data_cadastro = Column(DateTime, default=datetime.utcnow)
    
    autor = relationship("Autor", back_populates="livros")
    editora = relationship("Editora", back_populates="livros")
    categorias = relationship("Categoria", secondary="livro_categoria", back_populates="livros")
    emprestimos = relationship("Emprestimo", back_populates="livro")

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    cpf = Column(String(11), unique=True, index=True, nullable=False)
    matricula = Column(String(20), unique=True, index=True, nullable=False)
    tipo = Column(Enum(TipoUsuario), default=TipoUsuario.ALUNO)
    curso = Column(String(100), nullable=True)
    telefone = Column(String(20))
    endereco = Column(Text)
    data_nascimento = Column(Date)
    data_cadastro = Column(DateTime, default=datetime.utcnow)
    ativo = Column(Boolean, default=True)
    
    emprestimos = relationship("Emprestimo", back_populates="usuario")
    reservas = relationship("Reserva", back_populates="usuario")

class Emprestimo(Base):
    __tablename__ = "emprestimos"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    livro_id = Column(Integer, ForeignKey("livros.id"), nullable=False)
    data_emprestimo = Column(DateTime, default=datetime.utcnow)
    data_devolucao_prevista = Column(DateTime, default=lambda: datetime.utcnow() + timedelta(days=14))
    data_devolucao_real = Column(DateTime, nullable=True)
    status = Column(Enum(StatusEmprestimo), default=StatusEmprestimo.ATIVO)
    multa = Column(Float, default=0.0)
    observacoes = Column(Text, nullable=True)
    
    usuario = relationship("Usuario", back_populates="emprestimos")
    livro = relationship("Livro", back_populates="emprestimos")

class Reserva(Base):
    __tablename__ = "reservas"
    
    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    livro_id = Column(Integer, ForeignKey("livros.id"), nullable=False)
    data_reserva = Column(DateTime, default=datetime.utcnow)
    data_expiracao = Column(DateTime, default=lambda: datetime.utcnow() + timedelta(days=2))
    status = Column(String(20), default="pendente")  # pendente, concluída, cancelada, expirada
    
    usuario = relationship("Usuario", back_populates="reservas")
    livro = relationship("Livro")

# Tabela de associação para relacionamento muitos-para-muitos entre Livro e Categoria
class LivroCategoria(Base):
    __tablename__ = "livro_categoria"
    
    livro_id = Column(Integer, ForeignKey("livros.id"), primary_key=True)
    categoria_id = Column(Integer, ForeignKey("categorias.id"), primary_key=True)
