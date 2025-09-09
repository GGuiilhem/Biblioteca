from pydantic_settings import BaseSettings
from typing import Dict, Any

class Settings(BaseSettings):
    PROJECT_NAME: str = "Biblioteca - IMPACTA"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Configurações do Jinja2
    TEMPLATES_AUTO_RELOAD: bool = True
    TEMPLATES_STRIP_WHITESPACE: bool = True
    
    # Configurações de segurança
    SECRET_KEY: str = "sua-chave-secreta-aqui"  # Em produção, use uma chave segura e armazene em variáveis de ambiente
    
    class Config:
        case_sensitive = True

# Configurações do Jinja2
JINJA2_FILTERS: Dict[str, Any] = {
    'tojson': lambda x: x  # Filtro para converter para JSON
}

settings = Settings()
