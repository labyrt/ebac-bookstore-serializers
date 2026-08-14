# Bookstore — Paginação e Django Debug Toolbar

Projeto desenvolvido por **Lucy Mazzini Lessa** para o curso de Backend Python da EBAC.

## Objetivo desta etapa

Dar continuidade ao projeto Bookstore da etapa de ViewSets, adicionando a paginação global do Django REST Framework e o Django Debug Toolbar para apoio ao desenvolvimento e análise das requisições locais.

## Paginação

A paginação foi configurada globalmente em `bookstore/settings.py` usando `PageNumberPagination`:

```python
REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 5,
}
```

Com isso, as listas de categorias, produtos e pedidos usam o formato paginado do DRF, com as propriedades `count`, `next`, `previous` e `results`.

Exemplos:

- `/api/products/`
- `/api/products/?page=2`
- `/api/categories/`
- `/api/orders/`

## Django Debug Toolbar

O pacote `django-debug-toolbar` foi adicionado como dependência de desenvolvimento pelo Poetry e configurado com:

- `debug_toolbar` em `INSTALLED_APPS`;
- `DebugToolbarMiddleware` em `MIDDLEWARE`;
- `127.0.0.1` em `INTERNAL_IPS`;
- rotas de depuração em `/__debug__/`.

A ferramenta é destinada ao ambiente local de desenvolvimento, com `DEBUG=True`.

## Executar o projeto

```bash
poetry install
poetry run python manage.py runserver
```

Depois, a API pode ser acessada em `http://127.0.0.1:8000/api/products/`.

## Testes e validação

```bash
poetry check
poetry run python manage.py check
poetry run pytest -q
```

Os testes desta etapa verificam a primeira e a segunda página da listagem de produtos e a configuração local do Django Debug Toolbar, além de preservar os testes das etapas anteriores.

## Continuidade do projeto

A branch `pagination-debug-toolbar` foi criada a partir de `viewsets-tests`, pois este exercício continua diretamente a implementação de ViewSets, URLs e testes realizada na etapa anterior.
