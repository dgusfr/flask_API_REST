# GameVerse API

API REST desenvolvida com Python + Flask para gerenciamento de jogos com autenticação JWT, validação robusta, paginação, filtros e arquitetura limpa.

---

## Sumário

- [Tecnologias Utilizadas](#tecnologias-utilizadas)
- [Status](#status)
- [Descrição](#descrição)
- [Funcionalidades](#funcionalidades)
- [Documentação](#documentacao)
- [Autor](#autor)

---

## Tecnologias Utilizadas

<div style="display: flex; justify-content: space-between; align-items: center; width: 100%;">
  <img src="images/python.png" alt="Logo Python" width="120"/>
</div>

---

## Status

![Em Desenvolvimento](http://img.shields.io/static/v1?label=STATUS&message=EM%20DESENVOLVIMENTO&color=RED&style=for-the-badge)

---

## Descrição

A GameVerse API permite gerenciar uma lista de jogos, com funcionalidades de login seguro usando JWT, controle de usuários e operações CRUD sobre os games cadastrados.

Além das operações básicas, conta com paginação, filtros, logs automáticos e proteção contra requisições maliciosas.

Ideal para uso em sistemas de catálogo de jogos, backend de e-commerces simples, protótipos ou estudos de API RESTful com boas práticas.

---

## Funcionalidades

- ✅ Autenticação com JWT (login seguro)
- ✅ Cadastro, edição, exclusão e consulta de games
- ✅ Validação de dados com Marshmallow
- ✅ Filtros por título, ano e preço
- ✅ Paginação com controle de página e limite de itens
- ✅ Logs automáticos com rotação
- ✅ Controle de erros e mensagens padronizadas
- ✅ Proteção contra payloads excessivos
- ✅ Configurações seguras via `.env`
- ✅ Pronto para deploy com Gunicorn + Nginx

---

## Documentação

### 🔐 POST `/auth`

Autentica o usuário e retorna um token JWT.

**Exemplo de request:**

```json
{
  "email": "diego@email.com",
  "password": "1234"
}
```

**Resposta:**

```json
{
  "token": "SEU_TOKEN_JWT"
}
```

---

### 📦 GET `/games`

Retorna lista de games com paginação e filtros.

**Parâmetros opcionais:**

- `page`, `per_page`
- `title`, `year`
- `min_price`, `max_price`

**Exemplo de uso:**

```
GET /games?page=1&per_page=5&title=mario&min_price=10
```

**Headers:**

```
Authorization: Bearer SEU_TOKEN
```

---

### 📦 POST `/game`

Cadastra novo game.

```json
{
  "title": "Minecraft",
  "year": 2012,
  "price": 99.90
}
```

---

### ✏️ PUT `/game/:id`

Atualiza um game existente.

```json
{
  "title": "Minecraft Edição Java",
  "price": 89.90
}
```

---

### 🗑️ DELETE `/game/:id`

Remove um game pelo ID.

---

## Autor

Desenvolvido por Diego Franco