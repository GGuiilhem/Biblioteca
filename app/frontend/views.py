from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from pathlib import Path
from app.core.database import get_db
from app.models import models
from app.models.models import Emprestimo, UsuarioAuth
from app.core.auth import get_current_user

# Configuração dos templates
BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(Path(BASE_DIR, "templates")))
# Cria o router para as rotas do frontend
frontend_router = APIRouter()

# Alias para compatibilidade com código existente
router = frontend_router

# Função para verificar se o usuário é admin
def is_admin(user: UsuarioAuth) -> bool:
    return user.is_admin


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
        {"request": request, "livro_id": None}
    )

@router.get("/livros/{livro_id}/editar", response_class=HTMLResponse)
async def editar_livro(request: Request, livro_id: int):
    return templates.TemplateResponse(
        "livros/formulario.html",
        {"request": request, "livro_id": livro_id}
    )

@router.get("/livros/{livro_id}", response_class=HTMLResponse)
async def visualizar_livro(
    request: Request, 
    livro_id: int, 
    db: Session = Depends(get_db)
):
    # Busca o livro pelo ID
    livro = db.query(models.Livro).filter(models.Livro.id == livro_id).first()
    if not livro:
        raise HTTPException(status_code=404, detail="Livro não encontrado")
        
    return templates.TemplateResponse(
        "livros/detalhes.html",
        {
            "request": request, 
            "livro_id": livro_id,
            "livro": livro
        }
    )

# Rotas para Editoras (apenas admins)
@router.get("/editoras", response_class=HTMLResponse)
async def listar_editoras_page(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse(
        "editoras/lista.html",
        {"request": request}
    )

@router.get("/editoras/novo", response_class=HTMLResponse)
async def nova_editora(request: Request):
    return templates.TemplateResponse(
        "editoras/formulario.html",
        {"request": request, "editora_id": None}
    )

@router.get("/editoras/{editora_id}/editar", response_class=HTMLResponse)
async def editar_editora(request: Request, editora_id: int):
    return templates.TemplateResponse(
        "editoras/formulario.html",
        {"request": request, "editora_id": editora_id}
    )

@router.get("/editoras/{editora_id}", response_class=HTMLResponse)
async def visualizar_editora(
    request: Request, 
    editora_id: int, 
    db: Session = Depends(get_db)
):
    # Busca a editora pelo ID
    editora = db.query(models.Editora).filter(models.Editora.id == editora_id).first()
    if not editora:
        raise HTTPException(status_code=404, detail="Editora não encontrada")
        
    # Busca os livros da editora
    livros = db.query(models.Livro).filter(models.Livro.editora_id == editora_id).all()
    
    return templates.TemplateResponse(
        "editoras/detalhes.html",
        {
            "request": request, 
            "editora_id": editora_id,
            "editora": editora,
            "livros": livros
        }
    )

# Rotas para Empréstimos
@router.get("/emprestimos", response_class=HTMLResponse)
async def listar_emprestimos_page(request: Request):
    return templates.TemplateResponse(
        "emprestimos/lista.html",
        {"request": request}
    )

@router.get("/emprestimos/novo", response_class=HTMLResponse)
async def novo_emprestimo(request: Request):
    return templates.TemplateResponse(
        "emprestimos/formulario.html",
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

# Rotas de Autenticação
@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse(
        "auth/login.html",
        {"request": request}
    )

@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse(
        "auth/register.html",
        {"request": request}
    )

@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, db: Session = Depends(get_db)):
    try:
        # Calcular estatísticas reais do banco de dados
        from app.models.models import Livro, Usuario, StatusEmprestimo
        from datetime import datetime
        
        # Total de livros
        total_livros = db.query(Livro).count()
        
        # Empréstimos ativos
        emprestimos_ativos = db.query(Emprestimo).filter(
            Emprestimo.status == StatusEmprestimo.ATIVO
        ).count()
        
        # Empréstimos atrasados (data de devolução passou e ainda está ativo)
        hoje = datetime.now().date()
        emprestimos_atrasados = db.query(Emprestimo).filter(
            Emprestimo.status == StatusEmprestimo.ATIVO,
            Emprestimo.data_devolucao_prevista < hoje
        ).count()
        
        # Usuários ativos
        usuarios_ativos = db.query(Usuario).filter(Usuario.ativo == True).count()
        
        # Livros mais populares (versão simplificada e consistente)
        from sqlalchemy import func
        
        # Buscar os primeiros 3 livros com seus autores (dados consistentes)
        primeiros_livros = db.query(Livro, models.Autor).join(
            models.Autor, Livro.autor_id == models.Autor.id
        ).limit(3).all()
        
        # Criar lista com contagem real de empréstimos
        livros_populares = []
        for livro, autor in primeiros_livros:
            # Contar empréstimos reais para este livro
            total_emprestimos = db.query(Emprestimo).filter(
                Emprestimo.livro_id == livro.id
            ).count()
            
            livros_populares.append({
                'titulo': livro.titulo,
                'autor_nome': autor.nome,
                'total_emprestimos': total_emprestimos
            })
        
        # Empréstimos recentes (últimos 5)
        emprestimos_recentes = db.query(Emprestimo).join(
            Livro, Emprestimo.livro_id == Livro.id
        ).join(
            Usuario, Emprestimo.usuario_id == Usuario.id
        ).order_by(
            Emprestimo.data_emprestimo.desc()
        ).limit(5).all()
        
        # Estatísticas para o template
        stats = {
            "total_livros": total_livros,
            "emprestimos_ativos": emprestimos_ativos,
            "emprestimos_atrasados": emprestimos_atrasados,
            "usuarios_ativos": usuarios_ativos,
            "livros_populares": livros_populares,
            "emprestimos_recentes": emprestimos_recentes
        }
        
    except Exception as e:
        # Em caso de erro, usar valores padrão
        stats = {
            "total_livros": 0,
            "emprestimos_ativos": 0,
            "emprestimos_atrasados": 0,
            "usuarios_ativos": 0,
            "livros_populares": [],
            "emprestimos_recentes": []
        }
    
    return templates.TemplateResponse(
        "auth/dashboard.html",
        {"request": request, "stats": stats}
    )

# Exporta o router para ser importado por outros módulos
__all__ = ['frontend_router']
