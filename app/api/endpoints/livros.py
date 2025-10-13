from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.models import Livro as DBLivro, Autor as DBAutor, Editora as DBEditora
from app.schemas.book import Livro, LivroCreate, LivroUpdate
from app.core.auth import get_current_user
from app.models.models import UsuarioAuth

# Dependency para verificar se é admin
async def require_admin(current_user: UsuarioAuth = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado. Apenas administradores podem realizar esta ação."
        )
    return current_user

router = APIRouter()

@router.post("/livros/", response_model=Livro, status_code=201)
def create_livro(
    livro: LivroCreate, 
    db: Session = Depends(get_db),
    admin_user: UsuarioAuth = Depends(require_admin)
):
    """
    Cria um novo livro
    """
    # Verificar se o autor existe
    autor = db.query(DBAutor).filter(DBAutor.id == livro.autor_id).first()
    if not autor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Autor não encontrado"
        )
    
    # Verificar se a editora existe (se fornecida)
    if livro.editora_id:
        editora = db.query(DBEditora).filter(DBEditora.id == livro.editora_id).first()
        if not editora:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Editora não encontrada"
            )
    
    # Verificar se já existe um livro com o mesmo ISBN
    existing_book = db.query(DBLivro).filter(DBLivro.isbn == livro.isbn).first()
    if existing_book:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Já existe um livro cadastrado com este ISBN"
        )
    
    # Criar o livro
    db_livro = DBLivro(**livro.dict())
    db.add(db_livro)
    db.commit()
    db.refresh(db_livro)
    
    return db_livro

@router.get("/livros/", response_model=List[Livro])
def read_livros(
    skip: int = 0, 
    limit: int = 100,
    search: str = None,
    db: Session = Depends(get_db)
):
    """
    Lista todos os livros com ordenação alfabética e pesquisa opcional
    """
    query = db.query(DBLivro)
    
    # Aplicar filtro de pesquisa se fornecido
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            DBLivro.titulo.ilike(search_filter)
        )
    
    # Ordenar alfabeticamente por título
    query = query.order_by(DBLivro.titulo.asc())
    
    livros = query.offset(skip).limit(limit).all()
    return livros

@router.get("/livros/{livro_id}", response_model=Livro)
def read_livro(
    livro_id: int, 
    db: Session = Depends(get_db)
):
    """
    Busca um livro por ID
    """
    livro = db.query(DBLivro).filter(DBLivro.id == livro_id).first()
    if not livro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Livro não encontrado"
        )
    return livro

@router.put("/livros/{livro_id}", response_model=Livro)
def update_livro(
    livro_id: int,
    livro_update: LivroUpdate,
    db: Session = Depends(get_db),
    admin_user: UsuarioAuth = Depends(require_admin)
):
    """
    Atualiza um livro
    """
    livro = db.query(DBLivro).filter(DBLivro.id == livro_id).first()
    if not livro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Livro não encontrado"
        )
    
    # Atualizar apenas os campos fornecidos
    update_data = livro_update.dict(exclude_unset=True)
    
    # Verificar se o autor existe (se fornecido)
    if "autor_id" in update_data:
        autor = db.query(DBAutor).filter(DBAutor.id == update_data["autor_id"]).first()
        if not autor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Autor não encontrado"
            )
    
    # Verificar se a editora existe (se fornecida)
    if "editora_id" in update_data and update_data["editora_id"]:
        editora = db.query(DBEditora).filter(DBEditora.id == update_data["editora_id"]).first()
        if not editora:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Editora não encontrada"
            )
    
    # Verificar ISBN único (se fornecido)
    if "isbn" in update_data:
        existing_book = db.query(DBLivro).filter(
            DBLivro.isbn == update_data["isbn"],
            DBLivro.id != livro_id
        ).first()
        if existing_book:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Já existe outro livro cadastrado com este ISBN"
            )
    
    # Aplicar atualizações
    for field, value in update_data.items():
        setattr(livro, field, value)
    
    db.commit()
    db.refresh(livro)
    
    return livro

@router.delete("/livros/{livro_id}")
def delete_livro(
    livro_id: int,
    db: Session = Depends(get_db),
    admin_user: UsuarioAuth = Depends(require_admin)
):
    """
    Remove um livro
    """
    livro = db.query(DBLivro).filter(DBLivro.id == livro_id).first()
    if not livro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Livro não encontrado"
        )
    
    db.delete(livro)
    db.commit()
    
    return {"message": "Livro removido com sucesso"}
