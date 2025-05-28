from flask import Flask, jsonify, request
from flask_cors import CORS
import jwt
import datetime
from functools import wraps

app = Flask(__name__)
CORS(app)

# Chave secreta para o JWT
JWT_SECRET = "v3ry$3cur3&UnpredictableSecretKey!123"
JWT_ALGORITHM = "HS256"

# Banco de dados fictício
dataBase = {
    "games": {
        1: {"title": "Call of Duty MW", "year": 2019, "price": 60},
        2: {"title": "Sea of Thieves", "year": 2018, "price": 40},
        3: {"title": "Minecraft", "year": 2012, "price": 20},
    },
    "users": {
        1: {"id": 1, "name": "Diego", "email": "diego@email.com", "password": "1234"}
    }
}

# Middleware de autenticação
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return jsonify({"error": "Token inválido!"}), 401

        try:
            token = auth_header.split(" ")[1]
            data = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            request.user = {"id": data["id"], "email": data["email"]}
        except Exception:
            return jsonify({"error": "Token inválido!"}), 401

        return f(*args, **kwargs)
    return decorated

# Rotas
@app.route("/games", methods=["GET"])
@token_required
def get_games():
    games = [
        {"id": id, **game}
        for id, game in dataBase["games"].items()
    ]
    return jsonify(games), 200

@app.route("/game/<int:id>", methods=["GET"])
@token_required
def get_game(id):
    game = dataBase["games"].get(id)
    if not game:
        return "", 404
    return jsonify({"id": id, **game}), 200

@app.route("/game", methods=["POST"])
@token_required
def add_game():
    data = request.json
    title, year, price = data.get("title"), data.get("year"), data.get("price")
    if not title or not year or not price:
        return jsonify({"error": "Dados incompletos!"}), 400

    new_id = max(dataBase["games"].keys()) + 1
    dataBase["games"][new_id] = {"title": title, "year": year, "price": price}
    return "", 201

@app.route("/game/<int:id>", methods=["DELETE"])
@token_required
def delete_game(id):
    if id not in dataBase["games"]:
        return "", 404
    del dataBase["games"][id]
    return "", 200

@app.route("/game/<int:id>", methods=["PUT"])
@token_required
def update_game(id):
    game = dataBase["games"].get(id)
    if not game:
        return "", 404

    data = request.json
    game["title"] = data.get("title", game["title"])
    game["year"] = data.get("year", game["year"])
    game["price"] = data.get("price", game["price"])
    return "", 200

@app.route("/auth", methods=["POST"])
def auth():
    data = request.json
    email, password = data.get("email"), data.get("password")

    user = next((u for u in dataBase["users"].values() if u["email"] == email), None)
    if not user or user["password"] != password:
        return jsonify({"error": "Credenciais inválidas!"}), 401

    payload = {
        "id": user["id"],
        "email": user["email"],
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=48)
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return jsonify({"token": token}), 200

# Inicialização
if __name__ == "__main__":
    app.run(port=3000, debug=True)
