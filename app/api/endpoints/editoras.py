from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.models import Editora as DBEditora, UsuarioAuth
from app.core.auth import get_current_user
from pydantic import BaseModel, Field

# Schemas para editora
class EditoraBase(BaseModel):
    nome: str = Field(..., min_length=1, max_length=100, example="Companhia das Letras")
    endereco: Optional[str] = Field(None, max_length=255, example="São Paulo, SP")
    telefone: Optional[str] = Field(None, max_length=20, example="(11) 3707-3500")
    email: Optional[str] = Field(None, max_length=100, example="contato@editora.com.br")
    website: Optional[str] = Field(None, max_length=255, example="https://www.editora.com.br")

class EditoraCreate(EditoraBase):
    pass

class EditoraUpdate(BaseModel):
    nome: Optional[str] = Field(None, min_length=1, max_length=100)
    endereco: Optional[str] = Field(None, max_length=255)
    telefone: Optional[str] = Field(None, max_length=20)
    email: Optional[str] = Field(None, max_length=100)
    website: Optional[str] = Field(None, max_length=255)

class EditoraResponse(EditoraBase):
    id: int
    
    class Config:
        from_attributes = True

# Dependency para verificar se é admin
async def require_admin(current_user: UsuarioAuth = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado. Apenas administradores podem realizar esta ação."
        )
    return current_user

router = APIRouter()

@router.get("/editoras/", response_model=List[EditoraResponse])
def listar_editoras(db: Session = Depends(get_db)):
    """
    Lista todas as editoras
    """
    editoras = db.query(DBEditora).all()
    return editoras

@router.post("/editoras/", response_model=EditoraResponse, status_code=201)
def criar_editora(
    editora: EditoraCreate,
    db: Session = Depends(get_db),
    admin_user: UsuarioAuth = Depends(require_admin)
):
    """
    Cria uma nova editora (apenas admins)
    """
    # Verificar se já existe editora com o mesmo nome
    existing_editora = db.query(DBEditora).filter(DBEditora.nome == editora.nome).first()
    if existing_editora:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Já existe uma editora com este nome"
        )
    
    db_editora = DBEditora(**editora.dict())
    db.add(db_editora)
    db.commit()
    db.refresh(db_editora)
    return db_editora

@router.get("/editoras/{editora_id}", response_model=EditoraResponse)
def obter_editora(editora_id: int, db: Session = Depends(get_db)):
    """
    Obtém uma editora por ID
    """
    editora = db.query(DBEditora).filter(DBEditora.id == editora_id).first()
    if not editora:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Editora não encontrada"
        )
    return editora

@router.put("/editoras/{editora_id}", response_model=EditoraResponse)
def atualizar_editora(
    editora_id: int,
    editora: EditoraUpdate,
    db: Session = Depends(get_db),
    admin_user: UsuarioAuth = Depends(require_admin)
):
    """
    Atualiza uma editora (apenas admins)
    """
    db_editora = db.query(DBEditora).filter(DBEditora.id == editora_id).first()
    if not db_editora:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Editora não encontrada"
        )
    
    # Verificar se o novo nome já existe (se fornecido)
    if editora.nome and editora.nome != db_editora.nome:
        existing_editora = db.query(DBEditora).filter(DBEditora.nome == editora.nome).first()
        if existing_editora:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Já existe uma editora com este nome"
            )
    
    update_data = editora.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_editora, key, value)
    
    db.add(db_editora)
    db.commit()
    db.refresh(db_editora)
    return db_editora

@router.delete("/editoras/{editora_id}", status_code=204)
def deletar_editora(
    editora_id: int,
    db: Session = Depends(get_db),
    admin_user: UsuarioAuth = Depends(require_admin)
):
    """
    Deleta uma editora (apenas admins)
    """
    db_editora = db.query(DBEditora).filter(DBEditora.id == editora_id).first()
    if not db_editora:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Editora não encontrada"
        )
    
    # Verificar se há livros associados
    if db_editora.livros:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não é possível excluir editora que possui livros associados"
        )
    
    db.delete(db_editora)
    db.commit()
    return {"ok": True}
