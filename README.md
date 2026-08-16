# Bookstore — Token Authentication em pedidos

Projeto desenvolvido por **Lucy Mazzini Lessa** para o curso de Backend Python da EBAC.

## Objetivo desta etapa

Dar continuidade ao projeto Bookstore adicionando autenticação por token do Django REST Framework no `OrderViewSet`, mantendo o catálogo de produtos aberto para consulta pública.

## Autenticação

O app `rest_framework.authtoken` foi adicionado ao `INSTALLED_APPS` para habilitar os tokens do DRF.

O `OrderViewSet` utiliza:

```python
authentication_classes = [TokenAuthentication]
permission_classes = [IsAuthenticated]
```

Além disso, o queryset de pedidos é filtrado pelo usuário autenticado. Dessa forma, cada usuário acessa somente os próprios pedidos.

O usuário autenticado também é mantido como dono do pedido durante criação e atualização.

## Produtos permanecem públicos

O `ProductViewSet` continua aberto, usando `AllowAny`, para que a listagem e os detalhes dos produtos possam ser consultados sem autenticação.

## Como usar o token

Depois de aplicar as migrações, um token pode ser criado para um usuário usando as ferramentas do DRF, por exemplo no shell:

```python
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token

user = get_user_model().objects.get(username="usuario")
token, _ = Token.objects.get_or_create(user=user)
print(token.key)
```

Nas requisições protegidas, o cabeçalho segue o formato:

```text
Authorization: Token <seu-token>
```

## Executar o projeto

```bash
poetry install
poetry run python manage.py migrate
poetry run python manage.py runserver
```

Rotas principais:

- `/api/products/` — pública;
- `/api/categories/` — permanece conforme a etapa anterior;
- `/api/orders/` — exige Token Authentication.

## Testes

```bash
poetry check
poetry run python manage.py check
poetry run python manage.py migrate --noinput
poetry run pytest -q
```

Os testes desta etapa verificam:

- acesso a pedidos sem token retorna `401`;
- operações CRUD de pedido funcionam com token válido;
- um usuário lista somente os próprios pedidos;
- um usuário não consegue acessar pedido de outro usuário;
- o catálogo de produtos continua acessível sem autenticação;
- testes das etapas anteriores continuam funcionando.

## Continuidade do projeto

A branch `token-authentication-orders` foi criada a partir de `pagination-debug-toolbar`, pois esta atividade continua diretamente o projeto desenvolvido nas etapas anteriores.

---

## Módulo 19 — Docker

Nesta etapa o Bookstore passa a ser executável dentro de um container Docker, conforme solicitado no exercício do Módulo 19.

### Construir a imagem

```bash
docker build -t bookstore-ebac:module19 .
```

### Executar o projeto no container

```bash
docker run --rm -p 8000:8000 bookstore-ebac:module19
```

A aplicação fica disponível em `http://127.0.0.1:8000/`.

### Dockerfile

O container utiliza Python 3.12, compatível com a versão declarada no `pyproject.toml`, instala as dependências com Poetry e expõe a porta `8000`.

Como medida de segurança, o processo da aplicação roda com um usuário sem privilégios de root. O arquivo `.dockerignore` também evita o envio de arquivos locais, caches, banco SQLite de desenvolvimento e arquivos `.env` para o contexto de build.

### Validação automática

O workflow `Docker - Exercício Módulo 19` executa o exercício integralmente em um runner do GitHub Actions:

1. constrói a imagem Docker;
2. executa `python manage.py check` dentro da imagem;
3. executa a suíte Pytest dentro da imagem;
4. confirma que o processo não roda como root;
5. inicia o container usando o `CMD` do Dockerfile;
6. verifica por HTTP que o servidor Django responde na porta 8000.

Assim, a execução do Docker é comprovada sem depender da instalação do Docker Desktop na máquina local.

### Branch da atividade

`dockerize-bookstore-module19`

---

## Módulo 20 — Docker Compose + PostgreSQL

Nesta etapa o Bookstore deixa de depender apenas do banco SQLite local quando executado em containers e passa a utilizar PostgreSQL através do Docker Compose.

### Arquitetura

O `compose.yaml` possui dois serviços:

- `web`: aplicação Django REST Framework construída pelo `Dockerfile` do Módulo 19;
- `db`: PostgreSQL 17 com volume persistente e healthcheck.

O serviço `web` só inicia depois que o PostgreSQL é considerado saudável pelo Compose.

### Variáveis de ambiente

As credenciais do banco não são versionadas. Crie o arquivo `.env` a partir do exemplo:

```bash
cp .env.example .env
```

No Windows, você também pode copiar `.env.example` para `.env` pelo Explorador de Arquivos e alterar a senha local.

### Subir a aplicação completa

```bash
docker compose up --build
```

A API fica disponível em:

```text
http://127.0.0.1:8000/api/products/
```

Para encerrar:

```bash
docker compose down
```

Para encerrar e apagar também o volume de desenvolvimento do PostgreSQL:

```bash
docker compose down -v
```

### Banco de dados

O Django lê `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_HOST` e `POSTGRES_PORT` do ambiente. Quando `POSTGRES_HOST` está presente, o backend utilizado é `django.db.backends.postgresql`.

O projeto utiliza Psycopg 3 como driver PostgreSQL. Fora do Compose, se as variáveis de PostgreSQL não existirem, o SQLite continua disponível para desenvolvimento local e compatibilidade com as etapas anteriores.

### Validação automática

O workflow `Docker Compose + PostgreSQL - Módulo 20` valida em um ambiente efêmero:

1. sintaxe do Compose;
2. build da aplicação;
3. inicialização do PostgreSQL;
4. healthcheck e ordem correta de inicialização;
5. conexão real do Django com PostgreSQL;
6. `manage.py check`;
7. suíte Pytest completa usando PostgreSQL;
8. resposta HTTP real de `/api/products/`;
9. encerramento e remoção dos containers/volume de CI.

### Branch da atividade

`docker-compose-postgres-module20`
