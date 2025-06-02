from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import jwt
import datetime
from functools import wraps

# ========== Configuração da aplicação ==========
app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///gameverse.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'v3ry$3cur3&UnpredictableSecretKey!123'
db = SQLAlchemy(app)
JWT_ALGORITHM = 'HS256'

# ========== Modelos ==========
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)

# ========== Inicializa o banco e cria usuário padrão ==========
@app.before_first_request
def create_tables():
    db.create_all()
    # Usuário padrão, inserido apenas se não existir
    if not User.query.filter_by(email="diego@email.com").first():
        user = User(name="Diego", email="diego@email.com", password="1234")
        db.session.add(user)
        db.session.commit()

# ========== Middleware de autenticação JWT ==========
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"error": "Token não fornecido ou inválido"}), 401
        try:
            token = auth_header.split()[1]
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=[JWT_ALGORITHM])
            request.user_id = data['id']
            request.user_email = data['email']
        except Exception:
            return jsonify({"error": "Token inválido"}), 401
        return f(*args, **kwargs)
    return decorated

# ========== Rotas ==========
@app.route("/")
def home():
    return jsonify({"message": "Bem-vindo à API GameVerse (Flask + SQLAlchemy)!"}), 200

@app.route("/auth", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    user = User.query.filter_by(email=email).first()
    if not user or user.password != password:
        return jsonify({"error": "Credenciais inválidas!"}), 401
    token = jwt.encode({
        "id": user.id,
        "email": user.email,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=48)
    }, app.config['SECRET_KEY'], algorithm=JWT_ALGORITHM)
    return jsonify({"token": token}), 200

@app.route("/games", methods=["GET"])
@token_required
def list_games():
    games = Game.query.all()
    games_list = [
        {"id": game.id, "title": game.title, "year": game.year, "price": game.price}
        for game in games
    ]
    return jsonify(games_list), 200

@app.route("/game/<int:game_id>", methods=["GET"])
@token_required
def get_game(game_id):
    game = Game.query.get(game_id)
    if not game:
        return jsonify({"error": "Jogo não encontrado"}), 404
    return jsonify({"id": game.id, "title": game.title, "year": game.year, "price": game.price}), 200

@app.route("/game", methods=["POST"])
@token_required
def create_game():
    data = request.get_json()
    title = data.get("title")
    year = data.get("year")
    price = data.get("price")
    if not title or not year or not price:
        return jsonify({"error": "Campos obrigatórios: title, year, price"}), 400
    new_game = Game(title=title, year=year, price=price)
    db.session.add(new_game)
    db.session.commit()
    return jsonify({"message": "Jogo cadastrado com sucesso!", "id": new_game.id}), 201

@app.route("/game/<int:game_id>", methods=["PUT"])
@token_required
def update_game(game_id):
    game = Game.query.get(game_id)
    if not game:
        return jsonify({"error": "Jogo não encontrado"}), 404
    data = request.get_json()
    game.title = data.get("title", game.title)
    game.year = data.get("year", game.year)
    game.price = data.get("price", game.price)
    db.session.commit()
    return jsonify({"message": "Jogo atualizado com sucesso."}), 200

@app.route("/game/<int:game_id>", methods=["DELETE"])
@token_required
def delete_game(game_id):
    game = Game.query.get(game_id)
    if not game:
        return jsonify({"error": "Jogo não encontrado"}), 404
    db.session.delete(game)
    db.session.commit()
    return jsonify({"message": "Jogo excluído com sucesso."}), 200

# ========== Execução ==========
if __name__ == "__main__":
    app.run(port=3000, debug=True)
