from fastapi import APIRouter, Request, Form, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional

from app.core.database import get_db
from app.models import models
from app.schemas import book, author, user, emprestimo

router = APIRouter()

# ==================== ROTAS PARA LIVROS ====================

@router.post("/livros/")
async def create_livro(
    titulo: str = Form(...),
    subtitulo: Optional[str] = Form(None),
    autor_id: int = Form(...),
    editora_id: Optional[int] = Form(None),
    isbn: str = Form(...),
    edicao: Optional[int] = Form(1),
    ano_publicacao: Optional[int] = Form(None),
    num_paginas: Optional[int] = Form(None),
    sinopse: Optional[str] = Form(None),
    genero: Optional[str] = Form(None),
    idioma: Optional[str] = Form("Português"),
    db: Session = Depends(get_db)
):
    try:
        # Verificar se o autor existe
        autor = db.query(models.Autor).filter(models.Autor.id == autor_id).first()
        if not autor:
            raise HTTPException(status_code=404, detail="Autor não encontrado")
        
        # Verificar se a editora existe (se fornecida)
        if editora_id:
            editora = db.query(models.Editora).filter(models.Editora.id == editora_id).first()
            if not editora:
                raise HTTPException(status_code=404, detail="Editora não encontrada")
        
        # Verificar se ISBN já existe
        existing_book = db.query(models.Livro).filter(models.Livro.isbn == isbn).first()
        if existing_book:
            raise HTTPException(status_code=400, detail="ISBN já cadastrado")
        
        db_livro = models.Livro(
            titulo=titulo,
            subtitulo=subtitulo,
            autor_id=autor_id,
            editora_id=editora_id,
            isbn=isbn,
            edicao=edicao,
            ano_publicacao=ano_publicacao,
            num_paginas=num_paginas,
            sinopse=sinopse,
            genero=genero,
            idioma=idioma
        )
        
        db.add(db_livro)
        db.commit()
        db.refresh(db_livro)
        return RedirectResponse(url="/livros", status_code=303)
        
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Erro de integridade dos dados")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@router.put("/livros/{livro_id}")
async def update_livro(
    livro_id: int,
    titulo: Optional[str] = Form(None),
    subtitulo: Optional[str] = Form(None),
    autor_id: Optional[int] = Form(None),
    editora_id: Optional[int] = Form(None),
    isbn: Optional[str] = Form(None),
    edicao: Optional[int] = Form(None),
    ano_publicacao: Optional[int] = Form(None),
    num_paginas: Optional[int] = Form(None),
    sinopse: Optional[str] = Form(None),
    genero: Optional[str] = Form(None),
    idioma: Optional[str] = Form(None),
    status: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    try:
        livro = db.query(models.Livro).filter(models.Livro.id == livro_id).first()
        if not livro:
            raise HTTPException(status_code=404, detail="Livro não encontrado")
        
        # Atualizar apenas os campos fornecidos
        update_data = {}
        if titulo is not None:
            update_data["titulo"] = titulo
        if subtitulo is not None:
            update_data["subtitulo"] = subtitulo
        if autor_id is not None:
            # Verificar se o autor existe
            autor = db.query(models.Autor).filter(models.Autor.id == autor_id).first()
            if not autor:
                raise HTTPException(status_code=404, detail="Autor não encontrado")
            update_data["autor_id"] = autor_id
        if editora_id is not None:
            # Verificar se a editora existe
            editora = db.query(models.Editora).filter(models.Editora.id == editora_id).first()
            if not editora:
                raise HTTPException(status_code=404, detail="Editora não encontrada")
            update_data["editora_id"] = editora_id
        if isbn is not None:
            # Verificar se ISBN já existe em outro livro
            existing_book = db.query(models.Livro).filter(
                models.Livro.isbn == isbn, 
                models.Livro.id != livro_id
            ).first()
            if existing_book:
                raise HTTPException(status_code=400, detail="ISBN já cadastrado")
            update_data["isbn"] = isbn
        if edicao is not None:
            update_data["edicao"] = edicao
        if ano_publicacao is not None:
            update_data["ano_publicacao"] = ano_publicacao
        if num_paginas is not None:
            update_data["num_paginas"] = num_paginas
        if sinopse is not None:
            update_data["sinopse"] = sinopse
        if genero is not None:
            update_data["genero"] = genero
        if idioma is not None:
            update_data["idioma"] = idioma
        if status is not None:
            update_data["status"] = status
        
        for key, value in update_data.items():
            setattr(livro, key, value)
        
        db.commit()
        return RedirectResponse(url=f"/livros/{livro_id}", status_code=303)
        
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Erro de integridade dos dados")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@router.delete("/livros/{livro_id}")
async def delete_livro(livro_id: int, db: Session = Depends(get_db)):
    try:
        livro = db.query(models.Livro).filter(models.Livro.id == livro_id).first()
        if not livro:
            raise HTTPException(status_code=404, detail="Livro não encontrado")
        
        # Verificar se há empréstimos ativos
        emprestimos_ativos = db.query(models.Emprestimo).filter(
            models.Emprestimo.livro_id == livro_id,
            models.Emprestimo.status == models.StatusEmprestimo.ATIVO
        ).first()
        
        if emprestimos_ativos:
            raise HTTPException(
                status_code=400, 
                detail="Não é possível excluir livro com empréstimos ativos"
            )
        
        db.delete(livro)
        db.commit()
        return RedirectResponse(url="/livros", status_code=303)
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

# ==================== ROTAS PARA AUTORES ====================

@router.post("/autores/")
async def create_autor(
    nome: str = Form(...),
    nacionalidade: Optional[str] = Form(None),
    data_nascimento: Optional[str] = Form(None),
    biografia: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    try:
        # Converter data se fornecida
        data_nasc = None
        if data_nascimento:
            from datetime import datetime
            data_nasc = datetime.strptime(data_nascimento, "%Y-%m-%d").date()
        
        db_autor = models.Autor(
            nome=nome,
            nacionalidade=nacionalidade,
            data_nascimento=data_nasc,
            biografia=biografia
        )
        
        db.add(db_autor)
        db.commit()
        db.refresh(db_autor)
        return RedirectResponse(url="/autores", status_code=303)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail="Formato de data inválido. Use YYYY-MM-DD")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@router.put("/autores/{autor_id}")
async def update_autor(
    autor_id: int,
    nome: Optional[str] = Form(None),
    nacionalidade: Optional[str] = Form(None),
    data_nascimento: Optional[str] = Form(None),
    biografia: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    try:
        autor = db.query(models.Autor).filter(models.Autor.id == autor_id).first()
        if not autor:
            raise HTTPException(status_code=404, detail="Autor não encontrado")
        
        if nome is not None:
            autor.nome = nome
        if nacionalidade is not None:
            autor.nacionalidade = nacionalidade
        if data_nascimento is not None:
            from datetime import datetime
            autor.data_nascimento = datetime.strptime(data_nascimento, "%Y-%m-%d").date()
        if biografia is not None:
            autor.biografia = biografia
        
        db.commit()
        return RedirectResponse(url=f"/autores/{autor_id}", status_code=303)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail="Formato de data inválido. Use YYYY-MM-DD")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

# ==================== ROTAS PARA USUÁRIOS ====================

@router.post("/usuarios/")
async def create_usuario(
    nome: str = Form(...),
    email: str = Form(...),
    cpf: str = Form(...),
    matricula: str = Form(...),
    tipo: Optional[str] = Form("aluno"),
    curso: Optional[str] = Form(None),
    telefone: Optional[str] = Form(None),
    endereco: Optional[str] = Form(None),
    data_nascimento: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    try:
        # Verificar se email já existe
        existing_user = db.query(models.Usuario).filter(models.Usuario.email == email).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email já cadastrado")
        
        # Verificar se CPF já existe
        existing_cpf = db.query(models.Usuario).filter(models.Usuario.cpf == cpf).first()
        if existing_cpf:
            raise HTTPException(status_code=400, detail="CPF já cadastrado")
        
        # Verificar se matrícula já existe
        existing_matricula = db.query(models.Usuario).filter(models.Usuario.matricula == matricula).first()
        if existing_matricula:
            raise HTTPException(status_code=400, detail="Matrícula já cadastrada")
        
        # Converter data se fornecida
        data_nasc = None
        if data_nascimento:
            from datetime import datetime
            data_nasc = datetime.strptime(data_nascimento, "%Y-%m-%d").date()
        
        db_usuario = models.Usuario(
            nome=nome,
            email=email.lower(),
            cpf=cpf,
            matricula=matricula,
            tipo=tipo,
            curso=curso,
            telefone=telefone,
            endereco=endereco,
            data_nascimento=data_nasc
        )
        
        db.add(db_usuario)
        db.commit()
        db.refresh(db_usuario)
        return RedirectResponse(url="/usuarios", status_code=303)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail="Formato de data inválido. Use YYYY-MM-DD")
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Erro de integridade dos dados")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

# ==================== ROTAS PARA EMPRÉSTIMOS ====================

@router.post("/emprestimos/")
async def create_emprestimo(
    usuario_id: int = Form(...),
    livro_id: int = Form(...),
    observacoes: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    try:
        # Verificar se usuário existe e está ativo
        usuario = db.query(models.Usuario).filter(
            models.Usuario.id == usuario_id,
            models.Usuario.ativo == True
        ).first()
        if not usuario:
            raise HTTPException(status_code=404, detail="Usuário não encontrado ou inativo")
        
        # Verificar se livro existe e está disponível
        livro = db.query(models.Livro).filter(
            models.Livro.id == livro_id,
            models.Livro.status == models.StatusLivro.DISPONIVEL
        ).first()
        if not livro:
            raise HTTPException(status_code=404, detail="Livro não encontrado ou não disponível")
        
        # Verificar se usuário já tem empréstimo ativo deste livro
        emprestimo_existente = db.query(models.Emprestimo).filter(
            models.Emprestimo.usuario_id == usuario_id,
            models.Emprestimo.livro_id == livro_id,
            models.Emprestimo.status == models.StatusEmprestimo.ATIVO
        ).first()
        if emprestimo_existente:
            raise HTTPException(status_code=400, detail="Usuário já possui empréstimo ativo deste livro")
        
        # Criar empréstimo
        db_emprestimo = models.Emprestimo(
            usuario_id=usuario_id,
            livro_id=livro_id,
            observacoes=observacoes
        )
        
        # Atualizar status do livro
        livro.status = models.StatusLivro.EMPRESTADO
        
        db.add(db_emprestimo)
        db.commit()
        db.refresh(db_emprestimo)
        
        return RedirectResponse(url="/emprestimos", status_code=303)
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@router.put("/emprestimos/{emprestimo_id}/devolver")
async def devolver_livro(
    emprestimo_id: int,
    observacoes: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    try:
        emprestimo = db.query(models.Emprestimo).filter(
            models.Emprestimo.id == emprestimo_id,
            models.Emprestimo.status == models.StatusEmprestimo.ATIVO
        ).first()
        
        if not emprestimo:
            raise HTTPException(status_code=404, detail="Empréstimo não encontrado ou já finalizado")
        
        from datetime import datetime
        
        # Atualizar empréstimo
        emprestimo.data_devolucao_real = datetime.utcnow()
        emprestimo.status = models.StatusEmprestimo.DEVOLVIDO
        if observacoes:
            emprestimo.observacoes = observacoes
        
        # Calcular multa se atrasado
        if emprestimo.data_devolucao_real > emprestimo.data_devolucao_prevista:
            dias_atraso = (emprestimo.data_devolucao_real - emprestimo.data_devolucao_prevista).days
            emprestimo.multa = dias_atraso * 2.0  # R$ 2,00 por dia de atraso
        
        # Atualizar status do livro
        livro = db.query(models.Livro).filter(models.Livro.id == emprestimo.livro_id).first()
        livro.status = models.StatusLivro.DISPONIVEL
        
        db.commit()
        return RedirectResponse(url=f"/emprestimos/{emprestimo_id}", status_code=303)
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")
