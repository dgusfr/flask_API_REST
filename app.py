from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import jwt
import datetime
from functools import wraps
from schemas import GameSchema, LoginSchema
from marshmallow import ValidationError

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///gameverse.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'v3ry$3cur3&UnpredictableSecretKey!123'
app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024  # 1MB máximo para requisições
db = SQLAlchemy(app)
JWT_ALGORITHM = 'HS256'


# ======= Modelos =======
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

# ======= JWT Auth Middleware =======
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

# ======= Schemas Marshmallow =======
game_schema = GameSchema()
login_schema = LoginSchema()

# ======= Rotas =======
@app.route("/")
def home():
    return jsonify({"message": "Bem-vindo à API GameVerse (Flask + SQLAlchemy)!"}), 200

@app.route("/auth", methods=["POST"])
def login():
    json_data = request.get_json()
    validated_data = login_schema.load(json_data)

    user = User.query.filter_by(email=validated_data["email"]).first()
    if not user or user.password != validated_data["password"]:
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
    json_data = request.get_json()
    validated_data = game_schema.load(json_data)

    new_game = Game(**validated_data)
    db.session.add(new_game)
    db.session.commit()

    return jsonify({"message": "Jogo cadastrado com sucesso!", "id": new_game.id}), 201

@app.route("/game/<int:game_id>", methods=["PUT"])
@token_required
def update_game(game_id):
    game = Game.query.get(game_id)
    if not game:
        return jsonify({"error": "Jogo não encontrado"}), 404
    json_data = request.get_json()
    validated_data = game_schema.load(json_data)

    game.title = validated_data.get("title", game.title)
    game.year = validated_data.get("year", game.year)
    game.price = validated_data.get("price", game.price)
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

# ======= Tratamento Global de Erros =======
@app.errorhandler(400)
def bad_request(error):
    return jsonify({"error": "Requisição inválida"}), 400

@app.errorhandler(401)
def unauthorized(error):
    return jsonify({"error": "Não autorizado"}), 401

@app.errorhandler(403)
def forbidden(error):
    return jsonify({"error": "Proibido"}), 403

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Recurso não encontrado"}), 404

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({"error": "Método não permitido"}), 405

@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({"error": "Erro interno do servidor"}), 500

@app.errorhandler(ValidationError)
def handle_validation_error(error):
    return jsonify({"errors": error.messages}), 400

@app.errorhandler(413)
def request_entity_too_large(error):
    return jsonify({"error": "Requisição muito grande. Limite máximo é 1MB."}), 413


# ======= Inicialização do banco e execução =======
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(email="diego@email.com").first():
            user = User(name="Diego", email="diego@email.com", password="1234")
            db.session.add(user)
            db.session.commit()
    app.run(port=3000, debug=True)

