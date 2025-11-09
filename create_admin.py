#!/usr/bin/env python3
"""
create_admin.py

Script simples para criar ou atualizar um usuário com privilégio de admin
no banco de dados SQLite usado por este projeto.

Exemplo de uso:
  python create_admin.py --email admin2@impacta.edu.br --password 'SenhaForte123!' --nome "Admin Novo" --matricula ADMIN002

Observação: este script espera ser executado a partir da raiz do projeto (onde está o arquivo `main.py`).
"""

import argparse
import getpass
from app.core.database import SessionLocal, engine, Base
from app.core.auth import get_password_hash
from app.models.models import UsuarioAuth


def parse_args():
    parser = argparse.ArgumentParser(description="Criar/atualizar usuário admin no banco da aplicação")
    parser.add_argument("--email", required=False, default=None, help="Email do usuário admin")
    parser.add_argument("--password", required=False, default=None, help="Senha do usuário admin")
    parser.add_argument("--nome", required=False, default=None, help="Nome do usuário")
    parser.add_argument("--matricula", required=False, default=None, help="Matrícula/identificador do usuário (opcional). Se omitida, será gerada automaticamente")
    return parser.parse_args()


def main():
    args = parse_args()

    # Garante que as tabelas existem
    Base.metadata.create_all(bind=engine)

    # Open DB session early so we can generate matricula if needed
    db = SessionLocal()
    try:
        # Interactive prompts (use defaults when user presses Enter)
        def prompt_with_default(text, default=None):
            if default:
                resp = input(f"{text} [{default}]: ")
                return resp.strip() or default
            else:
                resp = input(f"{text}: ")
                return resp.strip()

        default_email = "admin2@impacta.edu.br"
        default_password = "Admin@123"
        default_nome = "Administrador Novo"

        # Email
        email_val = args.email or prompt_with_default("Email do admin", default_email)

        # Password (hidden). If empty, use default_password
        if args.password:
            password_val = args.password
        else:
            pw = getpass.getpass("Senha do admin (pressione Enter para usar padrão): ")
            password_val = pw if pw else default_password

        # Nome
        nome_val = args.nome or prompt_with_default("Nome do admin", default_nome)

        # Now we can check existing by email
        existing = db.query(UsuarioAuth).filter(UsuarioAuth.email == email_val).first()

        # Helper to generate a unique ADMIN matricula like ADMIN001, ADMIN002, ...
        def generate_admin_matricula():
            # Fetch existing matriculas that start with ADMIN
            rows = db.query(UsuarioAuth.matricula).filter(UsuarioAuth.matricula.ilike('ADMIN%')).all()
            nums = []
            for (m,) in rows:
                if not m:
                    continue
                # extract trailing digits
                import re
                match = re.search(r"(\d+)$", m)
                if match:
                    nums.append(int(match.group(1)))
            next_num = 1
            if nums:
                next_num = max(nums) + 1
            return f"ADMIN{next_num:03d}"

        matricula_to_use = args.matricula
        if not matricula_to_use:
            generated = generate_admin_matricula()
            matricula_to_use = prompt_with_default("Matrícula (pressione Enter para usar gerada)", generated)
        if existing:
            # Atualiza campos essenciais e garante admin
            existing.nome = nome_val or existing.nome
            # Se o registro existente não tiver matrícula, preenche com a gerada
            if not existing.matricula:
                existing.matricula = matricula_to_use
            if password_val:
                existing.senha_hash = get_password_hash(password_val)
            existing.is_admin = True
            db.add(existing)
            action = "atualizado"
        else:
            novo = UsuarioAuth(
                matricula=matricula_to_use,
                nome=nome_val,
                email=email_val,
                senha_hash=get_password_hash(password_val),
                is_admin=True,
            )
            db.add(novo)
            action = "criado"

        db.commit()

        print(f"Usuário admin {action} com sucesso:")
        print(f"  email: {email_val}")
        print(f"  senha: {password_val}")
        print(f"  matricula: {matricula_to_use}")
        print("OBS: altere a senha imediatamente após o primeiro login e mantenha-a segura.")

    except Exception as e:
        db.rollback()
        print("Erro ao criar/atualizar usuário:", e)
    finally:
        db.close()


if __name__ == '__main__':
    main()
