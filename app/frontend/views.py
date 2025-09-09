from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from pathlib import Path

from app.core.database import get_db
from app.models import models

# Configuração dos templates
BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(Path(BASE_DIR, "templates")))

# Cria o router para as rotas do frontend
frontend_router = APIRouter()

# Alias para compatibilidade com código existente
router = frontend_router

@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

@router.get("/livros", response_class=HTMLResponse)
async def listar_livros(
    request: Request,
    db: Session = Depends(get_db)
):
    livros = db.query(models.Livro).all()
    return templates.TemplateResponse(
        "livros/lista.html",
        {"request": request, "livros": livros}
    )

@router.get("/livros/novo", response_class=HTMLResponse)
async def novo_livro(request: Request):
    return templates.TemplateResponse(
        "livros/formulario.html",
        {"request": request}
    )

# Rotas para Autores
@router.get("/autores", response_class=HTMLResponse)
async def listar_autores(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse(
        "autores/lista.html",
        {"request": request}
    )

@router.get("/autores/novo", response_class=HTMLResponse)
async def novo_autor(request: Request):
    return templates.TemplateResponse(
        "autores/formulario.html",
        {"request": request, "autor_id": None}
    )

@router.get("/autores/editar/{autor_id}", response_class=HTMLResponse)
async def editar_autor(request: Request, autor_id: int):
    return templates.TemplateResponse(
        "autores/formulario.html",
        {"request": request, "autor_id": autor_id}
    )

@router.get("/autores/{autor_id}", response_class=HTMLResponse)
async def visualizar_autor(
    request: Request, 
    autor_id: int, 
    db: Session = Depends(get_db)
):
    # Busca o autor pelo ID
    autor = db.query(models.Autor).filter(models.Autor.id == autor_id).first()
    if not autor:
        raise HTTPException(status_code=404, detail="Autor não encontrado")
        
    # Busca os livros do autor
    livros = db.query(models.Livro).filter(models.Livro.autor_id == autor_id).all()
    
    return templates.TemplateResponse(
        "autores/detalhes.html",
        {
            "request": request, 
            "autor_id": autor_id,
            "autor": autor,
            "livros": livros
        }
    )

# Rotas para Usuários
@router.get("/usuarios", response_class=HTMLResponse)
async def listar_usuarios(request: Request):
    return templates.TemplateResponse(
        "usuarios/lista.html",
        {"request": request}
    )

@router.get("/usuarios/novo", response_class=HTMLResponse)
async def novo_usuario(request: Request):
    return templates.TemplateResponse(
        "usuarios/formulario.html",
        {"request": request, "usuario_id": None}
    )

@router.get("/usuarios/editar/{usuario_id}", response_class=HTMLResponse)
async def editar_usuario(request: Request, usuario_id: int):
    return templates.TemplateResponse(
        "usuarios/formulario.html",
        {"request": request, "usuario_id": usuario_id}
    )

@router.get("/usuarios/{usuario_id}", response_class=HTMLResponse)
async def visualizar_usuario(
    request: Request, 
    usuario_id: int,
    db: Session = Depends(get_db)
):
    # Busca o usuário pelo ID
    usuario = db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    # Busca os empréstimos ativos do usuário
    emprestimos = db.query(models.Emprestimo).filter(
        models.Emprestimo.usuario_id == usuario_id,
        models.Emprestimo.status == "ativo"
    ).all()
    
    return templates.TemplateResponse(
        "usuarios/detalhes.html",
        {
            "request": request,
            "usuario_id": usuario_id,
            "usuario": usuario,
            "emprestimos": emprestimos
        }
    )

# Exporta o router para ser importado por outros módulos
__all__ = ['frontend_router']
