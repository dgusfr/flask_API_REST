# GameVerse API

GameVerse é uma API REST desenvolvida em **Python Flask**, com autenticação via JWT, que permite consultar e gerenciar uma lista fictícia de jogos.

## Tecnologias Utilizadas

- **Python 3**
- **Flask**
- **Flask-CORS**
- **PyJWT**

## Status

![Concluído](http://img.shields.io/static/v1?label=STATUS&message=CONCLUIDO&color=GREEN&style=for-the-badge)


## Descrição


A aplicação permite que usuários autenticados possam:

- Obter a lista de jogos
- Consultar detalhes de um jogo específico
- Adicionar novos jogos
- Atualizar informações de um jogo
- Excluir um jogo

A autenticação é feita através de um endpoint específico que gera um **token JWT** válido por 48 horas.

## Endpoints

### 🔑 POST /auth

Autentica o usuário e retorna o token JWT.

**Corpo da requisição:**

```json
{
  "email": "diego@email.com",
  "password": "1234"
}
```

**Resposta de sucesso (200):**

```json
{
  "token": "<token-jwt>"
}
```

---

### 📚 GET /games

Retorna a lista de todos os jogos.

**Headers:**

* `Authorization: Bearer <token>`

---

### 📚 GET /game/\:id

Retorna os dados de um jogo específico.

**Parâmetros:**

* `id` (número): ID do jogo.

**Headers:**

* `Authorization: Bearer <token>`

---

### ➕ POST /game

Adiciona um novo jogo.

**Headers:**

* `Authorization: Bearer <token>`

**Corpo:**

```json
{
  "title": "Novo jogo",
  "year": 2025,
  "price": 100
}
```

---

### ✏️ PUT /game/\:id

Atualiza informações de um jogo.

**Parâmetros:**

* `id` (número): ID do jogo.

**Headers:**

* `Authorization: Bearer <token>`

**Corpo (parcial ou completo):**

```json
{
  "title": "Jogo atualizado",
  "price": 80
}
```

---

### ❌ DELETE /game/\:id

Exclui um jogo.

**Parâmetros:**

* `id` (número): ID do jogo.

**Headers:**

* `Authorization: Bearer <token>`

---

## Autor

Desenvolvido por **Diego Franco**.
Entre em contato para sugestões ou melhorias! 🚀

---



