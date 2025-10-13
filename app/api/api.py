from fastapi import APIRouter
from app.api.endpoints import authors, auth, usuarios, livros, solicitacoes_autores, editoras, emprestimos

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(authors.router, prefix="", tags=["authors"])
api_router.include_router(usuarios.router, prefix="", tags=["usuarios"])
api_router.include_router(livros.router, prefix="", tags=["livros"])
api_router.include_router(editoras.router, prefix="", tags=["editoras"])
api_router.include_router(emprestimos.router, prefix="", tags=["emprestimos"])
api_router.include_router(solicitacoes_autores.router, prefix="", tags=["solicitacoes-autores"])
