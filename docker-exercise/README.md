# EBAC — Docker Hello World

Exercício de introdução ao Docker.

## Objetivo

Criar uma imagem baseada em BusyBox, versionar e publicar no Docker Hub.

## Dockerfile

```dockerfile
FROM busybox:1.36.1

CMD ["echo", "Hello World - Lucy Mazzini Lessa | EBAC Docker"]
```

## Publicação

A publicação é feita integralmente pelo GitHub Actions, sem necessidade de instalar Docker localmente.

O workflow:

1. constrói a imagem;
2. executa e valida o Hello World;
3. autentica no Docker Hub usando GitHub Secrets;
4. publica as tags `v1.0.0` e `latest`;
5. faz logout e testa um pull anônimo para confirmar que a imagem está pública.

## Imagem final

`DOCKER_ID/ebac-hello-world:v1.0.0`

`DOCKER_ID/ebac-hello-world:latest`

Projeto desenvolvido por Lucy Mazzini Lessa para atividade da EBAC.
