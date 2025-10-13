from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.models import Usuario as DBUsuario, UsuarioAuth as DBUsuarioAuth
from app.schemas.user import User, UserCreate, UserUpdate
from app.core.auth import get_current_user
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# Schema para exibir todas as contas do sistema
class ContaUsuario(BaseModel):
    id: int
    nome: str
    email: str
    tipo_conta: str  # "completa" ou "auth"
    cpf: Optional[str] = None
    matricula: Optional[str] = None
    tipo: Optional[str] = None
    ativo: Optional[bool] = None
    data_cadastro: Optional[datetime] = None
    criado_em: Optional[datetime] = None
    ultimo_login: Optional[datetime] = None
    is_admin: Optional[bool] = False
    
    class Config:
        from_attributes = True

router = APIRouter()

@router.post("/usuarios/", response_model=User, status_code=201)
def create_user(usuario: UserCreate, db: Session = Depends(get_db)):
    """
    Cria um novo usuário
    """
    # Verificar se email já existe
    db_user = db.query(DBUsuario).filter(DBUsuario.email == usuario.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email já cadastrado")
    
    db_usuario = DBUsuario(**usuario.dict())
    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)
    return db_usuario

@router.get("/usuarios/", response_model=List[ContaUsuario])
def read_users(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: DBUsuarioAuth = Depends(get_current_user)
):
    """
    Lista todas as contas do sistema (usuários completos + contas de autenticação)
    """
    contas = []
    
    # Buscar usuários completos
    usuarios_completos = db.query(DBUsuario).offset(skip).limit(limit).all()
    for usuario in usuarios_completos:
        conta = ContaUsuario(
            id=usuario.id,
            nome=usuario.nome,
            email=usuario.email,
            tipo_conta="completa",
            cpf=usuario.cpf,
            matricula=usuario.matricula,
            tipo=usuario.tipo.value if usuario.tipo else None,
            ativo=usuario.ativo,
            data_cadastro=usuario.data_cadastro
        )
        contas.append(conta)
    
    # Buscar contas de autenticação (login/registro)
    usuarios_auth = db.query(DBUsuarioAuth).offset(skip).limit(limit).all()
    for usuario_auth in usuarios_auth:
        conta = ContaUsuario(
            id=usuario_auth.id,
            nome=usuario_auth.nome,
            email=usuario_auth.email,
            tipo_conta="auth",
            matricula=usuario_auth.matricula,
            criado_em=usuario_auth.criado_em,
            ultimo_login=usuario_auth.ultimo_login,
            is_admin=usuario_auth.is_admin
        )
        contas.append(conta)
    
    return contas

@router.get("/usuarios/{usuario_id}", response_model=User)
def read_user(
    usuario_id: int, 
    db: Session = Depends(get_db),
    current_user: DBUsuario = Depends(get_current_user)
):
    """
    Busca um usuário específico pelo ID (requer autenticação)
    """
    db_usuario = db.query(DBUsuario).filter(DBUsuario.id == usuario_id).first()
    if db_usuario is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return db_usuario

@router.put("/usuarios/{usuario_id}", response_model=User)
def update_user(
    usuario_id: int,
    usuario: UserUpdate,
    db: Session = Depends(get_db),
    current_user: DBUsuario = Depends(get_current_user)
):
    """
    Atualiza um usuário existente (requer autenticação)
    """
    db_usuario = db.query(DBUsuario).filter(DBUsuario.id == usuario_id).first()
    if db_usuario is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    # Verificar se o usuário pode editar (só pode editar próprio perfil ou ser admin)
    if current_user.id != usuario_id:
        raise HTTPException(status_code=403, detail="Sem permissão para editar este usuário")

    update_data = usuario.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_usuario, key, value)

    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)
    return db_usuario

@router.delete("/usuarios/{usuario_id}", status_code=204)
def delete_user(
    usuario_id: int, 
    db: Session = Depends(get_db),
    current_user: DBUsuario = Depends(get_current_user)
):
    """
    Deleta um usuário (requer autenticação)
    """
    db_usuario = db.query(DBUsuario).filter(DBUsuario.id == usuario_id).first()
    if db_usuario is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    # Verificar se o usuário pode deletar (só pode deletar próprio perfil)
    if current_user.id != usuario_id:
        raise HTTPException(status_code=403, detail="Sem permissão para deletar este usuário")

    db.delete(db_usuario)
    db.commit()
    return {"ok": True}
