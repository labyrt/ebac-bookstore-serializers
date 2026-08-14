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
