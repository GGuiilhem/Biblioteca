#!/usr/bin/env python3
"""
Script para inicializar o banco de dados da Biblioteca IMPACTA
Cria as tabelas e popula com dados iniciais para desenvolvimento

Observação: passe --force para remover o arquivo `biblioteca.db` existente
e recriar o banco do zero (útil quando o modelo foi alterado).
"""

import argparse
from pathlib import Path

from app.core.database import engine, SessionLocal, Base
from app.models.models import (
    Autor, Editora, Categoria, Livro, Usuario, UsuarioAuth,
    StatusLivro, TipoUsuario, LivroCategoria
)
from app.core.auth import get_password_hash
from datetime import datetime, date
import sys

def create_tables():
    """Cria todas as tabelas no banco de dados"""
    print("Criando tabelas no banco de dados...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tabelas criadas com sucesso!")

def populate_initial_data():
    """Popula o banco com dados iniciais para desenvolvimento"""
    db = SessionLocal()
    
    try:
        print("Inserindo dados iniciais...")
        
        # Verificar se já existem dados
        if db.query(Autor).first():
            print("⚠️  Dados já existem no banco. Pulando inserção inicial.")
            return
        
        # Criar editoras
        editoras = [
            Editora(nome="Companhia das Letras", cidade="São Paulo", pais="Brasil"),
            Editora(nome="Record", cidade="Rio de Janeiro", pais="Brasil"),
            Editora(nome="Penguin Books", cidade="London", pais="Reino Unido"),
            Editora(nome="Saraiva", cidade="São Paulo", pais="Brasil"),
        ]
        
        for editora in editoras:
            db.add(editora)
        
        # Criar categorias
        categorias = [
            Categoria(nome="Ficção", descricao="Livros de ficção em geral"),
            Categoria(nome="Romance", descricao="Livros de romance"),
            Categoria(nome="Tecnologia", descricao="Livros sobre tecnologia e programação"),
            Categoria(nome="Ciências", descricao="Livros científicos"),
            Categoria(nome="História", descricao="Livros de história"),
            Categoria(nome="Biografia", descricao="Biografias e autobiografias"),
        ]
        
        for categoria in categorias:
            db.add(categoria)
        
        # Criar autores
        autores = [
            Autor(
                nome="Machado de Assis",
                nacionalidade="Brasileira",
                data_nascimento=date(1839, 6, 21),
                biografia="Joaquim Maria Machado de Assis foi um escritor brasileiro, considerado o maior nome da literatura brasileira."
            ),
            Autor(
                nome="Clarice Lispector",
                nacionalidade="Brasileira",
                data_nascimento=date(1920, 12, 10),
                biografia="Clarice Lispector foi uma escritora e jornalista brasileira nascida na Ucrânia."
            ),
            Autor(
                nome="Robert C. Martin",
                nacionalidade="Americana",
                data_nascimento=date(1952, 12, 5),
                biografia="Robert Cecil Martin, conhecido como Uncle Bob, é um engenheiro de software americano e autor."
            ),
            Autor(
                nome="Eric Evans",
                nacionalidade="Americana",
                biografia="Eric Evans é um consultor de software e autor do livro Domain-Driven Design."
            ),
        ]
        
        for autor in autores:
            db.add(autor)
        
        db.commit()  # Commit para obter os IDs
        
        # Criar livros
        livros = [
            Livro(
                titulo="Dom Casmurro",
                autor_id=1,  # Machado de Assis
                editora_id=1,  # Companhia das Letras
                isbn="9788535902777",
                ano_publicacao=1899,
                num_paginas=256,
                sinopse="Romance narrado em primeira pessoa por Bento Santiago.",
                status=StatusLivro.DISPONIVEL
            ),
            Livro(
                titulo="A Hora da Estrela",
                autor_id=2,  # Clarice Lispector
                editora_id=2,  # Record
                isbn="9788501061492",
                ano_publicacao=1977,
                num_paginas=87,
                sinopse="A história de Macabéa, uma jovem nordestina no Rio de Janeiro.",
                status=StatusLivro.DISPONIVEL
            ),
            Livro(
                titulo="Clean Code",
                subtitulo="A Handbook of Agile Software Craftsmanship",
                autor_id=3,  # Robert C. Martin
                editora_id=3,  # Penguin Books
                isbn="9780132350884",
                ano_publicacao=2008,
                num_paginas=464,
                sinopse="Um guia para escrever código limpo e maintível.",
                idioma="Inglês",
                status=StatusLivro.DISPONIVEL
            ),
            Livro(
                titulo="Domain-Driven Design",
                subtitulo="Tackling Complexity in the Heart of Software",
                autor_id=4,  # Eric Evans
                editora_id=3,  # Penguin Books
                isbn="9780321125217",
                ano_publicacao=2003,
                num_paginas=560,
                sinopse="Abordagem para desenvolvimento de software complexo.",
                idioma="Inglês",
                status=StatusLivro.DISPONIVEL
            ),
        ]
        
        for livro in livros:
            db.add(livro)
        
        # Criar usuários de exemplo
        usuarios = [
            Usuario(
                nome="João Silva",
                email="joao.silva@impacta.edu.br",
                cpf="12345678901",
                matricula="2024001",
                tipo=TipoUsuario.ALUNO,
                curso="Análise e Desenvolvimento de Sistemas",
                telefone="(11) 99999-0001"
            ),
            Usuario(
                nome="Maria Santos",
                email="maria.santos@impacta.edu.br",
                cpf="12345678902",
                matricula="2024002",
                tipo=TipoUsuario.ALUNO,
                curso="Ciência da Computação",
                telefone="(11) 99999-0002"
            ),
            Usuario(
                nome="Prof. Carlos Oliveira",
                email="carlos.oliveira@impacta.edu.br",
                cpf="12345678903",
                matricula="PROF001",
                tipo=TipoUsuario.PROFESSOR,
                telefone="(11) 99999-0003"
            ),
        ]
        
        for usuario in usuarios:
            db.add(usuario)
        
        # Criar usuário administrador para autenticação
        admin_user = UsuarioAuth(
            nome="Administrador",
            email="admin@impacta.edu.br",
            matricula="ADMIN001",
            senha_hash=get_password_hash("admin123"),
            is_admin=True
        )
        db.add(admin_user)
        
        # Criar usuário de teste
        test_user = UsuarioAuth(
            nome="Usuário Teste",
            email="teste@impacta.edu.br",
            matricula="USER001",
            senha_hash=get_password_hash("123456"),
            is_admin=False
        )
        db.add(test_user)
        
        db.commit()
        
        # Associar categorias aos livros
        associacoes = [
            LivroCategoria(livro_id=1, categoria_id=1),  # Dom Casmurro - Ficção
            LivroCategoria(livro_id=1, categoria_id=2),  # Dom Casmurro - Romance
            LivroCategoria(livro_id=2, categoria_id=1),  # A Hora da Estrela - Ficção
            LivroCategoria(livro_id=3, categoria_id=3),  # Clean Code - Tecnologia
            LivroCategoria(livro_id=4, categoria_id=3),  # Domain-Driven Design - Tecnologia
        ]
        
        for associacao in associacoes:
            db.add(associacao)
        
        db.commit()
        print("✅ Dados iniciais inseridos com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro ao inserir dados iniciais: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description="Inicializa o banco de dados da Biblioteca IMPACTA")
    parser.add_argument("--force", action="store_true", help="Remover arquivo biblioteca.db existente antes de criar")
    args = parser.parse_args()

    print("🚀 Inicializando banco de dados da Biblioteca IMPACTA")
    print("=" * 50)

    try:
        # Se solicitado, remove o arquivo do banco de dados para recriar do zero
        if args.force:
            db_path = Path(__file__).resolve().parent / "biblioteca.db"
            if db_path.exists():
                print(f"Removendo banco existente: {db_path}")
                db_path.unlink()

        create_tables()
        populate_initial_data()
        print("=" * 50)
        print("✅ Banco de dados inicializado com sucesso!")
        print("📚 Você pode agora executar a aplicação com: python main.py")

    except Exception as e:
        print(f"❌ Erro durante a inicialização: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
