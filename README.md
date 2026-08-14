# Bookstore — ViewSets e testes

Projeto desenvolvido por **Lucy Mazzini Lessa** para o curso de Backend Python da EBAC.

## Objetivo desta etapa

Construir as ViewSets a partir dos serializers do projeto Bookstore, disponibilizar as rotas da API e criar testes automatizados para validar o comportamento das operações CRUD.

## Implementação

- `CategoryViewSet` com `ModelViewSet`;
- `ProductViewSet` com `ModelViewSet`;
- `OrderViewSet` com `ModelViewSet`;
- ViewSets organizadas em pacotes próprios com exports nos arquivos `__init__.py`;
- `product/urls.py` com rotas de categorias e produtos;
- `order/urls.py` com rota de pedidos;
- inclusão das URLs dos apps no `bookstore/urls.py`;
- testes de criação, leitura, atualização e remoção;
- validação das rotas com Django REST Framework.

## Rotas

- `/api/categories/`
- `/api/products/`
- `/api/orders/`

Os detalhes de cada recurso são disponibilizados automaticamente pelos routers do DRF, por exemplo `/api/products/<id>/`.

## Testes

```bash
poetry install
poetry run pytest -q
```

Validação da branch `viewsets-tests`: **20 testes aprovados**.

## Estrutura das ViewSets

```text
product/
  viewsets/
    __init__.py
    category_viewset.py
    product_viewset.py

order/
  viewsets/
    __init__.py
    order_viewset.py
```

A branch `viewsets-tests` foi criada a partir de `serializers-tests`, pois esta atividade dá continuidade aos serializers construídos na etapa anterior.
