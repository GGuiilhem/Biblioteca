# 📚 Sistema de Biblioteca IMPACTA

Sistema completo de gerenciamento de biblioteca desenvolvido com **FastAPI**, **SQLAlchemy** e **Bootstrap 5**. Interface moderna, responsiva e funcionalidades completas para controle de acervo, usuários e empréstimos.

## ✨ Principais Recursos

- 🎨 **Interface moderna e responsiva** com design limpo
- 📖 **Gerenciamento completo de livros** com busca avançada
- 👥 **Sistema de autores** com biografias e relacionamentos
- 🔐 **Autenticação JWT** com níveis de acesso (Admin/Usuário)
- 📋 **Controle de empréstimos** com cálculo automático de multas
- 🏢 **Gestão de editoras** e categorização
- 📊 **Dashboard administrativo** com estatísticas em tempo real
- 🔍 **Busca inteligente** com filtros por título, autor e categoria
- 📱 **Design responsivo** otimizado para mobile e desktop

## 🚀 Instalação e Configuração

### Pré-requisitos
- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)

### 1. Clone o repositório
```bash
git clone <url-do-repositorio>
cd Biblioteca
```

### 2. Crie e ative o ambiente virtual
**Windows:**
```bash
python -m venv venv
.\venv\Scripts\activate
```

**Linux/MacOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instale as dependências
```bash
pip install -r requirements.txt
```

### 4. Inicialize o banco de dados
```bash
python init_db.py
```

**⚠️ Se os usuários padrão não funcionarem:**
```bash
# Reset completo do banco de dados
python reset_db.py
python init_db.py
```

### 5. Execute a aplicação
```bash
python main.py
```

## 🌐 Acessando o Sistema

Após iniciar o servidor, acesse:

- **🏠 Interface Principal**: http://localhost:8001
- **📚 Documentação da API**: http://localhost:8001/docs  
- **📖 Documentação Alternativa**: http://localhost:8001/redoc

### 👤 Usuários Padrão
- **Admin**: `admin@impacta.edu.br` / `admin123`
- **Usuário**: `teste@impacta.edu.br` / `123456`

### 🔧 Troubleshooting - Problemas de Login

**Se os usuários não funcionarem, execute:**

1. **Verificar usuários no banco:**
```bash
python check_users.py
```

2. **Reset completo (se necessário):**
```bash
python reset_db.py
python init_db.py
```

3. **Verificar novamente:**
```bash
python check_users.py
```

## 📁 Estrutura do Projeto

```
Biblioteca/
├── app/
│   ├── api/                    # API REST
│   │   ├── api.py             # Router principal da API
│   │   └── endpoints/         # Endpoints organizados por módulo
│   │       ├── auth.py        # Autenticação JWT
│   │       ├── authors.py     # Gestão de autores
│   │       ├── editoras.py    # Gestão de editoras
│   │       ├── emprestimos.py # Sistema de empréstimos
│   │       ├── livros.py      # Gestão de livros
│   │       ├── solicitacoes_autores.py # Solicitações de novos autores
│   │       └── usuarios.py    # Gestão de usuários
│   │
│   ├── core/                  # Configurações principais
│   │   ├── auth.py           # Lógica de autenticação
│   │   ├── config.py         # Configurações da aplicação
│   │   └── database.py       # Configuração do banco de dados
│   │
│   ├── frontend/             # Interface web
│   │   └── views.py          # Rotas do frontend
│   │
│   ├── backend/              # Processamento de formulários
│   │   └── routes.py         # Rotas de processamento
│   │
│   ├── models/               # Modelos do banco de dados
│   │   └── models.py         # Definições SQLAlchemy
│   │
│   ├── schemas/              # Validação de dados
│   │   ├── auth.py           # Schemas de autenticação
│   │   ├── author.py         # Schemas de autores
│   │   ├── book.py           # Schemas de livros
│   │   ├── emprestimo.py     # Schemas de empréstimos
│   │   ├── solicitacao_autor.py # Schemas de solicitações
│   │   └── user.py           # Schemas de usuários
│   │
│   ├── static/               # Arquivos estáticos
│   │   ├── css/style.css     # Estilos personalizados
│   │   └── js/main.js        # JavaScript principal
│   │
│   └── templates/            # Templates HTML (Jinja2)
│       ├── base.html         # Template base
│       ├── home.html         # Página inicial
│       ├── auth/             # Templates de autenticação
│       ├── autores/          # Templates de autores
│       ├── editoras/         # Templates de editoras
│       ├── emprestimos/      # Templates de empréstimos
│       ├── livros/           # Templates de livros
│       └── usuarios/         # Templates de usuários
│
├── .gitignore               # Arquivos ignorados pelo Git
├── README.md               # Documentação do projeto
├── requirements.txt        # Dependências Python
├── main.py                # Ponto de entrada da aplicação
├── init_db.py             # Inicialização do banco de dados
└── biblioteca.db          # Banco de dados SQLite
```

## 📚 Funcionalidades Detalhadas

### 📖 Gerenciamento de Livros
- ✅ **CRUD completo** - Criar, visualizar, editar e excluir livros
- ✅ **Busca avançada** - Por título, autor, ISBN, categoria
- ✅ **Filtros inteligentes** - Status, editora, ano de publicação
- ✅ **Upload de capas** - Suporte a imagens de capa
- ✅ **Controle de status** - Disponível, Emprestado, Em Manutenção
- ✅ **Informações completas** - ISBN, sinopse, idioma, páginas

### 👥 Sistema de Autores
- ✅ **Perfis completos** - Nome, biografia, nacionalidade
- ✅ **Relacionamentos** - Livros por autor
- ✅ **Solicitações** - Usuários podem solicitar novos autores
- ✅ **Aprovação** - Sistema de aprovação para administradores

### 🔐 Autenticação e Autorização
- ✅ **JWT Tokens** - Autenticação segura baseada em tokens
- ✅ **Níveis de acesso** - Administrador e Usuário comum
- ✅ **Proteção de rotas** - Endpoints protegidos por permissão
- ✅ **Sessões persistentes** - Login automático

### 📋 Sistema de Empréstimos
- ✅ **Controle completo** - Criar, visualizar, devolver
- ✅ **Cálculo automático** - Datas de devolução e multas
- ✅ **Status dinâmico** - Ativo, Finalizado, Atrasado
- ✅ **Histórico** - Registro completo de movimentações
- ✅ **Validações** - Disponibilidade e limites por usuário

### 🏢 Gestão de Editoras
- ✅ **Cadastro completo** - Nome, informações de contato
- ✅ **Relacionamentos** - Livros por editora
- ✅ **Organização** - Categorização do acervo

### 📊 Dashboard e Relatórios
- ✅ **Estatísticas em tempo real** - Livros, autores, empréstimos
- ✅ **Gráficos interativos** - Visualização de dados
- ✅ **Métricas importantes** - Livros mais emprestados, usuários ativos
- ✅ **Interface administrativa** - Painel de controle completo

## 🔧 Stack Tecnológico

### 🐍 Backend
- **Python 3.8+** - Linguagem principal
- **FastAPI** - Framework web moderno e performático
- **SQLAlchemy 2.0** - ORM avançado para banco de dados
- **Pydantic** - Validação de dados e serialização
- **Uvicorn** - Servidor ASGI de alta performance
- **JWT** - Autenticação baseada em tokens
- **Passlib** - Criptografia de senhas
- **Python-Jose** - Manipulação de tokens JWT

### 🎨 Frontend
- **HTML5** - Estrutura semântica
- **Bootstrap 5** - Framework CSS responsivo
- **JavaScript ES6+** - Interatividade moderna
- **Jinja2** - Engine de templates
- **Select2** - Componentes de seleção avançados
- **Bootstrap Icons** - Ícones vetoriais

### 🗄️ Banco de Dados
- **SQLite** - Desenvolvimento (arquivo local)
- **PostgreSQL/MySQL** - Produção (suporte nativo)

### 🛠️ Ferramentas de Desenvolvimento
- **Git** - Controle de versão
- **Pytest** - Testes automatizados
- **Alembic** - Migrações de banco de dados

## 🚀 API REST Endpoints

### 🔐 Autenticação
```http
POST   /api/v1/auth/login          # Login de usuário
POST   /api/v1/auth/register       # Registro de usuário
GET    /api/v1/auth/me             # Perfil do usuário logado
```

### 📖 Livros
```http
GET    /api/v1/livros/             # Listar livros (com filtros)
POST   /api/v1/livros/             # Criar novo livro
GET    /api/v1/livros/{id}         # Obter livro específico
PUT    /api/v1/livros/{id}         # Atualizar livro
DELETE /api/v1/livros/{id}         # Excluir livro
```

### 👥 Autores
```http
GET    /api/v1/autores/            # Listar autores
POST   /api/v1/autores/            # Criar novo autor (admin)
GET    /api/v1/autores/{id}        # Obter autor específico
PUT    /api/v1/autores/{id}        # Atualizar autor (admin)
DELETE /api/v1/autores/{id}        # Excluir autor (admin)
```

### 👤 Usuários
```http
GET    /api/v1/usuarios/           # Listar usuários (admin)
POST   /api/v1/usuarios/           # Criar usuário (admin)
GET    /api/v1/usuarios/{id}       # Obter usuário específico
PUT    /api/v1/usuarios/{id}       # Atualizar usuário
DELETE /api/v1/usuarios/{id}       # Excluir usuário (admin)
```

### 📋 Empréstimos
```http
GET    /api/v1/emprestimos/        # Listar empréstimos
POST   /api/v1/emprestimos/        # Criar empréstimo
GET    /api/v1/emprestimos/{id}    # Obter empréstimo específico
PUT    /api/v1/emprestimos/{id}/devolver  # Devolver livro
```

### 🏢 Editoras
```http
GET    /api/v1/editoras/           # Listar editoras
POST   /api/v1/editoras/           # Criar editora (admin)
PUT    /api/v1/editoras/{id}       # Atualizar editora (admin)
DELETE /api/v1/editoras/{id}       # Excluir editora (admin)
```

### 📝 Solicitações de Autores
```http
GET    /api/v1/solicitacoes-autores/     # Listar solicitações
POST   /api/v1/solicitacoes-autores/     # Criar solicitação
PUT    /api/v1/solicitacoes-autores/{id} # Aprovar/Rejeitar (admin)
```

## 🎯 Características Técnicas

### 🔒 Segurança
- **Autenticação JWT** com tokens seguros
- **Criptografia de senhas** com bcrypt
- **Validação de entrada** em todos os endpoints
- **Proteção CORS** configurada
- **Sanitização de dados** automática

### 📊 Performance
- **Consultas otimizadas** com SQLAlchemy
- **Paginação automática** em listagens
- **Cache de templates** Jinja2
- **Compressão de assets** estáticos
- **Lazy loading** de relacionamentos

### 🧪 Qualidade de Código
- **Arquitetura limpa** com separação de responsabilidades
- **Padrões REST** bem definidos
- **Documentação automática** com OpenAPI/Swagger
- **Validação de tipos** com Pydantic
- **Código limpo** sem dependências desnecessárias

## 📝 Licença

Este projeto foi desenvolvido como trabalho acadêmico para a **IMPACTA Tecnologia**.

## 👥 Contribuição

Este é um projeto acadêmico. Para sugestões ou melhorias:

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request