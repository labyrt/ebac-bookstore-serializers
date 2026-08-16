# Módulo 23 — Projeto Final: PythonAnywhere e Continuous Delivery

Este documento acompanha a etapa final do Bookstore da EBAC. O material atualizado do módulo usa o PythonAnywhere para disponibilizar a API e, em seguida, automatiza o deploy a partir do GitHub.

## 1. Preparação do projeto

A branch desta etapa é `feat-pythonanywhere`.

O projeto já utiliza Python 3.12 e Psycopg 3. Para preservar a compatibilidade das etapas anteriores, a implementação mantém essas versões e adiciona `GitPython`, necessário para a automação de atualização do repositório.

Validações executadas no GitHub Actions:

```bash
poetry check --lock
poetry install --no-interaction
poetry run python manage.py check
poetry run python manage.py makemigrations --check --dry-run
poetry run pytest -q
```

## 2. Criar o ambiente no PythonAnywhere

1. Crie a conta no PythonAnywhere.
2. Abra um console Bash.
3. Clone o repositório após a integração desta etapa na `main`:

```bash
git clone https://github.com/labyrt/ebac-bookstore-serializers.git
cd ebac-bookstore-serializers
```

4. Crie um ambiente virtual usando a mesma versão de Python escolhida na configuração do Web App. Para este projeto, use Python 3.12 se essa versão estiver disponível no sistema da sua conta:

```bash
python3.12 -m venv ~/bookstore-venv
source ~/bookstore-venv/bin/activate
```

5. Instale o Poetry e as dependências:

```bash
pip install poetry
poetry install --without dev --no-interaction
```

6. Aplique as migrações e colete os arquivos estáticos:

```bash
poetry run python manage.py migrate --noinput
poetry run python manage.py collectstatic --noinput
```

## 3. Criar o Web App

Na aba **Web** do PythonAnywhere:

1. clique em **Add a new web app**;
2. escolha **Manual configuration**;
3. selecione a mesma versão de Python usada pelo virtualenv;
4. em **Source code**, informe a pasta do repositório, por exemplo:
   `/home/SEU_USUARIO/ebac-bookstore-serializers`;
5. em **Virtualenv**, informe:
   `/home/SEU_USUARIO/bookstore-venv`.

## 4. Variáveis de produção

Não coloque chaves reais no GitHub. Configure os valores apenas no ambiente do PythonAnywhere/WSGI:

```text
DJANGO_SECRET_KEY=<uma-chave-forte-e-privada>
DJANGO_DEBUG=false
DJANGO_ALLOWED_HOSTS=SEU_USUARIO.pythonanywhere.com
DJANGO_CSRF_TRUSTED_ORIGINS=https://SEU_USUARIO.pythonanywhere.com
```

O projeto usa SQLite quando as variáveis `POSTGRES_*` não são fornecidas. Assim, a etapa gratuita do PythonAnywhere pode ser validada sem expor credenciais de banco.

## 5. WSGI

No arquivo WSGI indicado pela aba **Web**, ajuste o caminho para o diretório que contém `manage.py` e carregue o projeto Django:

```python
import os
import sys

path = "/home/SEU_USUARIO/ebac-bookstore-serializers"
if path not in sys.path:
    sys.path.insert(0, path)

os.environ["DJANGO_SETTINGS_MODULE"] = "bookstore.settings"
os.environ["DJANGO_DEBUG"] = "false"
os.environ["DJANGO_ALLOWED_HOSTS"] = "SEU_USUARIO.pythonanywhere.com"
os.environ["DJANGO_CSRF_TRUSTED_ORIGINS"] = "https://SEU_USUARIO.pythonanywhere.com"
# Configure DJANGO_SECRET_KEY aqui ou por outro mecanismo privado do servidor.

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
```

Depois, salve e clique em **Reload** na aba Web.

## 6. Resultado esperado

A API deve ficar disponível em:

```text
https://SEU_USUARIO.pythonanywhere.com/api/products/
```

A próxima branch do exercício, `feat-automate-deploy`, adiciona o endpoint protegido de webhook, a página de verificação e o reload automático após um push na `main`.
