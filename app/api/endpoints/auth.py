from datetime import timedelta, datetime
from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.core.database import get_db
from app.core.auth import (
    authenticate_user, 
    create_access_token, 
    get_password_hash,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    get_current_active_user
)
from app.models.models import UsuarioAuth
from app.schemas.auth import Token, RegisterRequest, UserResponse, LoginRequest

router = APIRouter()

def generate_matricula(db: Session) -> str:
    """Gera uma matrícula única no formato 2024001, 2024002, etc."""
    year = datetime.now().year
    year_prefix = str(year)
    
    # Buscar todas as matrículas do ano atual
    users_this_year = db.query(UsuarioAuth).filter(
        UsuarioAuth.matricula.like(f"{year_prefix}%")
    ).all()
    
    if users_this_year:
        # Extrair números sequenciais e encontrar o maior
        numbers = []
        for user in users_this_year:
            if user.matricula and len(user.matricula) >= 7:
                try:
                    number = int(user.matricula[4:])  # Remove os 4 primeiros dígitos (ano)
                    numbers.append(number)
                except ValueError:
                    continue
        
        next_number = max(numbers) + 1 if numbers else 1
    else:
        # Primeira matrícula do ano
        next_number = 1
    
    # Formatar com 3 dígitos (001, 002, etc.)
    return f"{year}{next_number:03d}"

@router.post("/login", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Login via API - retorna token JWT"""
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Atualizar último login
    user.ultimo_login = datetime.utcnow()
    db.commit()
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "user_id": user.id}, 
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }

@router.post("/login-form")
async def login_form(
    email: str = Form(...),
    senha: str = Form(...),
    db: Session = Depends(get_db)
):
    """Login via formulário HTML - redireciona para dashboard"""
    user = authenticate_user(db, email, senha)
    if not user:
        # Em uma implementação real, você redirecionaria com mensagem de erro
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos"
        )
    
    # Atualizar último login
    user.ultimo_login = datetime.utcnow()
    db.commit()
    
    # Por enquanto, redireciona para a página inicial
    # Em uma implementação completa, você definiria o cookie de sessão aqui
    return RedirectResponse(url="/", status_code=303)

@router.post("/register", response_model=UserResponse)
async def register_user(
    nome: str = Form(...),
    email: str = Form(...),
    senha: str = Form(...),
    confirmar_senha: str = Form(...),
    db: Session = Depends(get_db)
):
    """Registrar novo usuário"""
    
    # Validar se as senhas coincidem
    if senha != confirmar_senha:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Senhas não coincidem"
        )
    
    # Verificar se o email já existe
    existing_user = db.query(UsuarioAuth).filter(UsuarioAuth.email == email.lower()).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email já cadastrado"
        )
    
    try:
        # Gerar matrícula automática
        matricula = generate_matricula(db)
        
        # Criar novo usuário
        hashed_password = get_password_hash(senha)
        db_user = UsuarioAuth(
            matricula=matricula,
            nome=nome,
            email=email.lower(),
            senha_hash=hashed_password
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        return db_user
        
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Erro ao criar usuário"
        )

@router.post("/register-form")
async def register_form(
    nome: str = Form(...),
    email: str = Form(...),
    senha: str = Form(...),
    confirmar_senha: str = Form(...),
    db: Session = Depends(get_db)
):
    """Registrar via formulário HTML - redireciona para login"""
    
    try:
        # Usar a mesma lógica do endpoint de registro
        await register_user(nome, email, senha, confirmar_senha, db)
        
        # Redirecionar para página de login com sucesso
        return RedirectResponse(url="/login?registered=true", status_code=303)
        
    except HTTPException as e:
        # Em uma implementação real, você redirecionaria com mensagem de erro
        raise e

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: UsuarioAuth = Depends(get_current_active_user)):
    """Obter informações do usuário atual"""
    return current_user

@router.post("/logout")
async def logout():
    """Logout - invalida o token (implementação básica)"""
    # Em uma implementação completa, você invalidaria o token no servidor
    return {"message": "Logout realizado com sucesso"}

@router.post("/logout-form")
async def logout_form():
    """Logout via formulário - redireciona para home"""
    # Remove cookie de sessão e redireciona
    response = RedirectResponse(url="/", status_code=303)
    return response
