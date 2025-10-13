from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.core.database import get_db
from app.models.models import (
    Emprestimo as DBEmprestimo, 
    Livro as DBLivro, 
    Usuario as DBUsuario,
    UsuarioAuth,
    StatusEmprestimo,
    StatusLivro,
    TipoUsuario
)
from app.core.auth import get_current_user
from pydantic import BaseModel, Field

# Schemas para empréstimo
class EmprestimoBase(BaseModel):
    usuario_id: int = Field(..., description="ID do usuário")
    livro_id: int = Field(..., description="ID do livro")
    observacoes: Optional[str] = Field(None, max_length=500, description="Observações do empréstimo")

class EmprestimoCreate(EmprestimoBase):
    pass

class EmprestimoUpdate(BaseModel):
    data_devolucao_real: Optional[datetime] = Field(None, description="Data de devolução real")
    status: Optional[StatusEmprestimo] = Field(None, description="Status do empréstimo")
    multa: Optional[float] = Field(None, ge=0, description="Valor da multa")
    observacoes: Optional[str] = Field(None, max_length=500, description="Observações")

class EmprestimoResponse(BaseModel):
    id: int
    usuario_id: int
    livro_id: int
    data_emprestimo: datetime
    data_devolucao_prevista: datetime
    data_devolucao_real: Optional[datetime]
    status: StatusEmprestimo
    multa: float
    observacoes: Optional[str]
    
    # Dados relacionados
    usuario_nome: Optional[str] = None
    livro_titulo: Optional[str] = None
    livro_autor: Optional[str] = None
    
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

@router.get("/emprestimos/", response_model=List[EmprestimoResponse])
def listar_emprestimos(
    skip: int = 0,
    limit: int = 100,
    status_filter: Optional[StatusEmprestimo] = None,
    db: Session = Depends(get_db),
    admin_user: UsuarioAuth = Depends(require_admin)
):
    """
    Lista todos os empréstimos (apenas admins)
    """
    query = db.query(DBEmprestimo).join(DBUsuario).join(DBLivro)
    
    if status_filter:
        query = query.filter(DBEmprestimo.status == status_filter)
    
    emprestimos = query.offset(skip).limit(limit).all()
    
    # Enriquecer com dados relacionados
    result = []
    for emp in emprestimos:
        emp_dict = {
            "id": emp.id,
            "usuario_id": emp.usuario_id,
            "livro_id": emp.livro_id,
            "data_emprestimo": emp.data_emprestimo,
            "data_devolucao_prevista": emp.data_devolucao_prevista,
            "data_devolucao_real": emp.data_devolucao_real,
            "status": emp.status,
            "multa": emp.multa,
            "observacoes": emp.observacoes,
            "usuario_nome": emp.usuario.nome if emp.usuario else None,
            "livro_titulo": emp.livro.titulo if emp.livro else None,
            "livro_autor": emp.livro.autor.nome if emp.livro and emp.livro.autor else None
        }
        result.append(EmprestimoResponse(**emp_dict))
    
    return result

@router.post("/emprestimos/", response_model=EmprestimoResponse, status_code=201)
def criar_emprestimo(
    emprestimo: EmprestimoCreate,
    db: Session = Depends(get_db),
    current_user: UsuarioAuth = Depends(get_current_user)
):
    """
    Cria um novo empréstimo (admins podem para qualquer usuário, usuários comuns apenas para si)
    """
    
    # Se não for admin, criar/buscar usuário automaticamente pela matrícula
    if not current_user.is_admin:
        # Buscar usuário na tabela usuarios pela matrícula do usuário logado
        usuario_logado = db.query(DBUsuario).filter(DBUsuario.matricula == current_user.matricula).first()
        
        # Se o usuário não existe na tabela usuarios, criar automaticamente
        if not usuario_logado:
            usuario_logado = DBUsuario(
                nome=current_user.nome,
                email=current_user.email,
                matricula=current_user.matricula,
                tipo=TipoUsuario.ALUNO,
                ativo=True
            )
            db.add(usuario_logado)
            db.commit()
            db.refresh(usuario_logado)
        
        # Para usuários comuns, usar sempre o ID do usuário logado
        emprestimo.usuario_id = usuario_logado.id
        
    else:
        # Para admins, verificar se o usuário especificado existe
        usuario = db.query(DBUsuario).filter(DBUsuario.id == emprestimo.usuario_id).first()
        
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuário não encontrado"
            )
    
    # Verificar se o livro existe e está disponível
    livro = db.query(DBLivro).filter(DBLivro.id == emprestimo.livro_id).first()
    if not livro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Livro não encontrado"
        )
    
    if livro.status != StatusLivro.DISPONIVEL:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Livro não está disponível para empréstimo. Status atual: {livro.status}"
        )
    
    # Verificar se o usuário já tem empréstimos ativos deste livro
    emprestimo_ativo = db.query(DBEmprestimo).filter(
        DBEmprestimo.usuario_id == emprestimo.usuario_id,
        DBEmprestimo.livro_id == emprestimo.livro_id,
        DBEmprestimo.status == StatusEmprestimo.ATIVO
    ).first()
    
    if emprestimo_ativo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuário já possui um empréstimo ativo deste livro"
        )
    
    # Criar o empréstimo
    db_emprestimo = DBEmprestimo(
        usuario_id=emprestimo.usuario_id,
        livro_id=emprestimo.livro_id,
        observacoes=emprestimo.observacoes
    )
    
    # Atualizar status do livro
    livro.status = StatusLivro.EMPRESTADO
    
    db.add(db_emprestimo)
    db.add(livro)
    db.commit()
    db.refresh(db_emprestimo)
    
    # Retornar com dados enriquecidos
    return EmprestimoResponse(
        id=db_emprestimo.id,
        usuario_id=db_emprestimo.usuario_id,
        livro_id=db_emprestimo.livro_id,
        data_emprestimo=db_emprestimo.data_emprestimo,
        data_devolucao_prevista=db_emprestimo.data_devolucao_prevista,
        data_devolucao_real=db_emprestimo.data_devolucao_real,
        status=db_emprestimo.status,
        multa=db_emprestimo.multa,
        observacoes=db_emprestimo.observacoes,
        usuario_nome=usuario.nome,
        livro_titulo=livro.titulo,
        livro_autor=livro.autor.nome if livro.autor else None
    )

@router.get("/emprestimos/{emprestimo_id}", response_model=EmprestimoResponse)
def obter_emprestimo(
    emprestimo_id: int,
    db: Session = Depends(get_db),
    admin_user: UsuarioAuth = Depends(require_admin)
):
    """
    Obtém um empréstimo por ID (apenas admins)
    """
    emprestimo = db.query(DBEmprestimo).filter(DBEmprestimo.id == emprestimo_id).first()
    if not emprestimo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Empréstimo não encontrado"
        )
    
    return EmprestimoResponse(
        id=emprestimo.id,
        usuario_id=emprestimo.usuario_id,
        livro_id=emprestimo.livro_id,
        data_emprestimo=emprestimo.data_emprestimo,
        data_devolucao_prevista=emprestimo.data_devolucao_prevista,
        data_devolucao_real=emprestimo.data_devolucao_real,
        status=emprestimo.status,
        multa=emprestimo.multa,
        observacoes=emprestimo.observacoes,
        usuario_nome=emprestimo.usuario.nome if emprestimo.usuario else None,
        livro_titulo=emprestimo.livro.titulo if emprestimo.livro else None,
        livro_autor=emprestimo.livro.autor.nome if emprestimo.livro and emprestimo.livro.autor else None
    )

@router.put("/emprestimos/{emprestimo_id}/devolver", response_model=EmprestimoResponse)
def devolver_livro(
    emprestimo_id: int,
    multa: Optional[float] = 0.0,
    observacoes: Optional[str] = None,
    db: Session = Depends(get_db),
    admin_user: UsuarioAuth = Depends(require_admin)
):
    """
    Registra a devolução de um livro (apenas admins)
    """
    emprestimo = db.query(DBEmprestimo).filter(DBEmprestimo.id == emprestimo_id).first()
    if not emprestimo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Empréstimo não encontrado"
        )
    
    if emprestimo.status != StatusEmprestimo.ATIVO:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Este empréstimo não está ativo"
        )
    
    # Atualizar empréstimo
    emprestimo.data_devolucao_real = datetime.utcnow()
    emprestimo.status = StatusEmprestimo.DEVOLVIDO
    emprestimo.multa = multa or 0.0
    if observacoes:
        emprestimo.observacoes = observacoes
    
    # Atualizar status do livro
    livro = db.query(DBLivro).filter(DBLivro.id == emprestimo.livro_id).first()
    if livro:
        livro.status = StatusLivro.DISPONIVEL
        db.add(livro)
    
    db.add(emprestimo)
    db.commit()
    db.refresh(emprestimo)
    
    return EmprestimoResponse(
        id=emprestimo.id,
        usuario_id=emprestimo.usuario_id,
        livro_id=emprestimo.livro_id,
        data_emprestimo=emprestimo.data_emprestimo,
        data_devolucao_prevista=emprestimo.data_devolucao_prevista,
        data_devolucao_real=emprestimo.data_devolucao_real,
        status=emprestimo.status,
        multa=emprestimo.multa,
        observacoes=emprestimo.observacoes,
        usuario_nome=emprestimo.usuario.nome if emprestimo.usuario else None,
        livro_titulo=emprestimo.livro.titulo if emprestimo.livro else None,
        livro_autor=emprestimo.livro.autor.nome if emprestimo.livro and emprestimo.livro.autor else None
    )

@router.get("/emprestimos/usuario/{usuario_id}", response_model=List[EmprestimoResponse])
def listar_emprestimos_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    admin_user: UsuarioAuth = Depends(require_admin)
):
    """
    Lista empréstimos de um usuário específico (apenas admins)
    """
    emprestimos = db.query(DBEmprestimo).filter(DBEmprestimo.usuario_id == usuario_id).all()
    
    result = []
    for emp in emprestimos:
        emp_dict = {
            "id": emp.id,
            "usuario_id": emp.usuario_id,
            "livro_id": emp.livro_id,
            "data_emprestimo": emp.data_emprestimo,
            "data_devolucao_prevista": emp.data_devolucao_prevista,
            "data_devolucao_real": emp.data_devolucao_real,
            "status": emp.status,
            "multa": emp.multa,
            "observacoes": emp.observacoes,
            "usuario_nome": emp.usuario.nome if emp.usuario else None,
            "livro_titulo": emp.livro.titulo if emp.livro else None,
            "livro_autor": emp.livro.autor.nome if emp.livro and emp.livro.autor else None
        }
        result.append(EmprestimoResponse(**emp_dict))
    
    return result
