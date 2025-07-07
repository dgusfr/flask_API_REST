from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import jwt
import datetime
from functools import wraps
from schemas import GameSchema, LoginSchema
from marshmallow import ValidationError
import logging
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv
import os

# =================== Variáveis de ambiente ===================
load_dotenv()

# =================== Configuração da aplicação ===================
app = Flask(__name__)
CORS(app)

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
app.config["MAX_CONTENT_LENGTH"] = 1 * 1024 * 1024  # 1 MB
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")

db = SQLAlchemy(app)

# =================== Configuração dos logs ===================
handler = RotatingFileHandler("api.log", maxBytes=1_000_000, backupCount=3)
handler.setLevel(logging.INFO)
formatter = logging.Formatter(
    "%(asctime)s %(levelname)s %(message)s [%(pathname)s:%(lineno)d]"
)
handler.setFormatter(formatter)
app.logger.addHandler(handler)
app.logger.setLevel(logging.INFO)


# =================== Modelos ===================
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


# =================== JWT – middleware ===================
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"error": "Token não fornecido ou inválido"}), 401
        try:
            token = auth_header.split()[1]
            data = jwt.decode(
                token, app.config["SECRET_KEY"], algorithms=[JWT_ALGORITHM]
            )
            request.user_id = data["id"]
            request.user_email = data["email"]
        except Exception:
            return jsonify({"error": "Token inválido"}), 401
        return f(*args, **kwargs)

    return decorated


# =================== Schemas Marshmallow ===================
game_schema = GameSchema()
login_schema = LoginSchema()


# =================== Rotas públicas ===================
@app.route("/")
def home():
    return jsonify({"message": "Bem-vindo à API GameVerse (Flask + SQLAlchemy)!"}), 200


@app.route("/auth", methods=["POST"])
def login():
    json_data = request.get_json()
    validated = login_schema.load(json_data)

    user = User.query.filter_by(email=validated["email"]).first()
    if not user or user.password != validated["password"]:
        app.logger.warning(f"Tentativa de login falhou para {validated['email']}")
        return jsonify({"error": "Credenciais inválidas!"}), 401

    token = jwt.encode(
        {
            "id": user.id,
            "email": user.email,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=48),
        },
        app.config["SECRET_KEY"],
        algorithm=JWT_ALGORITHM,
    )

    app.logger.info(f"Login bem-sucedido para {user.email}")
    return jsonify({"token": token}), 200


# =================== Rotas protegidas ===================
@app.route("/games", methods=["GET"])
@token_required
def list_games():
    # ---------- paginação ----------
    try:
        page = max(1, int(request.args.get("page", 1)))
        per_page = int(request.args.get("per_page", 10))
    except ValueError:
        return jsonify({"error": "Parâmetros de paginação devem ser inteiros"}), 400
    per_page = max(1, min(per_page, 100))  # limite 1-100

    # ---------- filtros ----------
    title = request.args.get("title")
    year = request.args.get("year")
    min_price = request.args.get("min_price")
    max_price = request.args.get("max_price")

    query = Game.query
    if title:
        query = query.filter(Game.title.ilike(f"%{title}%"))
    if year:
        if not year.isdigit():
            return jsonify({"error": "Parâmetro year inválido"}), 400
        query = query.filter_by(year=int(year))
    if min_price:
        try:
            query = query.filter(Game.price >= float(min_price))
        except ValueError:
            return jsonify({"error": "Parâmetro min_price inválido"}), 400
    if max_price:
        try:
            query = query.filter(Game.price <= float(max_price))
        except ValueError:
            return jsonify({"error": "Parâmetro max_price inválido"}), 400

    total = query.count()
    games = query.offset((page - 1) * per_page).limit(per_page).all()

    games_data = [
        {"id": g.id, "title": g.title, "year": g.year, "price": g.price} for g in games
    ]
    total_pages = (total + per_page - 1) // per_page

    app.logger.info(
        f"Listagem de games por {request.user_email} | page={page} per_page={per_page} "
        f"filters: title={title} year={year} price={min_price}-{max_price}"
    )

    return (
        jsonify(
            {
                "page": page,
                "per_page": per_page,
                "total": total,
                "total_pages": total_pages,
                "data": games_data,
            }
        ),
        200,
    )


@app.route("/game/<int:game_id>", methods=["GET"])
@token_required
def get_game(game_id):
    game = Game.query.get(game_id)
    if not game:
        return jsonify({"error": "Jogo não encontrado"}), 404
    return (
        jsonify(
            {"id": game.id, "title": game.title, "year": game.year, "price": game.price}
        ),
        200,
    )


@app.route("/game", methods=["POST"])
@token_required
def create_game():
    json_data = request.get_json()
    validated = game_schema.load(json_data)

    new_game = Game(**validated)
    db.session.add(new_game)
    db.session.commit()

    app.logger.info(f"Jogo criado ({new_game.title}) por {request.user_email}")
    return jsonify({"message": "Jogo cadastrado com sucesso!", "id": new_game.id}), 201


@app.route("/game/<int:game_id>", methods=["PUT"])
@token_required
def update_game(game_id):
    game = Game.query.get(game_id)
    if not game:
        return jsonify({"error": "Jogo não encontrado"}), 404

    json_data = request.get_json()
    validated = game_schema.load(json_data)

    game.title = validated.get("title", game.title)
    game.year = validated.get("year", game.year)
    game.price = validated.get("price", game.price)
    db.session.commit()

    app.logger.info(f"Jogo {game_id} atualizado por {request.user_email}")
    return jsonify({"message": "Jogo atualizado com sucesso."}), 200


@app.route("/game/<int:game_id>", methods=["DELETE"])
@token_required
def delete_game(game_id):
    game = Game.query.get(game_id)
    if not game:
        return jsonify({"error": "Jogo não encontrado"}), 404
    db.session.delete(game)
    db.session.commit()

    app.logger.info(f"Jogo {game_id} deletado por {request.user_email}")
    return jsonify({"message": "Jogo excluído com sucesso."}), 200


# =================== handlers globais de erro ===================
@app.errorhandler(400)
def bad_request(e):
    return jsonify({"error": "Requisição inválida"}), 400


@app.errorhandler(401)
def unauthorized(e):
    return jsonify({"error": "Não autorizado"}), 401


@app.errorhandler(403)
def forbidden(e):
    return jsonify({"error": "Proibido"}), 403


@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Recurso não encontrado"}), 404


@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify({"error": "Método não permitido"}), 405


@app.errorhandler(413)
def too_large(e):
    return jsonify({"error": "Requisição muito grande. Limite = 1 MB"}), 413


@app.errorhandler(500)
def internal(e):
    app.logger.error(f"Erro interno: {e}")
    return jsonify({"error": "Erro interno do servidor"}), 500


@app.errorhandler(ValidationError)
def validation(e):
    return jsonify({"errors": e.messages}), 400


# =================== inicialização & seed ===================
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(email="diego@email.com").first():
            db.session.add(User(name="Diego", email="diego@email.com", password="1234"))
            db.session.commit()
    app.run(port=3000, debug=True)
