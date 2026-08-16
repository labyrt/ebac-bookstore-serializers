# Módulo 23 — Projeto Final: PythonAnywhere e Continuous Delivery

Este documento acompanha a etapa final do Bookstore da EBAC. O material atualizado do módulo usa o PythonAnywhere para disponibilizar a API e, em seguida, automatiza o deploy a partir do GitHub.

## 1. Preparação do projeto

A primeira branch desta etapa é `feat-pythonanywhere`.

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
3. Clone a `main` do repositório:

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

Não coloque chaves reais no GitHub. Configure estes valores apenas no ambiente do PythonAnywhere/WSGI:

```text
DJANGO_SECRET_KEY=<uma-chave-forte-e-privada>
DJANGO_DEBUG=false
DJANGO_ALLOWED_HOSTS=SEU_USUARIO.pythonanywhere.com
DJANGO_CSRF_TRUSTED_ORIGINS=https://SEU_USUARIO.pythonanywhere.com
GITHUB_WEBHOOK_SECRET=<outro-segredo-aleatorio-forte>
PYTHONANYWHERE_USERNAME=SEU_USUARIO
DEPLOY_REPOSITORY_PATH=/home/SEU_USUARIO/ebac-bookstore-serializers
```

O projeto usa SQLite quando as variáveis `POSTGRES_*` não são fornecidas. Assim, a etapa gratuita do PythonAnywhere pode ser validada sem expor credenciais de banco.

## 5. WSGI

No arquivo WSGI indicado pela aba **Web**, ajuste o caminho para o diretório que contém `manage.py` e carregue o projeto Django. Os segredos abaixo são exemplos de nomes de variáveis; use valores privados no servidor:

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
os.environ["PYTHONANYWHERE_USERNAME"] = "SEU_USUARIO"
os.environ["DEPLOY_REPOSITORY_PATH"] = path
# Configure DJANGO_SECRET_KEY e GITHUB_WEBHOOK_SECRET com valores privados.

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
```

Depois, salve e clique em **Reload** na aba Web.

## 6. Validar a publicação

A API deve ficar disponível em:

```text
https://SEU_USUARIO.pythonanywhere.com/api/products/
```

A página pedida na etapa de automação fica em:

```text
https://SEU_USUARIO.pythonanywhere.com/hello/
```

Ela deve exibir **Hello World!** e um link para a API.

## 7. Continuous Delivery com webhook

A segunda branch do exercício é `feat-automate-deploy`. Ela adiciona:

- `bookstore/views.py`;
- rota `POST /update_server/`;
- rota `GET /hello/`;
- template `bookstore/templates/hello_world.html`;
- testes automatizados do webhook.

No GitHub, abra **Settings → Webhooks → Add webhook** e configure:

```text
Payload URL: https://SEU_USUARIO.pythonanywhere.com/update_server/
Content type: application/json
Secret: o mesmo valor de GITHUB_WEBHOOK_SECRET configurado no servidor
Events: Just the push event
Active: marcado
```

O endpoint também responde corretamente ao evento `ping` usado pelo GitHub para validar o cadastro.

## 8. Proteções do deploy

O webhook não executa um `git pull` para qualquer requisição recebida. Ele:

1. verifica `X-Hub-Signature-256` com HMAC-SHA256;
2. aceita somente eventos GitHub autenticados;
3. ignora eventos diferentes de `push`;
4. ignora pushes de branches diferentes da `main`;
5. recusa atualizar se houver modificações locais rastreadas no servidor;
6. busca a `main` no `origin` e aceita somente atualização `fast-forward`;
7. toca o arquivo WSGI do PythonAnywhere para recarregar a aplicação.

O caminho padrão do WSGI é derivado de `PYTHONANYWHERE_USERNAME`. Se a conta usar uma configuração diferente, informe explicitamente:

```text
PYTHONANYWHERE_WSGI_FILE=/var/www/SEU_ARQUIVO_wsgi.py
```

## 9. Fluxo final

Depois de configurado, o fluxo esperado é:

```text
alteração de código
→ Pull Request
→ workflow Build - Projeto Final M23
→ merge na main
→ webhook do GitHub
→ atualização fast-forward no PythonAnywhere
→ reload do WSGI
→ aplicação atualizada
```

Esse é o ciclo de Continuous Integration + Continuous Delivery demonstrado no projeto final.
