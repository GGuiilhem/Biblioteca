from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.models import Autor as DBAutor, UsuarioAuth
from app.schemas.author import Autor, AutorCreate, AutorUpdate
from app.core.auth import get_current_user

# Dependency para verificar se é admin
async def require_admin(current_user: UsuarioAuth = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado. Apenas administradores podem realizar esta ação."
        )
    return current_user

router = APIRouter()

@router.post("/autores/", response_model=Autor, status_code=201)
def create_author(
    autor: AutorCreate, 
    db: Session = Depends(get_db),
    admin_user: UsuarioAuth = Depends(require_admin)
):
    """
    Cria um novo autor (apenas admins)
    """
    db_autor = DBAutor(**autor.dict())
    db.add(db_autor)
    db.commit()
    db.refresh(db_autor)
    return db_autor

@router.get("/autores/", response_model=List[Autor])
def read_authors(
    skip: int = 0, 
    limit: int = 100, 
    search: str = None,
    db: Session = Depends(get_db)
):
    """
    Lista todos os autores com ordenação alfabética e pesquisa opcional
    """
    query = db.query(DBAutor)
    
    # Aplicar filtro de pesquisa se fornecido
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            DBAutor.nome.ilike(search_filter)
        )
    
    # Ordenar alfabeticamente por nome
    query = query.order_by(DBAutor.nome.asc())
    
    autores = query.offset(skip).limit(limit).all()
    return autores

@router.get("/autores/{autor_id}", response_model=Autor)
def read_autor(autor_id: int, db: Session = Depends(get_db)):
    """
    Busca um autor específico pelo ID
    """
    db_autor = db.query(DBAutor).filter(DBAutor.id == autor_id).first()
    if db_autor is None:
        raise HTTPException(status_code=404, detail="Autor não encontrado")
    return db_autor

@router.put("/autores/{autor_id}", response_model=Autor)
def update_autor(
    autor_id: int,
    autor: AutorUpdate,
    db: Session = Depends(get_db),
    admin_user: UsuarioAuth = Depends(require_admin)
):
    """
    Atualiza um autor existente (apenas admins)
    """
    db_autor = db.query(DBAutor).filter(DBAutor.id == autor_id).first()
    if db_autor is None:
        raise HTTPException(status_code=404, detail="Autor não encontrado")

    update_data = autor.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_autor, key, value)

    db.add(db_autor)
    db.commit()
    db.refresh(db_autor)
    return db_autor

@router.delete("/autores/{autor_id}", status_code=204)
def delete_autor(
    autor_id: int, 
    db: Session = Depends(get_db),
    admin_user: UsuarioAuth = Depends(require_admin)
):
    """
    Deleta um autor (apenas admins)
    """
    db_autor = db.query(DBAutor).filter(DBAutor.id == autor_id).first()
    if db_autor is None:
        raise HTTPException(status_code=404, detail="Autor não encontrado")

    db.delete(db_autor)
    db.commit()
    return {"ok": True}
