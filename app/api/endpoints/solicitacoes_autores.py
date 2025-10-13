from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime

from app.core.database import get_db
from app.models.models import SolicitacaoAutor as DBSolicitacaoAutor, Autor as DBAutor, UsuarioAuth, StatusSolicitacao
from app.schemas.solicitacao_autor import (
    SolicitacaoAutorCreate, 
    SolicitacaoAutorResponse, 
    SolicitacaoAutorUpdate,
    SolicitacaoAutorSimples
)
from app.core.auth import get_current_user

router = APIRouter()

# Dependency para verificar se é admin
async def require_admin(current_user: UsuarioAuth = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado. Apenas administradores podem realizar esta ação."
        )
    return current_user

@router.post("/solicitacoes-autores/", response_model=SolicitacaoAutorResponse, status_code=201)
def criar_solicitacao_autor(
    solicitacao: SolicitacaoAutorCreate,
    db: Session = Depends(get_db),
    current_user: UsuarioAuth = Depends(get_current_user)
):
    """
    Cria uma nova solicitação de autor (usuários comuns)
    """
    # Verificar se já existe um autor com o mesmo nome
    autor_existente = db.query(DBAutor).filter(DBAutor.nome.ilike(f"%{solicitacao.nome}%")).first()
    if autor_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Já existe um autor cadastrado com nome similar"
        )
    
    # Verificar se já existe uma solicitação pendente para este autor
    solicitacao_existente = db.query(DBSolicitacaoAutor).filter(
        DBSolicitacaoAutor.nome.ilike(f"%{solicitacao.nome}%"),
        DBSolicitacaoAutor.status == StatusSolicitacao.PENDENTE
    ).first()
    
    if solicitacao_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Já existe uma solicitação pendente para um autor com nome similar"
        )
    
    # Criar a solicitação
    db_solicitacao = DBSolicitacaoAutor(
        **solicitacao.dict(),
        solicitante_id=current_user.id
    )
    db.add(db_solicitacao)
    db.commit()
    db.refresh(db_solicitacao)
    
    # Preparar resposta
    response = SolicitacaoAutorResponse(
        **db_solicitacao.__dict__,
        solicitante_nome=current_user.nome,
        aprovado_por_nome=None
    )
    
    return response

@router.get("/solicitacoes-autores/", response_model=List[SolicitacaoAutorSimples])
def listar_solicitacoes_autores(
    skip: int = 0,
    limit: int = 100,
    status_filtro: Optional[StatusSolicitacao] = None,
    db: Session = Depends(get_db),
    admin_user: UsuarioAuth = Depends(require_admin)
):
    """
    Lista todas as solicitações de autores (apenas admins)
    """
    query = db.query(DBSolicitacaoAutor)
    
    if status_filtro:
        query = query.filter(DBSolicitacaoAutor.status == status_filtro)
    
    solicitacoes = query.offset(skip).limit(limit).all()
    
    # Preparar resposta com nomes dos solicitantes
    response = []
    for solicitacao in solicitacoes:
        solicitante = db.query(UsuarioAuth).filter(UsuarioAuth.id == solicitacao.solicitante_id).first()
        response.append(SolicitacaoAutorSimples(
            **solicitacao.__dict__,
            solicitante_nome=solicitante.nome if solicitante else "Usuário não encontrado"
        ))
    
    return response

@router.get("/solicitacoes-autores/{solicitacao_id}", response_model=SolicitacaoAutorResponse)
def obter_solicitacao_autor(
    solicitacao_id: int,
    db: Session = Depends(get_db),
    admin_user: UsuarioAuth = Depends(require_admin)
):
    """
    Obtém detalhes de uma solicitação específica (apenas admins)
    """
    solicitacao = db.query(DBSolicitacaoAutor).filter(DBSolicitacaoAutor.id == solicitacao_id).first()
    if not solicitacao:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Solicitação não encontrada"
        )
    
    # Buscar dados dos usuários
    solicitante = db.query(UsuarioAuth).filter(UsuarioAuth.id == solicitacao.solicitante_id).first()
    aprovado_por = None
    if solicitacao.aprovado_por_id:
        aprovado_por = db.query(UsuarioAuth).filter(UsuarioAuth.id == solicitacao.aprovado_por_id).first()
    
    response = SolicitacaoAutorResponse(
        **solicitacao.__dict__,
        solicitante_nome=solicitante.nome if solicitante else "Usuário não encontrado",
        aprovado_por_nome=aprovado_por.nome if aprovado_por else None
    )
    
    return response

@router.put("/solicitacoes-autores/{solicitacao_id}/aprovar")
def aprovar_solicitacao_autor(
    solicitacao_id: int,
    db: Session = Depends(get_db),
    admin_user: UsuarioAuth = Depends(require_admin)
):
    """
    Aprova uma solicitação de autor e cria o autor (apenas admins)
    """
    solicitacao = db.query(DBSolicitacaoAutor).filter(DBSolicitacaoAutor.id == solicitacao_id).first()
    if not solicitacao:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Solicitação não encontrada"
        )
    
    if solicitacao.status != StatusSolicitacao.PENDENTE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Apenas solicitações pendentes podem ser aprovadas"
        )
    
    # Criar o autor
    novo_autor = DBAutor(
        nome=solicitacao.nome,
        nacionalidade=solicitacao.nacionalidade,
        data_nascimento=solicitacao.data_nascimento,
        biografia=solicitacao.biografia
    )
    db.add(novo_autor)
    
    # Atualizar a solicitação
    solicitacao.status = StatusSolicitacao.APROVADA
    solicitacao.data_aprovacao = datetime.utcnow()
    solicitacao.aprovado_por_id = admin_user.id
    
    db.commit()
    
    return {"message": "Solicitação aprovada e autor criado com sucesso", "autor_id": novo_autor.id}

@router.put("/solicitacoes-autores/{solicitacao_id}/rejeitar")
def rejeitar_solicitacao_autor(
    solicitacao_id: int,
    observacoes: str,
    db: Session = Depends(get_db),
    admin_user: UsuarioAuth = Depends(require_admin)
):
    """
    Rejeita uma solicitação de autor (apenas admins)
    """
    solicitacao = db.query(DBSolicitacaoAutor).filter(DBSolicitacaoAutor.id == solicitacao_id).first()
    if not solicitacao:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Solicitação não encontrada"
        )
    
    if solicitacao.status != StatusSolicitacao.PENDENTE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Apenas solicitações pendentes podem ser rejeitadas"
        )
    
    # Atualizar a solicitação
    solicitacao.status = StatusSolicitacao.REJEITADA
    solicitacao.data_aprovacao = datetime.utcnow()
    solicitacao.aprovado_por_id = admin_user.id
    solicitacao.observacoes = observacoes
    
    db.commit()
    
    return {"message": "Solicitação rejeitada com sucesso"}

@router.get("/minhas-solicitacoes-autores/", response_model=List[SolicitacaoAutorSimples])
def listar_minhas_solicitacoes(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: UsuarioAuth = Depends(get_current_user)
):
    """
    Lista as solicitações do usuário atual
    """
    solicitacoes = db.query(DBSolicitacaoAutor).filter(
        DBSolicitacaoAutor.solicitante_id == current_user.id
    ).offset(skip).limit(limit).all()
    
    response = []
    for solicitacao in solicitacoes:
        response.append(SolicitacaoAutorSimples(
            **solicitacao.__dict__,
            solicitante_nome=current_user.nome
        ))
    
    return response
